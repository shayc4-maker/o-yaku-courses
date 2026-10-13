// Morning (Green Invoice) adapter.
//
// Prepared against https://developers.morning.co/docs/openapi.bundled.json on 2026-10-07.
// Account-specific payment plugin and end-to-end sandbox behaviour still need verification.
//
// Base URLs are not hard-coded here — they come from configuration (MORNING_API_BASE,
// MORNING_AUTH_BASE) so they can be corrected without a code change.

let cachedToken = null; // { value, expiresAtMs, cacheKey }

async function getAccessToken(env) {
  if (!env.MORNING_API_KEY_ID || !env.MORNING_API_KEY_SECRET) throw new Error("morning_credentials_missing");
  const cacheKey = `${env.MORNING_AUTH_BASE}:${env.MORNING_API_BASE}:${env.MORNING_API_KEY_ID}:${env.MORNING_API_KEY_SECRET}`;
  if (cachedToken && cachedToken.cacheKey === cacheKey && cachedToken.expiresAtMs - Date.now() > 60_000) {
    return cachedToken.value;
  }

  let res;
  if (!env.MORNING_AUTH_FLOW || env.MORNING_AUTH_FLOW === "oauth") {
    res = await fetch(`${env.MORNING_AUTH_BASE}/idp/v1/oauth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        grant_type: "client_credentials",
        client_id: env.MORNING_API_KEY_ID,
        client_secret: env.MORNING_API_KEY_SECRET,
      }),
    });
  } else {
    // Long-documented flow: POST /account/token with the API key id + secret. To verify.
    res = await fetch(`${env.MORNING_API_BASE}/account/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: env.MORNING_API_KEY_ID, secret: env.MORNING_API_KEY_SECRET }),
    });
  }
  const body = await res.json().catch(() => ({}));
  const value = body.accessToken || body.access_token || body.token;
  if (!res.ok || !value) {
    throw new Error(`morning_auth_failed: HTTP ${res.status}`);
  }
  const expiresAtMs = body.expiresAt
    ? Number(body.expiresAt) * 1000
    : body.expires_in
      ? Date.now() + Number(body.expires_in) * 1000
      : Date.now() + 20 * 60_000;
  cachedToken = { value, expiresAtMs, cacheKey };
  return value;
}

async function morningFetch(env, path, init = {}) {
  const token = await getAccessToken(env);
  return fetch(`${env.MORNING_API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}`, ...(init.headers || {}) },
  });
}

const agorotToShekels = (a) => Math.round(a) / 100;

// Requests a one-off hosted payment page for this exact order.
// The amount and every line come from the server-side priced order, never from the browser.
export async function createPaymentPage(env, order, urls) {
  const body = {
    description: `משתלת אויאקו — הזמנה ${order.id}`,
    type: 320, // חשבונית מס / קבלה for this VAT-registered business.
    lang: "he",
    currency: order.currency,
    vatType: 0,
    amount: agorotToShekels(order.totalAgorot),
    maxPayments: 1,
    group: Number(env.MORNING_GROUP || 100), // Grow requires a payment group; 100 = credit card.
    client: {
      name: order.customer.name,
      emails: [order.customer.email],
      phone: order.customer.phone,
    },
    remarks: `הזמנה ${order.id}`,
    successUrl: urls.successUrl,
    failureUrl: urls.failureUrl,
    notifyUrl: urls.notifyUrl,
    custom: order.id,
  };
  if (env.MORNING_SEND_INCOME_LINES !== "false") {
    // Official ItemVatType 1 means VAT included in the unit price.
    body.income = order.lines.map((l) => ({
      description: l.name,
      quantity: l.quantity,
      price: agorotToShekels(l.unitPriceAgorot),
      currency: order.currency,
      vatType: Number(env.MORNING_INCOME_VAT_TYPE ?? 1),
    }));
  }
  if (env.MORNING_PLUGIN_ID) body.pluginId = env.MORNING_PLUGIN_ID;
  if (env.MORNING_GROUP) body.group = Number(env.MORNING_GROUP);

  const res = await morningFetch(env, "/payments/form", { method: "POST", body: JSON.stringify(body) });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.success === false || (data.errorCode != null && data.errorCode !== 0) || !data.url) {
    throw new Error(`morning_form_failed: HTTP ${res.status} code ${data.errorCode ?? "unknown"}`);
  }
  const paymentUrl = new URL(data.url);
  if (paymentUrl.protocol !== "https:" && !(env.PAYMENT_MODE === "morning_sandbox" && ["127.0.0.1", "localhost"].includes(paymentUrl.hostname))) {
    throw new Error("morning_form_insecure_url");
  }
  return { paymentUrl: data.url };
}

// Pulls a candidate document id out of a notification payload. The payload shape is not verified,
// so this only looks in a few plausible places and returns null otherwise.
export function extractDocumentId(payload) {
  if (!payload || typeof payload !== "object") return null;
  const candidates = [payload.documentId, payload.document?.id, payload.data?.documentId, payload.data?.document?.id, payload.id];
  const found = candidates.find((v) => typeof v === "string" && /^[A-Za-z0-9-]{8,64}$/.test(v));
  return found ?? null;
}

// Confirms a payment by reading the document back from Morning's API with our own credentials.
// The notification body itself is never treated as proof. Returns { confirmed: true, ... } only
// when the document exists, references this order, and its amount/currency can be read.
export async function confirmPayment(env, orderId, payload) {
  const documentId = extractDocumentId(payload);
  if (!documentId) return { confirmed: false, reason: "no_document_id_in_notification" };

  const res = await morningFetch(env, `/documents/${encodeURIComponent(documentId)}`, { method: "GET" });
  if (!res.ok) return { confirmed: false, reason: `document_lookup_http_${res.status}`, retryable: [404, 408, 429].includes(res.status) || res.status >= 500 };
  const doc = await res.json().catch(() => null);
  if (!doc) return { confirmed: false, reason: "document_lookup_unreadable", retryable: true };
  if (doc.id !== documentId) return { confirmed: false, reason: "document_id_mismatch" };
  if (doc.type !== 320) return { confirmed: false, reason: "not_payment_receipt" };
  if (![0, 1].includes(doc.status)) return { confirmed: false, reason: "document_cancelled_or_unverified_status" };

  const references = [doc.remarks, doc.description, doc.custom].filter(Boolean).join(" ");
  if (!new RegExp(`\\b${orderId}\\b`).test(references)) return { confirmed: false, reason: "document_does_not_reference_order" };
  if (!Number.isFinite(doc.amount) || doc.amount <= 0 || doc.currency !== "ILS") return { confirmed: false, reason: "document_amount_or_currency_invalid" };
  if (!Array.isArray(doc.payment) || !doc.payment.length || doc.payment.some((p) =>
    ![3, 10].includes(p.type) || p.currency !== doc.currency || !Number.isFinite(p.price) || p.price <= 0)) {
    return { confirmed: false, reason: "document_has_no_verified_online_payments" };
  }
  const paidAgorot = doc.payment.reduce((sum, p) => sum + Math.round(p.price * 100), 0);
  if (paidAgorot !== Math.round(doc.amount * 100)) return { confirmed: false, reason: "document_payment_total_mismatch" };

  return {
    confirmed: true,
    amountAgorot: Math.round(doc.amount * 100),
    currency: doc.currency,
    documentId,
    transactionId: doc.payment?.[0]?.transactionId ?? null,
  };
}
