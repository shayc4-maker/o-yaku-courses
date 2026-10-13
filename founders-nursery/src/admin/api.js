// Admin API. Every exported handler assumes verifyAccess() already succeeded; the router in
// src/admin/router.js enforces that before any handler (and therefore any DB access) runs.
import { PRODUCTS, PRODUCTS_BY_ID, formatShekels } from "../../public/catalog.js";
import { voucherExpiry } from "../../public/purchase-policy.js";
import { json, sha256Hex, nowIso, SECURITY_HEADERS } from "../util.js";
import {
  REDEMPTION_STARTS_ON, SQL_EXPIRES_AT, israelDate, israelDayStartUtc, isValidDay, lineState, voucherState, STATE_LABELS,
} from "../fulfillment.js";
import { isLoopbackRequest } from "./access.js";

export const PAYMENT_LABELS = {
  awaiting_payment: "ממתין לתשלום",
  paid: "שולם",
  needs_review: "דורש בדיקה",
  cancelled: "לא הושלם",
  failed_to_start: "לא נפתח תשלום",
};
export const MODE_LABELS = { morning_live: "אמיתי", morning_sandbox: "Sandbox", mock: "הדמיה" };

export class ApiError extends Error {
  constructor(status, code, extra = {}) {
    super(code);
    this.status = status;
    this.code = code;
    this.extra = extra;
  }
}

// Clock. TEST_NOW is honoured only for requests addressed to a loopback host (local tests);
// behind the production route it is ignored.
export function nowMs(request, env) {
  if (env.TEST_NOW && isLoopbackRequest(new URL(request.url))) {
    const t = Date.parse(env.TEST_NOW);
    if (!Number.isNaN(t)) return t;
  }
  return Date.now();
}
const sqlTime = (ms) => new Date(ms).toISOString().replace("T", " ").slice(0, 19);

// "live" = real Morning sales only. "test" = mock + sandbox, always labelled as such.
function scopeOf(url) {
  const s = url.searchParams.get("scope") || "live";
  if (s !== "live" && s !== "test") throw new ApiError(400, "invalid_scope");
  return s;
}
const SCOPE_SQL = {
  live: "o.payment_mode = 'morning_live'",
  test: "o.payment_mode IN ('mock', 'morning_sandbox')",
};

const ORDER_ID_RE = /^OY-[23456789A-HJ-NP-Z]{8}$/;
const KEY_RE = /^[A-Za-z0-9_-]{16,80}$/;

function likeArg(q) {
  return `%${q.replace(/[\\%_]/g, (c) => "\\" + c)}%`;
}
function digits(s) {
  return String(s).replace(/\D/g, "");
}
const PHONE_DIGITS_SQL = (col) => `replace(replace(replace(replace(replace(${col}, '-', ''), ' ', ''), '+', ''), '(', ''), ')', '')`;

function pageArgs(url, maxSize = 100) {
  const page = Math.max(1, Math.min(10000, parseInt(url.searchParams.get("page") || "1", 10) || 1));
  const pageSize = Math.max(1, Math.min(maxSize, parseInt(url.searchParams.get("pageSize") || "25", 10) || 25));
  return { page, pageSize, offset: (page - 1) * pageSize };
}

// Per-order computed columns: units entitled, redeemed, expiry and redemption state.
function orderCalcSql(nowSql) {
  return `
    (SELECT COALESCE(SUM(oi.redeem_units), 0) FROM order_items oi WHERE oi.order_id = o.id) AS units,
    (SELECT COALESCE(SUM(r.quantity), 0) FROM redemptions r WHERE r.order_id = o.id) AS redeemed,
    ${SQL_EXPIRES_AT} AS expires_sql,
    CASE
      WHEN o.status != 'paid' THEN 'na'
      WHEN o.voucher_cancelled_at IS NOT NULL THEN 'cancelled'
      WHEN (SELECT COALESCE(SUM(r.quantity), 0) FROM redemptions r WHERE r.order_id = o.id)
           >= (SELECT COALESCE(SUM(oi.redeem_units), 0) FROM order_items oi WHERE oi.order_id = o.id) THEN 'full'
      WHEN ${SQL_EXPIRES_AT} <= '${nowSql}' THEN 'expired'
      WHEN (SELECT COALESCE(SUM(r.quantity), 0) FROM redemptions r WHERE r.order_id = o.id) > 0 THEN 'partial'
      ELSE 'not_redeemed'
    END AS redemption_state`;
}

// ---------------------------------------------------------------------------------------------- reads

export async function me(request, env, admin) {
  return json({ email: admin.email, paymentMode: env.PAYMENT_MODE || "mock", today: israelDate(nowMs(request, env)), redemptionStartsOn: REDEMPTION_STARTS_ON });
}

export async function summary(request, env) {
  const url = new URL(request.url);
  const scope = scopeOf(url);
  const db = env.DB;
  const totals = await db
    .prepare(
      `SELECT COUNT(*) AS paid_orders, COALESCE(SUM(o.total_agorot), 0) AS revenue_agorot, COUNT(DISTINCT o.buyer_id) AS buyers
       FROM orders o WHERE o.status = 'paid' AND ${SCOPE_SQL[scope]}`,
    )
    .first();
  const { results: other } = await db
    .prepare(`SELECT o.status, COUNT(*) AS n FROM orders o WHERE o.status != 'paid' AND ${SCOPE_SQL[scope]} GROUP BY o.status`)
    .all();
  const nowSql = sqlTime(nowMs(request, env));
  const { results: states } = await db
    .prepare(`SELECT redemption_state, COUNT(*) AS n FROM (SELECT ${orderCalcSql(nowSql)} FROM orders o WHERE o.status = 'paid' AND ${SCOPE_SQL[scope]}) GROUP BY redemption_state`)
    .all();
  return json({
    scope,
    paidOrders: totals.paid_orders,
    revenueAgorot: totals.revenue_agorot,
    buyers: totals.buyers,
    notSales: Object.fromEntries(other.map((r) => [r.status, r.n])),
    redemptionStates: Object.fromEntries(states.map((r) => [r.redemption_state, r.n])),
  });
}

export async function listOrders(request, env) {
  const url = new URL(request.url);
  const scope = scopeOf(url);
  const { page, pageSize, offset } = pageArgs(url);
  const where = [SCOPE_SQL[scope]];
  const args = [];

  const product = url.searchParams.get("product");
  if (product) {
    if (!PRODUCTS_BY_ID[product]) throw new ApiError(400, "invalid_product");
    where.push("EXISTS (SELECT 1 FROM order_items x WHERE x.order_id = o.id AND x.product_id = ?)");
    args.push(product);
  }
  const payment = url.searchParams.get("payment");
  if (payment) {
    if (!PAYMENT_LABELS[payment]) throw new ApiError(400, "invalid_payment");
    where.push("o.status = ?");
    args.push(payment);
  }
  for (const [param, op] of [["from", ">="], ["to", "<"]]) {
    const v = url.searchParams.get(param);
    if (!v) continue;
    if (!isValidDay(v)) throw new ApiError(400, `invalid_${param}`);
    const day = param === "to" ? new Date(Date.parse(`${v}T00:00:00Z`) + 86400000).toISOString().slice(0, 10) : v;
    where.push(`o.created_at ${op} ?`);
    args.push(israelDayStartUtc(day));
  }
  const q = (url.searchParams.get("q") || "").trim().slice(0, 100);
  if (q) {
    const d = digits(q);
    where.push(`(o.id LIKE ? ESCAPE '\\' OR o.customer_name LIKE ? ESCAPE '\\' OR lower(o.customer_email) LIKE ? ESCAPE '\\'${
      d.length >= 3 ? ` OR ${PHONE_DIGITS_SQL("o.customer_phone")} LIKE ?` : ""})`);
    args.push(likeArg(q.toUpperCase()), likeArg(q), likeArg(q.toLowerCase()));
    if (d.length >= 3) args.push(`%${d}%`);
  }
  const redemption = url.searchParams.get("redemption");
  const outer = [];
  if (redemption) {
    if (!STATE_LABELS[redemption]) throw new ApiError(400, "invalid_redemption");
    outer.push("redemption_state = ?");
  }
  const SORTS = { created: "created_at", paid: "paid_at", total: "total_agorot", id: "id", name: "customer_name" };
  const sort = SORTS[url.searchParams.get("sort") || "created"];
  if (!sort) throw new ApiError(400, "invalid_sort");
  const dir = url.searchParams.get("dir") === "asc" ? "ASC" : "DESC";

  const nowSql = sqlTime(nowMs(request, env));
  const inner = `SELECT o.id, o.created_at, o.paid_at, o.status, o.payment_mode, o.total_agorot, o.customer_name,
      o.customer_phone, o.customer_email, o.buyer_id, o.voucher_cancelled_at,
      (SELECT group_concat(x.name || ' — ' || x.quantity_label, ' | ') FROM order_items x WHERE x.order_id = o.id) AS items_text,
      ${orderCalcSql(nowSql)}
    FROM orders o WHERE ${where.join(" AND ")}`;
  const filterArgs = redemption ? [...args, redemption] : args;
  const outerWhere = outer.length ? `WHERE ${outer.join(" AND ")}` : "";
  const countRow = await env.DB.prepare(`SELECT COUNT(*) AS n FROM (${inner}) ${outerWhere}`).bind(...filterArgs).first();
  const { results } = await env.DB
    .prepare(`SELECT * FROM (${inner}) ${outerWhere} ORDER BY ${sort} ${dir} NULLS LAST, id ${dir} LIMIT ? OFFSET ?`)
    .bind(...filterArgs, pageSize, offset)
    .all();
  return json({
    scope, page, pageSize, total: countRow.n,
    orders: results.map((o) => ({
      id: o.id,
      createdAt: o.created_at,
      paidAt: o.paid_at,
      buyerId: o.buyer_id,
      customer: { name: o.customer_name, phone: o.customer_phone, email: o.customer_email },
      itemsText: o.items_text,
      totalAgorot: o.total_agorot,
      status: o.status,
      paymentMode: o.payment_mode,
      redemptionState: o.redemption_state,
      units: o.units,
      redeemed: o.redeemed,
      expiresAt: o.paid_at ? voucherExpiry(o.paid_at) : null,
    })),
  });
}

async function loadOrderDetail(env, orderId, ms) {
  const db = env.DB;
  const order = await db.prepare("SELECT * FROM orders WHERE id = ?").bind(orderId).first();
  if (!order) return null;
  const [items, redemptions, notes, activity, events] = await Promise.all([
    db.prepare(`SELECT oi.*, COALESCE((SELECT SUM(r.quantity) FROM redemptions r WHERE r.order_id = oi.order_id AND r.product_id = oi.product_id), 0) AS redeemed
                FROM order_items oi WHERE oi.order_id = ? ORDER BY oi.rowid`).bind(orderId).all(),
    db.prepare(`SELECT r.*, COALESCE((SELECT SUM(c.quantity) FROM redemptions c WHERE c.corrects_id = r.id), 0) AS corrected
                FROM redemptions r WHERE r.order_id = ? ORDER BY r.id`).bind(orderId).all(),
    db.prepare("SELECT * FROM order_notes WHERE order_id = ? ORDER BY id").bind(orderId).all(),
    db.prepare("SELECT * FROM admin_activity WHERE order_id = ? ORDER BY id").bind(orderId).all(),
    // Provider events: time and outcome only. Raw payloads stay out of the admin UI and exports.
    db.prepare("SELECT provider, outcome, received_at FROM payment_events WHERE order_id = ? ORDER BY id").bind(orderId).all(),
  ]);
  const paid = order.status === "paid" && !!order.paid_at;
  const expiresAt = paid ? voucherExpiry(order.paid_at) : null;
  const flags = { paid, cancelled: !!order.voucher_cancelled_at, expired: paid && Date.parse(expiresAt) <= ms };
  const lines = items.results.map((i) => {
    const units = i.redeem_units;
    return {
      productId: i.product_id,
      name: i.name,
      quantity: i.quantity,
      quantityLabel: i.quantity_label,
      unitPriceAgorot: i.unit_price_agorot,
      lineTotalAgorot: i.line_total_agorot,
      redemptionText: i.redemption_text,
      units,
      unitLabel: i.redeem_unit_label,
      redeemed: i.redeemed,
      remaining: Math.max(0, units - i.redeemed),
      state: lineState({ ...flags, units, redeemed: i.redeemed }),
    };
  });

  // Current coordination values: latest note per (product, kind).
  const current = {};
  for (const n of notes.results) if (n.kind !== "note") current[`${n.product_id || ""}:${n.kind}`] = n;

  const history = [
    { at: order.created_at, type: "created", text: "הזמנה נוצרה", by: null },
    order.terms_accepted_at && { at: order.terms_accepted_at, type: "terms", text: `אישור תנאים (${order.terms_version})`, by: null },
    ...events.results.map((e) => ({ at: e.received_at, type: "payment_event", text: `הודעת ${e.provider === "mock" ? "הדמיה" : "Morning"}: ${e.outcome || "התקבלה"}`, by: null })),
    order.paid_at && { at: order.paid_at, type: "paid", text: "תשלום אושר", by: null },
    ...redemptions.results.map((r) => ({
      at: r.created_at,
      type: r.kind,
      text: r.kind === "redeem"
        ? `מימוש ${r.quantity} ${unitLabelFor(lines, r.product_id)} · ${productName(lines, r.product_id)} · ${r.redeemed_on}`
        : `תיקון מימוש #${r.corrects_id}: הפחתה של ${Math.abs(r.quantity)} ${unitLabelFor(lines, r.product_id)} · ${productName(lines, r.product_id)}`,
      note: r.note,
      reason: r.reason,
      by: r.admin_email,
    })),
    ...notes.results.map((n) => ({
      at: n.created_at, type: "note", text: `${NOTE_KINDS[n.kind]?.label || n.kind}${n.product_id ? ` · ${productName(lines, n.product_id)}` : ""}: ${n.value}`, by: n.admin_email,
    })),
    ...activity.results.map((a) => ({ at: a.created_at, type: a.action, text: ACTIVITY_LABELS[a.action] || a.action, reason: a.reason, by: a.admin_email })),
  ].filter(Boolean).sort((a, b) => (a.at < b.at ? -1 : a.at > b.at ? 1 : 0));

  return {
    id: order.id,
    createdAt: order.created_at,
    paidAt: order.paid_at,
    status: order.status,
    statusReason: order.status_reason,
    paymentMode: order.payment_mode,
    totalAgorot: order.total_agorot,
    currency: order.currency,
    buyerId: order.buyer_id,
    customer: { name: order.customer_name, phone: order.customer_phone, email: order.customer_email },
    termsVersion: order.terms_version,
    termsAcceptedAt: order.terms_accepted_at,
    providerDocumentId: order.provider_document_id,
    voucher: paid ? {
      expiresAt,
      state: voucherState(lines, flags),
      cancelledAt: order.voucher_cancelled_at,
      cancelledBy: order.voucher_cancelled_by,
      cancelReason: order.voucher_cancel_reason,
    } : null,
    lines,
    redemptions: redemptions.results.map((r) => ({
      id: r.id, productId: r.product_id, kind: r.kind, quantity: r.quantity, correctsId: r.corrects_id,
      redeemedOn: r.redeemed_on, note: r.note, reason: r.reason, by: r.admin_email, at: r.created_at,
      correctable: r.kind === "redeem" ? r.quantity + r.corrected : 0,
    })),
    coordination: Object.values(current).map((n) => ({ productId: n.product_id, kind: n.kind, value: n.value, at: n.created_at, by: n.admin_email })),
    notes: notes.results.filter((n) => n.kind === "note").map((n) => ({ productId: n.product_id, value: n.value, at: n.created_at, by: n.admin_email })),
    history,
  };
}
const productName = (lines, id) => lines.find((l) => l.productId === id)?.name || id;
const unitLabelFor = (lines, id) => lines.find((l) => l.productId === id)?.unitLabel || "";
const ACTIVITY_LABELS = { voucher_cancelled: "השובר בוטל (חסימת מימוש בלבד, ללא החזר)" };

export async function getOrderAdmin(request, env, orderId) {
  if (!ORDER_ID_RE.test(orderId)) throw new ApiError(404, "not_found");
  const detail = await loadOrderDetail(env, orderId, nowMs(request, env));
  if (!detail) throw new ApiError(404, "not_found");
  return json(detail);
}

export async function listBuyers(request, env) {
  const url = new URL(request.url);
  const scope = scopeOf(url);
  const { page, pageSize, offset } = pageArgs(url);
  const q = (url.searchParams.get("q") || "").trim().slice(0, 100);
  const args = [];
  let search = "";
  if (q) {
    const d = digits(q);
    search = `AND (b.name LIKE ? ESCAPE '\\' OR b.email_normalized LIKE ? ESCAPE '\\'
      OR EXISTS (SELECT 1 FROM orders s WHERE s.buyer_id = b.id AND (s.customer_name LIKE ? ESCAPE '\\'${d.length >= 3 ? ` OR ${PHONE_DIGITS_SQL("s.customer_phone")} LIKE ?` : ""}))
      ${d.length >= 3 ? `OR ${PHONE_DIGITS_SQL("b.phone")} LIKE ?` : ""})`;
    args.push(likeArg(q), likeArg(q.toLowerCase()), likeArg(q));
    if (d.length >= 3) args.push(`%${d}%`, `%${d}%`);
  }
  const base = `FROM buyers b JOIN orders o ON o.buyer_id = b.id AND ${SCOPE_SQL[scope]} WHERE 1 = 1 ${search}`;
  const count = await env.DB.prepare(`SELECT COUNT(DISTINCT b.id) AS n ${base}`).bind(...args).first();
  const { results } = await env.DB
    .prepare(
      `SELECT b.id, b.name, b.phone, b.email_normalized AS email,
         COUNT(o.id) AS orders,
         SUM(CASE WHEN o.status = 'paid' THEN 1 ELSE 0 END) AS paid_orders,
         COALESCE(SUM(CASE WHEN o.status = 'paid' THEN o.total_agorot ELSE 0 END), 0) AS paid_agorot,
         MAX(o.created_at) AS last_order_at
       ${base} GROUP BY b.id ORDER BY last_order_at DESC, b.id DESC LIMIT ? OFFSET ?`,
    )
    .bind(...args, pageSize, offset)
    .all();
  return json({
    scope, page, pageSize, total: count.n,
    buyers: results.map((b) => ({
      id: b.id, name: b.name, phone: b.phone, email: b.email, orders: b.orders, paidOrders: b.paid_orders,
      paidAgorot: b.paid_agorot, lastOrderAt: b.last_order_at,
    })),
  });
}

export async function getBuyer(request, env, buyerId) {
  const id = Number(buyerId);
  if (!Number.isInteger(id) || id < 1) throw new ApiError(404, "not_found");
  const db = env.DB;
  const buyer = await db.prepare("SELECT * FROM buyers WHERE id = ?").bind(id).first();
  if (!buyer) throw new ApiError(404, "not_found");
  const ms = nowMs(request, env);
  const { results: orders } = await db
    .prepare(`SELECT o.*, ${orderCalcSql(sqlTime(ms))} FROM orders o WHERE o.buyer_id = ? ORDER BY o.created_at DESC`)
    .bind(id)
    .all();

  // Balances per paid order line, all environments, each line marked with its environment.
  const { results: lines } = await db
    .prepare(
      `SELECT oi.order_id, oi.product_id, oi.name, oi.quantity_label, oi.redeem_units, oi.redeem_unit_label, o.payment_mode,
         o.paid_at, o.voucher_cancelled_at,
         COALESCE((SELECT SUM(r.quantity) FROM redemptions r WHERE r.order_id = oi.order_id AND r.product_id = oi.product_id), 0) AS redeemed
       FROM order_items oi JOIN orders o ON o.id = oi.order_id
       WHERE o.buyer_id = ? AND o.status = 'paid' ORDER BY o.paid_at DESC, oi.rowid`,
    )
    .bind(id)
    .all();

  // Explicit mismatch report: orders whose recorded name/phone differ from the buyer record.
  // Nothing is merged or rewritten automatically.
  const variants = [...new Set(orders.map((o) => `${o.customer_name} · ${o.customer_phone}`))];
  const { results: samePhone } = await db
    .prepare(
      `SELECT DISTINCT b.id, b.name, b.email_normalized AS email FROM buyers b JOIN orders o ON o.buyer_id = b.id
       WHERE b.id != ? AND ${PHONE_DIGITS_SQL("o.customer_phone")} = ?`,
    )
    .bind(id, digits(buyer.phone))
    .all();

  const paidLive = orders.filter((o) => o.status === "paid" && o.payment_mode === "morning_live");
  return json({
    id: buyer.id,
    name: buyer.name,
    phone: buyer.phone,
    email: buyer.email_normalized,
    createdAt: buyer.created_at,
    paidLiveAgorot: paidLive.reduce((n, o) => n + o.total_agorot, 0),
    paidLiveOrders: paidLive.length,
    detailVariants: variants.length > 1 ? variants : [],
    samePhoneOtherBuyers: samePhone,
    orders: orders.map((o) => ({
      id: o.id, createdAt: o.created_at, paidAt: o.paid_at, status: o.status, paymentMode: o.payment_mode,
      totalAgorot: o.total_agorot, redemptionState: o.redemption_state, customer: { name: o.customer_name, phone: o.customer_phone, email: o.customer_email },
    })),
    balances: lines.map((l) => {
      const expiresAt = voucherExpiry(l.paid_at);
      const flags = { paid: true, cancelled: !!l.voucher_cancelled_at, expired: Date.parse(expiresAt) <= ms };
      return {
        orderId: l.order_id, productId: l.product_id, name: l.name, quantityLabel: l.quantity_label, paymentMode: l.payment_mode,
        units: l.redeem_units, unitLabel: l.redeem_unit_label, redeemed: l.redeemed,
        remaining: flags.cancelled || flags.expired ? 0 : Math.max(0, l.redeem_units - l.redeemed),
        state: lineState({ ...flags, units: l.redeem_units, redeemed: l.redeemed }), expiresAt,
      };
    }),
  });
}

async function productRows(env, scope, ms) {
  const nowSql = sqlTime(ms);
  const { results } = await env.DB
    .prepare(
      `SELECT oi.product_id,
         SUM(oi.quantity) AS qty, SUM(oi.redeem_units) AS units, SUM(oi.line_total_agorot) AS revenue_agorot,
         SUM(COALESCE(r.red, 0)) AS redeemed,
         SUM(CASE WHEN o.voucher_cancelled_at IS NULL AND ${SQL_EXPIRES_AT} > '${nowSql}' THEN oi.redeem_units - COALESCE(r.red, 0) ELSE 0 END) AS remaining,
         SUM(CASE WHEN o.voucher_cancelled_at IS NOT NULL OR ${SQL_EXPIRES_AT} <= '${nowSql}' THEN oi.redeem_units - COALESCE(r.red, 0) ELSE 0 END) AS lapsed
       FROM order_items oi
       JOIN orders o ON o.id = oi.order_id
       LEFT JOIN (SELECT order_id, product_id, SUM(quantity) AS red FROM redemptions GROUP BY order_id, product_id) r
         ON r.order_id = oi.order_id AND r.product_id = oi.product_id
       WHERE o.status = 'paid' AND ${SCOPE_SQL[scope]}
       GROUP BY oi.product_id`,
    )
    .all();
  const byId = Object.fromEntries(results.map((r) => [r.product_id, r]));
  // Catalog order for the nine current products, plus any product that only exists in old orders.
  const ids = [...PRODUCTS.map((p) => p.id), ...results.map((r) => r.product_id).filter((id) => !PRODUCTS_BY_ID[id])];
  return ids.map((id) => {
    const p = PRODUCTS_BY_ID[id];
    const r = byId[id] || { qty: 0, units: 0, revenue_agorot: 0, redeemed: 0, remaining: 0, lapsed: 0 };
    return {
      productId: id,
      name: p?.name || id,
      saleUnit: p ? p.unit.many : "",
      redeemUnit: p?.perUnitCount ? p.perUnitCount.label : p ? p.unit.many : "",
      perSaleUnit: p?.perUnitCount?.size || 1,
      soldQty: r.qty,
      soldUnits: r.units,
      revenueAgorot: r.revenue_agorot,
      redeemedUnits: r.redeemed,
      remainingUnits: r.remaining,
      lapsedUnits: r.lapsed,
    };
  });
}

export async function products(request, env) {
  const scope = scopeOf(new URL(request.url));
  return json({ scope, products: await productRows(env, scope, nowMs(request, env)) });
}

// ---------------------------------------------------------------------------------------------- writes

async function readBody(request) {
  const text = await request.text();
  if (text.length > 8 * 1024) throw new ApiError(413, "payload_too_large");
  try {
    const v = JSON.parse(text);
    if (!v || typeof v !== "object" || Array.isArray(v)) throw new Error();
    return v;
  } catch {
    throw new ApiError(400, "invalid_json");
  }
}
function cleanText(v, max, field, required = false) {
  if (v == null || v === "") {
    if (required) throw new ApiError(400, `${field}_required`);
    return null;
  }
  if (typeof v !== "string") throw new ApiError(400, `invalid_${field}`);
  const s = v.trim().replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "");
  if (required && s.length === 0) throw new ApiError(400, `${field}_required`);
  if (s.length > max) throw new ApiError(400, `${field}_too_long`);
  return s || null;
}
function requireKey(body) {
  if (typeof body.idempotencyKey !== "string" || !KEY_RE.test(body.idempotencyKey)) throw new ApiError(400, "invalid_idempotency_key");
  return body.idempotencyKey;
}

async function replayOrConflict(env, key, fingerprint) {
  const row = await env.DB.prepare("SELECT * FROM redemptions WHERE idempotency_key = ?").bind(key).first();
  if (!row) return null;
  if (row.request_fingerprint !== fingerprint) throw new ApiError(409, "idempotency_conflict");
  return row;
}

// Records a redemption. The balance check and the insert are one SQL statement, so two tabs or
// two concurrent requests can never redeem more than was paid for (D1 executes statements serially).
export async function redeem(request, env, admin, orderId) {
  if (!ORDER_ID_RE.test(orderId)) throw new ApiError(404, "not_found");
  const body = await readBody(request);
  const key = requireKey(body);
  const productId = typeof body.productId === "string" ? body.productId : "";
  const qty = body.quantity;
  if (!Number.isInteger(qty) || qty < 1 || qty > 10000) throw new ApiError(400, "invalid_quantity");
  const day = body.date;
  if (!isValidDay(day)) throw new ApiError(400, "invalid_date");
  const note = cleanText(body.note, 500, "note");
  const fingerprint = await sha256Hex(JSON.stringify(["redeem", orderId, productId, qty, day, note]));

  const replay = await replayOrConflict(env, key, fingerprint);
  if (replay) return json({ ok: true, replayed: true, redemption: { id: replay.id } });

  const ms = nowMs(request, env);
  const today = israelDate(ms);
  if (today < REDEMPTION_STARTS_ON) throw new ApiError(409, "redemption_not_started", { startsOn: REDEMPTION_STARTS_ON });
  if (day < REDEMPTION_STARTS_ON) throw new ApiError(400, "date_before_redemption_start", { startsOn: REDEMPTION_STARTS_ON });
  if (day > today) throw new ApiError(400, "date_in_future");

  const order = await env.DB.prepare("SELECT id, status, paid_at, voucher_cancelled_at FROM orders WHERE id = ?").bind(orderId).first();
  if (!order) throw new ApiError(404, "not_found");
  if (order.status !== "paid" || !order.paid_at) throw new ApiError(409, "order_not_paid");
  if (order.voucher_cancelled_at) throw new ApiError(409, "voucher_cancelled");
  const expiresAt = voucherExpiry(order.paid_at);
  if (Date.parse(expiresAt) <= ms) throw new ApiError(409, "voucher_expired", { expiresAt });
  if (day > israelDate(Date.parse(expiresAt))) throw new ApiError(400, "date_after_expiry");

  const ts = nowIso();
  const r = await env.DB
    .prepare(
      `INSERT INTO redemptions (order_id, product_id, kind, quantity, redeemed_on, note, admin_email, idempotency_key, request_fingerprint, created_at)
       SELECT ?1, ?2, 'redeem', ?3, ?4, ?5, ?6, ?7, ?8, ?9
       WHERE EXISTS (SELECT 1 FROM orders o WHERE o.id = ?1 AND o.status = 'paid' AND o.voucher_cancelled_at IS NULL)
         AND (SELECT oi.redeem_units FROM order_items oi WHERE oi.order_id = ?1 AND oi.product_id = ?2)
             - COALESCE((SELECT SUM(x.quantity) FROM redemptions x WHERE x.order_id = ?1 AND x.product_id = ?2), 0) >= ?3
       ON CONFLICT(idempotency_key) DO NOTHING`,
    )
    .bind(orderId, productId, qty, day, note, admin.email, key, fingerprint, ts)
    .run();

  if (r.meta.changes === 1) {
    const row = await env.DB.prepare("SELECT id FROM redemptions WHERE idempotency_key = ?").bind(key).first();
    return json({ ok: true, redemption: { id: row.id } }, 201);
  }
  // Nothing inserted: a concurrent request with the same key, or a rule failed at write time.
  const again = await replayOrConflict(env, key, fingerprint);
  if (again) return json({ ok: true, replayed: true, redemption: { id: again.id } });
  const line = await env.DB
    .prepare(`SELECT oi.redeem_units AS units, COALESCE((SELECT SUM(x.quantity) FROM redemptions x WHERE x.order_id = oi.order_id AND x.product_id = oi.product_id), 0) AS redeemed
              FROM order_items oi WHERE oi.order_id = ? AND oi.product_id = ?`)
    .bind(orderId, productId)
    .first();
  if (!line) throw new ApiError(400, "invalid_product");
  const now = await env.DB.prepare("SELECT status, voucher_cancelled_at FROM orders WHERE id = ?").bind(orderId).first();
  if (now.voucher_cancelled_at) throw new ApiError(409, "voucher_cancelled");
  if (now.status !== "paid") throw new ApiError(409, "order_not_paid");
  throw new ApiError(409, "insufficient_balance", { remaining: Math.max(0, line.units - line.redeemed) });
}

// A correction reverses part or all of one earlier redemption. History is never deleted.
export async function correct(request, env, admin, redemptionId) {
  const id = Number(redemptionId);
  if (!Number.isInteger(id) || id < 1) throw new ApiError(404, "not_found");
  const body = await readBody(request);
  const key = requireKey(body);
  const qty = body.quantity;
  if (!Number.isInteger(qty) || qty < 1 || qty > 10000) throw new ApiError(400, "invalid_quantity");
  const reason = cleanText(body.reason, 500, "reason", true);
  if (reason.length < 3) throw new ApiError(400, "reason_required");
  const fingerprint = await sha256Hex(JSON.stringify(["correct", id, qty, reason]));
  const replay = await replayOrConflict(env, key, fingerprint);
  if (replay) return json({ ok: true, replayed: true, redemption: { id: replay.id } });

  const orig = await env.DB.prepare("SELECT * FROM redemptions WHERE id = ?").bind(id).first();
  if (!orig) throw new ApiError(404, "not_found");
  if (orig.kind !== "redeem") throw new ApiError(400, "not_a_redemption");

  const ts = nowIso();
  const r = await env.DB
    .prepare(
      `INSERT INTO redemptions (order_id, product_id, kind, quantity, corrects_id, redeemed_on, reason, admin_email, idempotency_key, request_fingerprint, created_at)
       SELECT o.order_id, o.product_id, 'correction', -?2, o.id, ?3, ?4, ?5, ?6, ?7, ?8
       FROM redemptions o
       WHERE o.id = ?1 AND o.kind = 'redeem'
         AND o.quantity + COALESCE((SELECT SUM(c.quantity) FROM redemptions c WHERE c.corrects_id = o.id), 0) >= ?2
       ON CONFLICT(idempotency_key) DO NOTHING`,
    )
    .bind(id, qty, israelDate(nowMs(request, env)), reason, admin.email, key, fingerprint, ts)
    .run();
  if (r.meta.changes === 1) {
    const row = await env.DB.prepare("SELECT id FROM redemptions WHERE idempotency_key = ?").bind(key).first();
    return json({ ok: true, redemption: { id: row.id } }, 201);
  }
  const again = await replayOrConflict(env, key, fingerprint);
  if (again) return json({ ok: true, replayed: true, redemption: { id: again.id } });
  throw new ApiError(409, "correction_exceeds_redemption");
}

// Blocks further redemption. Not a refund: payment status is never changed here.
export async function cancelVoucher(request, env, admin, orderId) {
  if (!ORDER_ID_RE.test(orderId)) throw new ApiError(404, "not_found");
  const body = await readBody(request);
  const reason = cleanText(body.reason, 500, "reason", true);
  if (reason.length < 3) throw new ApiError(400, "reason_required");
  if (body.confirm !== true) throw new ApiError(400, "confirm_required");
  const order = await env.DB.prepare("SELECT status, voucher_cancelled_at FROM orders WHERE id = ?").bind(orderId).first();
  if (!order) throw new ApiError(404, "not_found");
  if (order.status !== "paid") throw new ApiError(409, "order_not_paid");
  if (order.voucher_cancelled_at) return json({ ok: true, alreadyCancelled: true });
  const ts = nowIso();
  const [upd] = await env.DB.batch([
    env.DB
      .prepare(`UPDATE orders SET voucher_cancelled_at = ?, voucher_cancelled_by = ?, voucher_cancel_reason = ?
                WHERE id = ? AND status = 'paid' AND voucher_cancelled_at IS NULL`)
      .bind(ts, admin.email, reason, orderId),
    env.DB
      .prepare(`INSERT INTO admin_activity (order_id, action, details, reason, admin_email, created_at)
                SELECT id, 'voucher_cancelled', NULL, ?, ?, ? FROM orders
                WHERE id = ? AND voucher_cancelled_at = ? AND voucher_cancelled_by = ?`)
      .bind(reason, admin.email, ts, orderId, ts, admin.email),
  ]);
  return json({ ok: true, alreadyCancelled: upd.meta.changes !== 1 });
}

export const NOTE_KINDS = {
  note: { label: "הערה פנימית", max: 1000 },
  session: { label: "מועד סדנה / שיעור", max: 200 },
  shirt_size: { label: "מידת חולצה", max: 60 },
  pickup: { label: "תיאום איסוף", max: 500 },
  shipping: { label: "תיאום משלוח", max: 500 },
  pot_details: { label: "פרטי כלי בהזמנה אישית", max: 1000 },
  trees_in: { label: "הכנסת עצים", date: true },
  service_end: { label: "סיום שנת השירות", date: true },
};

// Coordination data never changes redeemed quantities.
export async function addNote(request, env, admin, orderId) {
  if (!ORDER_ID_RE.test(orderId)) throw new ApiError(404, "not_found");
  const body = await readBody(request);
  const kind = NOTE_KINDS[body.kind] ? body.kind : null;
  if (!kind) throw new ApiError(400, "invalid_kind");
  const spec = NOTE_KINDS[kind];
  let value;
  if (spec.date) {
    if (!isValidDay(body.value)) throw new ApiError(400, "invalid_date");
    value = body.value;
  } else {
    value = cleanText(body.value, spec.max, "value", true);
  }
  const order = await env.DB.prepare("SELECT id FROM orders WHERE id = ?").bind(orderId).first();
  if (!order) throw new ApiError(404, "not_found");
  let productId = null;
  if (body.productId) {
    const line = await env.DB.prepare("SELECT 1 FROM order_items WHERE order_id = ? AND product_id = ?").bind(orderId, body.productId).first();
    if (!line) throw new ApiError(400, "invalid_product");
    productId = body.productId;
  }
  await env.DB
    .prepare("INSERT INTO order_notes (order_id, product_id, kind, value, admin_email, created_at) VALUES (?, ?, ?, ?, ?, ?)")
    .bind(orderId, productId, kind, value, admin.email, nowIso())
    .run();
  return json({ ok: true }, 201);
}

// ---------------------------------------------------------------------------------------------- CSV

// Cells that a spreadsheet would treat as a formula are prefixed with an apostrophe.
export function csvCell(v) {
  if (v == null) return "";
  if (typeof v === "number") return String(v);
  let s = String(v);
  if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}
export function toCsv(header, rows) {
  return "﻿" + [header, ...rows].map((r) => r.map(csvCell).join(",")).join("\r\n") + "\r\n";
}
const shekels = (agorot) => agorot / 100;
const day = (iso) => (iso ? israelDate(Date.parse(iso)) : "");

export async function exportCsv(request, env, kind) {
  const url = new URL(request.url);
  const scope = scopeOf(url);
  const ms = nowMs(request, env);
  const envLabel = (m) => MODE_LABELS[m] || m;
  let header;
  let rows;
  if (kind === "buyers") {
    const { results } = await env.DB
      .prepare(
        `SELECT b.id, b.name, b.phone, b.email_normalized AS email, o.payment_mode,
           SUM(CASE WHEN o.status = 'paid' THEN 1 ELSE 0 END) AS paid_orders,
           COALESCE(SUM(CASE WHEN o.status = 'paid' THEN o.total_agorot ELSE 0 END), 0) AS paid_agorot
         FROM buyers b JOIN orders o ON o.buyer_id = b.id AND ${SCOPE_SQL[scope]}
         GROUP BY b.id, o.payment_mode ORDER BY b.id`,
      )
      .all();
    header = ["סביבה", "מזהה קונה", "שם", "טלפון", "אימייל", "הזמנות ששולמו", "סכום ששולם (₪, כולל מע״מ)"];
    rows = results.map((b) => [envLabel(b.payment_mode), b.id, b.name, b.phone, b.email, b.paid_orders, shekels(b.paid_agorot)]);
  } else if (kind === "orders") {
    const { results } = await env.DB
      .prepare(
        `SELECT o.id, o.created_at, o.paid_at, o.status, o.payment_mode, o.total_agorot, o.customer_name, o.customer_phone,
           o.customer_email, o.buyer_id,
           (SELECT group_concat(x.name || ' — ' || x.quantity_label, ' | ') FROM order_items x WHERE x.order_id = o.id) AS items_text,
           ${orderCalcSql(sqlTime(ms))}
         FROM orders o WHERE ${SCOPE_SQL[scope]} ORDER BY o.created_at`,
      )
      .all();
    header = ["סביבה", "מספר הזמנה", "תאריך הזמנה", "תאריך תשלום", "מזהה קונה", "שם", "טלפון", "אימייל", "פריטים",
      "סה״כ (₪, כולל מע״מ)", "מצב תשלום", "מצב מימוש", "תוקף שובר"];
    rows = results.map((o) => [envLabel(o.payment_mode), o.id, day(o.created_at), day(o.paid_at), o.buyer_id, o.customer_name,
      o.customer_phone, o.customer_email, o.items_text, shekels(o.total_agorot), PAYMENT_LABELS[o.status] || o.status,
      STATE_LABELS[o.redemption_state], o.paid_at ? day(voucherExpiry(o.paid_at)) : ""]);
  } else if (kind === "balances") {
    const { results } = await env.DB
      .prepare(
        `SELECT oi.order_id, oi.product_id, oi.name, oi.quantity, oi.quantity_label, oi.redeem_units, oi.redeem_unit_label,
           o.payment_mode, o.paid_at, o.voucher_cancelled_at, o.customer_name, o.customer_phone,
           COALESCE((SELECT SUM(r.quantity) FROM redemptions r WHERE r.order_id = oi.order_id AND r.product_id = oi.product_id), 0) AS redeemed
         FROM order_items oi JOIN orders o ON o.id = oi.order_id
         WHERE o.status = 'paid' AND ${SCOPE_SQL[scope]} ORDER BY o.paid_at, oi.rowid`,
      )
      .all();
    header = ["סביבה", "מספר הזמנה", "שם", "טלפון", "מוצר", "כמות שנרכשה", "יחידות למימוש", "יחידה", "מומש", "יתרה", "מצב", "תוקף שובר"];
    rows = results.map((l) => {
      const expiresAt = voucherExpiry(l.paid_at);
      const flags = { paid: true, cancelled: !!l.voucher_cancelled_at, expired: Date.parse(expiresAt) <= ms };
      const remaining = flags.cancelled || flags.expired ? 0 : Math.max(0, l.redeem_units - l.redeemed);
      return [envLabel(l.payment_mode), l.order_id, l.customer_name, l.customer_phone, l.name, l.quantity_label, l.redeem_units,
        l.redeem_unit_label, l.redeemed, remaining, STATE_LABELS[lineState({ ...flags, units: l.redeem_units, redeemed: l.redeemed })], day(expiresAt)];
    });
  } else {
    throw new ApiError(404, "not_found");
  }
  const stamp = israelDate(ms);
  return new Response(toCsv(header, rows), {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="oyaku-${kind}-${scope === "live" ? "live" : "TEST"}-${stamp}.csv"`,
      "Cache-Control": "no-store",
      ...SECURITY_HEADERS,
    },
  });
}

export { formatShekels };
