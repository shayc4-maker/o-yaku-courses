import { nowIso } from "./util.js";

export async function getOrder(db, orderId) {
  const order = await db.prepare("SELECT * FROM orders WHERE id = ?").bind(orderId).first();
  if (!order) return null;
  const { results } = await db
    .prepare("SELECT * FROM order_items WHERE order_id = ? ORDER BY rowid")
    .bind(orderId)
    .all();
  return { ...order, items: results };
}

export async function getOrderByIdempotencyKey(db, key) {
  const row = await db.prepare("SELECT id FROM orders WHERE idempotency_key = ?").bind(key).first();
  return row ? getOrder(db, row.id) : null;
}

// Inserts the order and its lines atomically. Throws on a duplicate idempotency key,
// which the caller treats as "another request already created this order".
export async function insertOrder(db, order, lines) {
  const ts = nowIso();
  const stmts = [
    db
      .prepare(
        `INSERT INTO orders (id, access_token, idempotency_key, request_fingerprint, status, payment_mode,
           currency, total_agorot, customer_name, customer_email, customer_phone, created_at, updated_at)
         VALUES (?, ?, ?, ?, 'awaiting_payment', ?, ?, ?, ?, ?, ?, ?, ?)`,
      )
      .bind(
        order.id,
        order.accessToken,
        order.idempotencyKey,
        order.fingerprint,
        order.paymentMode,
        order.currency,
        order.totalAgorot,
        order.customer.name,
        order.customer.email,
        order.customer.phone,
        ts,
        ts,
      ),
    ...lines.map((l) =>
      db
        .prepare(
          `INSERT INTO order_items (order_id, product_id, name, unit_label, quantity_label,
             unit_price_agorot, quantity, line_total_agorot) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
        )
        .bind(order.id, l.productId, l.name, l.unitLabel, l.quantityLabel, l.unitPriceAgorot, l.quantity, l.lineTotalAgorot),
    ),
  ];
  await db.batch(stmts);
}

export async function setPaymentUrl(db, orderId, url) {
  await db
    .prepare("UPDATE orders SET provider_payment_url = ?, updated_at = ? WHERE id = ? AND status = 'awaiting_payment'")
    .bind(url, nowIso(), orderId)
    .run();
}

// Moves an order out of awaiting_payment only. Never touches a paid order.
export async function setStatusIfAwaiting(db, orderId, status, reason = null) {
  const r = await db
    .prepare("UPDATE orders SET status = ?, status_reason = ?, updated_at = ? WHERE id = ? AND status = 'awaiting_payment'")
    .bind(status, reason, nowIso(), orderId)
    .run();
  return r.meta.changes === 1;
}

// Records an inbound provider event exactly once. Returns false when this event_key was seen before.
export async function recordEvent(db, { provider, eventKey, orderId, payload }) {
  const r = await db
    .prepare(
      "INSERT OR IGNORE INTO payment_events (provider, event_key, order_id, payload, received_at) VALUES (?, ?, ?, ?, ?)",
    )
    .bind(provider, eventKey, orderId, payload, nowIso())
    .run();
  return r.meta.changes === 1;
}

export async function setEventOutcome(db, eventKey, outcome) {
  await db.prepare("UPDATE payment_events SET outcome = ? WHERE event_key = ?").bind(outcome, eventKey).run();
}

// Applies a payment that was confirmed through the provider's server-side mechanism.
// Safe to call any number of times for the same order: only the first call can change it.
export async function applyConfirmedPayment(db, orderId, { amountAgorot, currency, documentId, transactionId }) {
  const order = await db.prepare("SELECT id, status, total_agorot, currency FROM orders WHERE id = ?").bind(orderId).first();
  if (!order) return "unknown_order";
  if (order.status === "paid") return "already_paid";

  const ts = nowIso();
  if (amountAgorot !== order.total_agorot || (currency && currency !== order.currency)) {
    await db
      .prepare(
        `UPDATE orders SET status = 'needs_review', status_reason = ?, provider_document_id = ?, provider_transaction_id = ?,
           updated_at = ? WHERE id = ? AND status != 'paid'`,
      )
      .bind(`amount_mismatch: got ${amountAgorot} ${currency || ""}`, documentId ?? null, transactionId ?? null, ts, orderId)
      .run();
    return "amount_mismatch";
  }

  const r = await db
    .prepare(
      `UPDATE orders SET status = 'paid', status_reason = NULL, provider_document_id = ?, provider_transaction_id = ?,
         paid_at = ?, updated_at = ? WHERE id = ? AND status != 'paid'`,
    )
    .bind(documentId ?? null, transactionId ?? null, ts, ts, orderId)
    .run();
  return r.meta.changes === 1 ? "paid" : "already_paid";
}

export async function markNeedsReview(db, orderId, reason) {
  await db
    .prepare("UPDATE orders SET status = 'needs_review', status_reason = ?, updated_at = ? WHERE id = ? AND status != 'paid'")
    .bind(reason, nowIso(), orderId)
    .run();
}

export function publicOrderView(order) {
  return {
    id: order.id,
    status: order.status,
    paymentMode: order.payment_mode,
    currency: order.currency,
    totalAgorot: order.total_agorot,
    createdAt: order.created_at,
    paidAt: order.paid_at,
    items: order.items.map((i) => ({
      productId: i.product_id,
      name: i.name,
      quantity: i.quantity,
      quantityLabel: i.quantity_label,
      unitPriceAgorot: i.unit_price_agorot,
      lineTotalAgorot: i.line_total_agorot,
    })),
  };
}
