import { PRODUCTS, priceCart, formatShekels } from "../public/catalog.js";
import {
  json, html, redirect, nowIso, randomToken, newOrderId, sha256Hex, hmacHex, safeEqual,
  readJson, HttpError, escapeHtml,
} from "./util.js";
import {
  getOrder, getOrderByIdempotencyKey, insertOrder, setPaymentUrl, setStatusIfAwaiting,
  recordEvent, setEventOutcome, applyConfirmedPayment, markNeedsReview, publicOrderView,
} from "./orders.js";
import * as morning from "./payments/morning.js";

// PAYMENT_MODE:
//   mock             — default. Local test page, no provider is contacted, nothing is charged.
//   morning_sandbox  — Morning sandbox credentials. For verifying the integration.
//   morning_live     — real charges. Also requires ALLOW_LIVE_PAYMENTS = "yes".
function paymentMode(env) {
  const mode = env.PAYMENT_MODE || "mock";
  if (!["mock", "morning_sandbox", "morning_live"].includes(mode)) throw new HttpError(500, "bad_payment_mode");
  if (mode === "morning_live" && env.ALLOW_LIVE_PAYMENTS !== "yes") throw new HttpError(503, "live_payments_not_allowed");
  return mode;
}

function baseUrl(env, request) {
  return (env.PUBLIC_BASE_URL || new URL(request.url).origin).replace(/\/$/, "");
}

const ID_RE = /^OY-[23456789A-HJ-NP-Z]{8}$/;
const TOKEN_RE = /^[0-9a-f]{48}$/;
const IDEMPOTENCY_RE = /^[A-Za-z0-9_-]{16,64}$/;

function validateCustomer(raw) {
  if (!raw || typeof raw !== "object") return null;
  const name = typeof raw.name === "string" ? raw.name.trim().replace(/\s+/g, " ") : "";
  const email = typeof raw.email === "string" ? raw.email.trim() : "";
  const phone = typeof raw.phone === "string" ? raw.phone.trim() : "";
  const errors = {};
  if (name.length < 2 || name.length > 80) errors.name = "invalid";
  if (email.length > 120 || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) errors.email = "invalid";
  const digits = phone.replace(/\D/g, "");
  if (!/^[0-9+\-\s()]{9,20}$/.test(phone) || digits.length < 9 || digits.length > 15) errors.phone = "invalid";
  return Object.keys(errors).length ? { errors } : { customer: { name, email, phone } };
}

async function loadAuthorizedOrder(env, orderId, token) {
  if (!ID_RE.test(orderId || "") || !TOKEN_RE.test(token || "")) return null;
  const order = await getOrder(env.DB, orderId);
  if (!order || !safeEqual(order.access_token, token)) return null;
  return order;
}

function checkoutResponse(order, mode) {
  if (order.status === "awaiting_payment" && !order.provider_payment_url) {
    // Another request with the same key is still creating the payment page.
    return json({ state: "pending", orderId: order.id }, 202);
  }
  return json({
    state: order.status === "awaiting_payment" ? "redirect" : order.status,
    orderId: order.id,
    token: order.access_token,
    paymentUrl: order.status === "awaiting_payment" ? order.provider_payment_url : null,
    paymentMode: mode,
  });
}

// Server-side round window. Unset ROUND_OPENS_AT = no restriction (dates not decided yet).
function roundState(env, now = Date.now()) {
  if (!env.ROUND_OPENS_AT) return "open";
  const start = Date.parse(env.ROUND_OPENS_AT);
  if (Number.isNaN(start)) throw new HttpError(500, "bad_round_date");
  if (now < start) return "not_open";
  if (now >= start + 14 * 86400000) return "closed";
  return "open";
}

async function handleCheckout(request, env) {
  const mode = paymentMode(env);
  const round = roundState(env);
  if (round === "not_open") return json({ error: "round_not_open" }, 403);
  if (round === "closed") return json({ error: "round_closed" }, 403);
  const body = await readJson(request);

  if (!IDEMPOTENCY_RE.test(body.idempotencyKey || "")) throw new HttpError(400, "invalid_idempotency_key");
  const priced = priceCart(body.items);
  if (!priced.ok) return json({ error: priced.error }, 400);
  const c = validateCustomer(body.customer);
  if (c.errors) return json({ error: "invalid_customer", fields: c.errors }, 400);

  // Fingerprint of what was actually ordered — prices are deliberately not part of the input.
  const fingerprint = await sha256Hex(
    JSON.stringify({ lines: priced.lines.map((l) => [l.productId, l.quantity]), customer: c.customer }),
  );

  const existing = await getOrderByIdempotencyKey(env.DB, body.idempotencyKey);
  if (existing) {
    if (existing.request_fingerprint !== fingerprint) return json({ error: "idempotency_conflict" }, 409);
    return checkoutResponse(existing, mode);
  }

  const order = {
    id: newOrderId(),
    accessToken: randomToken(),
    idempotencyKey: body.idempotencyKey,
    fingerprint,
    paymentMode: mode,
    currency: priced.currency,
    totalAgorot: priced.totalAgorot,
    customer: c.customer,
    lines: priced.lines,
  };
  try {
    await insertOrder(env.DB, order, priced.lines);
  } catch (err) {
    // Lost a race against a concurrent request carrying the same idempotency key.
    const raced = await getOrderByIdempotencyKey(env.DB, body.idempotencyKey);
    if (raced) {
      if (raced.request_fingerprint !== fingerprint) return json({ error: "idempotency_conflict" }, 409);
      return checkoutResponse(raced, mode);
    }
    throw err;
  }

  const base = baseUrl(env, request);
  const q = `order=${order.id}&t=${order.accessToken}`;
  let paymentUrl;
  try {
    if (mode === "mock") {
      paymentUrl = `${base}/pay/mock?${q}`;
    } else {
      const sig = await hmacHex(env.NOTIFY_SIGNING_SECRET, order.id);
      ({ paymentUrl } = await morning.createPaymentPage(env, order, {
        successUrl: `${base}/pay/return?${q}&result=success`,
        failureUrl: `${base}/pay/return?${q}&result=failure`,
        notifyUrl: `${base}/api/morning/notify?order=${order.id}&sig=${sig}`,
      }));
    }
  } catch (err) {
    console.error("payment page creation failed", order.id, err.message);
    await setStatusIfAwaiting(env.DB, order.id, "failed_to_start", String(err.message).slice(0, 300));
    return json({ error: "payment_unavailable", orderId: order.id }, 502);
  }
  await setPaymentUrl(env.DB, order.id, paymentUrl);
  return json({ state: "redirect", orderId: order.id, token: order.accessToken, paymentUrl, paymentMode: mode });
}

async function handleOrderStatus(url, env, orderId) {
  const order = await loadAuthorizedOrder(env, orderId, url.searchParams.get("t"));
  if (!order) return json({ error: "not_found" }, 404);
  return json(publicOrderView(order));
}

// Where the customer lands after the hosted payment page. This is navigation only:
// it never marks an order as paid. A failure/cancel return closes an unpaid order.
async function handleReturn(url, env) {
  const orderId = url.searchParams.get("order");
  const token = url.searchParams.get("t");
  const order = await loadAuthorizedOrder(env, orderId, token);
  if (!order) return redirect("/order?error=not_found");
  if (url.searchParams.get("result") === "failure") {
    await setStatusIfAwaiting(env.DB, order.id, "cancelled", "customer_returned_via_failure_url");
  }
  return redirect(`/order?order=${order.id}&t=${token}`);
}

// Notification endpoint given to Morning as notifyUrl for each order.
// 1. The URL carries an HMAC of the order id that only this server can produce.
// 2. Each distinct notification body is stored once (payment_events.event_key is unique).
// 3. The order is marked paid only after the document is read back from Morning's API.
async function handleMorningNotify(request, url, env) {
  const mode = paymentMode(env);
  if (mode === "mock") return json({ error: "not_enabled" }, 404);

  const orderId = url.searchParams.get("order") || "";
  const sig = url.searchParams.get("sig") || "";
  if (!ID_RE.test(orderId) || !safeEqual(sig, await hmacHex(env.NOTIFY_SIGNING_SECRET, orderId))) {
    return json({ error: "forbidden" }, 403);
  }
  const raw = await request.text();
  if (raw.length > 64 * 1024) return json({ error: "payload_too_large" }, 413);

  const eventKey = `morning:${orderId}:${await sha256Hex(raw)}`;
  const isNew = await recordEvent(env.DB, { provider: "morning", eventKey, orderId, payload: raw });
  if (!isNew) return json({ ok: true, duplicate: true });

  let payload = null;
  try {
    payload = JSON.parse(raw);
  } catch {
    payload = Object.fromEntries(new URLSearchParams(raw));
  }

  let outcome;
  try {
    const result = await morning.confirmPayment(env, orderId, payload);
    if (result.confirmed) {
      outcome = await applyConfirmedPayment(env.DB, orderId, result);
    } else {
      await markNeedsReview(env.DB, orderId, `notify_unconfirmed: ${result.reason}`);
      outcome = `needs_review:${result.reason}`;
    }
  } catch (err) {
    // Leave the event recorded and the order for manual reconciliation. Reply 200 so the
    // provider does not keep retrying an event we already hold.
    console.error("notify processing failed", orderId, err.message);
    await markNeedsReview(env.DB, orderId, `notify_error: ${String(err.message).slice(0, 200)}`);
    outcome = "error";
  }
  await setEventOutcome(env.DB, eventKey, outcome);
  return json({ ok: true });
}

// ---------------------------------------------------------------------------------------------
// Mock provider (PAYMENT_MODE=mock only). Stands in for the hosted payment page so the full
// flow — redirect, success, failure, cancel, duplicate notification — can be exercised locally.

function mockPage(order, token) {
  const rows = order.items
    .map(
      (i) =>
        `<tr><td>${escapeHtml(i.name)}<br><small>${escapeHtml(i.quantity_label)}</small></td><td class="num">${formatShekels(i.line_total_agorot)}</td></tr>`,
    )
    .join("");
  const hidden = `<input type="hidden" name="order" value="${order.id}"><input type="hidden" name="t" value="${token}">`;
  return `<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>דף תשלום לדוגמה · מצב בדיקה</title><link rel="icon" type="image/png" href="/assets/favicon.png"><link rel="stylesheet" href="/styles.css"></head>
<body class="mock-pay"><main class="wrap narrow">
<p class="test-banner" role="status">מצב בדיקה. זה אינו דף תשלום אמיתי ולא יבוצע חיוב.</p>
<p class="eyebrow">דף תשלום לדוגמה</p>
<h1 class="h2">הזמנה ${order.id}</h1>
<table class="summary-table"><tbody>${rows}</tbody>
<tfoot><tr><th scope="row">סה״כ <small>כולל מע״מ</small></th><td class="num">${formatShekels(order.total_agorot)}</td></tr></tfoot></table>
${
  order.status === "awaiting_payment"
    ? `<div class="mock-actions">
<form method="post" action="/pay/mock">${hidden}<input type="hidden" name="outcome" value="success"><button class="btn btn-primary" type="submit">סימולציה: תשלום הצליח</button></form>
<form method="post" action="/pay/mock">${hidden}<input type="hidden" name="outcome" value="failure"><button class="btn btn-secondary" type="submit">סימולציה: תשלום נכשל</button></form>
<form method="post" action="/pay/mock">${hidden}<input type="hidden" name="outcome" value="cancel"><button class="btn btn-ghost" type="submit">ביטול וחזרה לאתר</button></form>
</div>`
    : `<p>ההזמנה כבר אינה ממתינה לתשלום (${escapeHtml(order.status)}).</p><p><a href="/order?order=${order.id}&t=${token}">למצב ההזמנה</a></p>`
}
</main></body></html>`;
}

async function handleMockPage(url, env) {
  if (paymentMode(env) !== "mock") return json({ error: "not_found" }, 404);
  const token = url.searchParams.get("t");
  const order = await loadAuthorizedOrder(env, url.searchParams.get("order"), token);
  if (!order) return html("<p>הזמנה לא נמצאה.</p>", 404);
  return html(mockPage(order, token));
}

// The mock's "provider notification" goes through the same recordEvent/applyConfirmedPayment
// path as a real one, so double submits exercise the duplicate-event handling.
async function handleMockSubmit(request, env) {
  if (paymentMode(env) !== "mock") return json({ error: "not_found" }, 404);
  const form = await request.formData();
  const token = form.get("t");
  const order = await loadAuthorizedOrder(env, form.get("order"), token);
  if (!order) return html("<p>הזמנה לא נמצאה.</p>", 404);
  const outcome = form.get("outcome");
  const q = `order=${order.id}&t=${token}`;

  if (outcome === "success") {
    const eventKey = `mock:${order.id}:success`;
    const isNew = await recordEvent(env.DB, {
      provider: "mock",
      eventKey,
      orderId: order.id,
      payload: JSON.stringify({ outcome, at: nowIso() }),
    });
    if (isNew) {
      const result = await applyConfirmedPayment(env.DB, order.id, {
        amountAgorot: order.total_agorot,
        currency: order.currency,
        documentId: null,
        transactionId: `mock-${order.id}`,
      });
      await setEventOutcome(env.DB, eventKey, result);
    }
    return redirect(`/pay/return?${q}&result=success`);
  }
  if (outcome === "failure" || outcome === "cancel") {
    return redirect(`/pay/return?${q}&result=failure`);
  }
  return html("<p>פעולה לא מוכרת.</p>", 400);
}

// ---------------------------------------------------------------------------------------------

function publicConfig(env) {
  const mode = env.PAYMENT_MODE || "mock";
  return {
    paymentMode: mode,
    // A real charge is possible only in live mode with the explicit live switch on.
    liveCharges: mode === "morning_live" && env.ALLOW_LIVE_PAYMENTS === "yes",
    // ISO date-time of the round's opening, once decided. Empty = no dates or countdown shown.
    roundOpensAt: env.ROUND_OPENS_AT || null,
    roundDays: 14,
  };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const { pathname } = url;
    const method = request.method;
    try {
      if (pathname === "/api/config" && method === "GET") return json(publicConfig(env));
      if (pathname === "/api/catalog" && method === "GET") return json({ products: PRODUCTS });
      if (pathname === "/api/checkout" && method === "POST") return await handleCheckout(request, env);
      const m = pathname.match(/^\/api\/orders\/([^/]+)$/);
      if (m && method === "GET") return await handleOrderStatus(url, env, m[1]);
      if (pathname === "/api/morning/notify" && method === "POST") return await handleMorningNotify(request, url, env);
      if (pathname === "/pay/return" && method === "GET") return await handleReturn(url, env);
      if (pathname === "/pay/mock" && method === "GET") return await handleMockPage(url, env);
      if (pathname === "/pay/mock" && method === "POST") return await handleMockSubmit(request, env);
      if (pathname.startsWith("/api/") || pathname.startsWith("/pay/")) return json({ error: "not_found" }, 404);
      return env.ASSETS.fetch(request);
    } catch (err) {
      if (err instanceof HttpError) return json({ error: err.code }, err.status);
      console.error("unhandled", err);
      return json({ error: "server_error" }, 500);
    }
  },
};
