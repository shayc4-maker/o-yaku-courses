// API checks against a running local Worker (npm run dev). BASE defaults to http://127.0.0.1:8787.
// Run with: node --test test/api.e2e.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";

const BASE = process.env.BASE || "http://127.0.0.1:8787";
const customer = { name: "בדיקה אוטומטית", phone: "050-1234567", email: "test@example.com" };
const key = () => "k" + crypto.randomUUID().replace(/-/g, "");

async function post(path, body, opts = {}) {
  const res = await fetch(BASE + path, {
    method: "POST",
    headers: { "Content-Type": opts.form ? "application/x-www-form-urlencoded" : "application/json" },
    body: opts.form ? new URLSearchParams(body) : JSON.stringify(body),
    redirect: "manual",
  });
  const text = await res.text();
  let data = null;
  try { data = JSON.parse(text); } catch {}
  return { status: res.status, data, text, location: res.headers.get("location") };
}
const getOrder = async (id, t) => (await fetch(`${BASE}/api/orders/${id}?t=${t}`)).json();

function sql(query) {
  return JSON.parse(execFileSync("npx", ["wrangler", "d1", "execute", "oyaku-founders-orders", "--local", "--json", "--command", query], { encoding: "utf8" }))[0].results;
}

test("server recomputes prices and ignores client-sent amounts", async () => {
  const r = await post("/api/checkout", {
    idempotencyKey: key(),
    customer,
    items: [{ id: "custom-pot", qty: 2, priceAgorot: 100, lineTotalAgorot: 100 }, { id: "tshirt", qty: 1, priceAgorot: 1 }],
    totalAgorot: 200,
    total: 2,
  });
  assert.equal(r.status, 200);
  const o = await getOrder(r.data.orderId, r.data.token);
  assert.equal(o.totalAgorot, 252000); // 2 × 1,200 + 120
  assert.deepEqual(o.items.map((i) => i.unitPriceAgorot), [120000, 12000]);
});

test("invalid quantities and products are rejected", async () => {
  for (const items of [
    [{ id: "tshirt", qty: 0 }], [{ id: "tshirt", qty: -1 }], [{ id: "tshirt", qty: 1.5 }],
    [{ id: "tshirt", qty: "2" + "0".repeat(3) }], [{ id: "tshirt", qty: "abc" }], [{ id: "bonsai-lesson", qty: 1 }], [],
  ]) {
    const r = await post("/api/checkout", { idempotencyKey: key(), customer, items });
    assert.equal(r.status, 400, JSON.stringify(items));
  }
  const bad = await post("/api/checkout", { idempotencyKey: key(), customer: { ...customer, email: "x" }, items: [{ id: "tshirt", qty: 1 }] });
  assert.equal(bad.status, 400);
  assert.equal(bad.data.error, "invalid_customer");
});

test("double submit with the same idempotency key returns one order and one payment page", async () => {
  const k = key();
  const body = { idempotencyKey: k, customer, items: [{ id: "ceramics-group", qty: 4 }] };
  const results = await Promise.all([post("/api/checkout", body), post("/api/checkout", body), post("/api/checkout", body)]);
  const ids = new Set(results.filter((r) => r.status === 200).map((r) => r.data.orderId));
  assert.equal(ids.size, 1);
  for (const r of results) assert.ok([200, 202].includes(r.status));
  const rows = sql(`SELECT COUNT(*) AS n FROM orders WHERE idempotency_key = '${k}'`);
  assert.equal(rows[0].n, 1);
  const again = await post("/api/checkout", body);
  assert.equal(again.data.orderId, [...ids][0]);
  assert.equal(again.data.paymentUrl, results.find((r) => r.status === 200).data.paymentUrl);
  // Same key, different cart → conflict instead of silently reusing the old order.
  const changed = await post("/api/checkout", { ...body, items: [{ id: "ceramics-group", qty: 5 }] });
  assert.equal(changed.status, 409);
});

test("return to success URL alone does not mark an order paid", async () => {
  const r = await post("/api/checkout", { idempotencyKey: key(), customer, items: [{ id: "tshirt", qty: 1 }] });
  const ret = await fetch(`${BASE}/pay/return?order=${r.data.orderId}&t=${r.data.token}&result=success`, { redirect: "manual" });
  assert.equal(ret.status, 303);
  assert.equal((await getOrder(r.data.orderId, r.data.token)).status, "awaiting_payment");
});

test("mock: cancel → cancelled; retry creates a new order; success → paid once even when submitted twice", async () => {
  const items = [{ id: "akadama-10", qty: 2 }, { id: "nursery-sqm-year", qty: 1 }];
  const first = await post("/api/checkout", { idempotencyKey: key(), customer, items });
  const cancel = await post("/pay/mock", { order: first.data.orderId, t: first.data.token, outcome: "cancel" }, { form: true });
  assert.equal(cancel.status, 303);
  await fetch(BASE + cancel.location, { redirect: "manual" });
  assert.equal((await getOrder(first.data.orderId, first.data.token)).status, "cancelled");

  const failed = await post("/pay/mock", { order: first.data.orderId, t: first.data.token, outcome: "failure" }, { form: true });
  assert.equal(failed.status, 303); // a closed order cannot be re-opened by another failure

  const retry = await post("/api/checkout", { idempotencyKey: key(), customer, items });
  assert.notEqual(retry.data.orderId, first.data.orderId);
  const ok1 = await post("/pay/mock", { order: retry.data.orderId, t: retry.data.token, outcome: "success" }, { form: true });
  const ok2 = await post("/pay/mock", { order: retry.data.orderId, t: retry.data.token, outcome: "success" }, { form: true });
  assert.equal(ok1.status, 303);
  assert.equal(ok2.status, 303);
  const o = await getOrder(retry.data.orderId, retry.data.token);
  assert.equal(o.status, "paid");
  assert.equal(o.totalAgorot, 430000); // 2 × 1,400 + 1,500
  const ev = sql(`SELECT COUNT(*) AS n FROM payment_events WHERE order_id = '${retry.data.orderId}'`);
  assert.equal(ev[0].n, 1);

  // A failure/cancel arriving after payment does not undo it.
  await fetch(`${BASE}/pay/return?order=${retry.data.orderId}&t=${retry.data.token}&result=failure`, { redirect: "manual" });
  assert.equal((await getOrder(retry.data.orderId, retry.data.token)).status, "paid");
});

test("order status requires the order's token", async () => {
  const r = await post("/api/checkout", { idempotencyKey: key(), customer, items: [{ id: "tshirt", qty: 1 }] });
  const wrong = await fetch(`${BASE}/api/orders/${r.data.orderId}?t=${"0".repeat(48)}`);
  assert.equal(wrong.status, 404);
  const mock = await post("/pay/mock", { order: r.data.orderId, t: "0".repeat(48), outcome: "success" }, { form: true });
  assert.equal(mock.status, 404);
});

test("Morning notify endpoint is closed in mock mode", async () => {
  const r = await post("/api/morning/notify?order=OY-23456789&sig=x", { any: 1 });
  assert.equal(r.status, 404);
});

test("pages carry noindex", async () => {
  for (const p of ["/", "/order", "/api/config"]) {
    const res = await fetch(BASE + p);
    assert.match(res.headers.get("x-robots-tag") || "", /noindex/, p);
  }
  const html = await (await fetch(BASE + "/")).text();
  assert.match(html, /<meta name="robots" content="noindex/);
});
