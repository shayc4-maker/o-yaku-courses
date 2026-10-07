// Exercises the Worker's Morning code path against a FAKE Morning server on localhost.
// This proves our own logic (server-side pricing → form request, signed notifyUrl, duplicate
// events, read-back confirmation, amount mismatch). It does NOT prove Morning's real API shape —
// that needs the sandbox checklist in docs/MORNING.md.
// Run: node --test test/morning-flow.e2e.mjs   (starts its own wrangler dev on :8788)
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { spawn, execFileSync } from "node:child_process";
import { createHmac } from "node:crypto";

const FAKE_PORT = 9799, WORKER_PORT = 8788, SECRET = "test-notify-secret-0123456789abcdef";
const BASE = `http://127.0.0.1:${WORKER_PORT}`;
const PERSIST = ".wrangler/state-morning-test";
const forms = [];      // bodies Morning received
const documents = {};  // documentId → document returned by GET /documents/:id
let tokenCalls = 0;

const fake = http.createServer((req, res) => {
  let body = "";
  req.on("data", (c) => (body += c));
  req.on("end", () => {
    const send = (code, obj) => { res.writeHead(code, { "Content-Type": "application/json" }); res.end(JSON.stringify(obj)); };
    if (req.method === "POST" && req.url === "/account/token") { tokenCalls++; return send(200, { token: "fake-jwt" }); }
    if (req.headers.authorization !== "Bearer fake-jwt") return send(401, { errorCode: 401 });
    if (req.method === "POST" && req.url === "/payments/form") {
      forms.push(JSON.parse(body));
      return send(200, { errorCode: 0, url: `http://127.0.0.1:${FAKE_PORT}/hosted/${forms.length}` });
    }
    const m = req.url.match(/^\/documents\/(.+)$/);
    if (req.method === "GET" && m) return documents[m[1]] ? send(200, documents[m[1]]) : send(404, {});
    send(404, {});
  });
});

let worker;
before(async () => {
  await new Promise((ok) => fake.listen(FAKE_PORT, "127.0.0.1", ok));
  execFileSync("npx", ["wrangler", "d1", "migrations", "apply", "oyaku-founders-orders", "--local", "--persist-to", PERSIST], { stdio: "ignore" });
  const vars = {
    PAYMENT_MODE: "morning_sandbox", MORNING_API_BASE: `http://127.0.0.1:${FAKE_PORT}`, MORNING_AUTH_FLOW: "legacy",
    NOTIFY_SIGNING_SECRET: SECRET, MORNING_API_KEY_ID: "id", MORNING_API_KEY_SECRET: "secret",
  };
  worker = spawn("npx", ["wrangler", "dev", "--port", String(WORKER_PORT), "--ip", "127.0.0.1", "--persist-to", PERSIST,
    ...Object.entries(vars).flatMap(([k, v]) => ["--var", `${k}:${v}`])], { stdio: "ignore", env: { ...process.env, NO_PROXY: "127.0.0.1,localhost" } });
  for (let i = 0; i < 60; i++) {
    try { if ((await fetch(BASE + "/api/config")).ok) return; } catch {}
    await new Promise((ok) => setTimeout(ok, 500));
  }
  throw new Error("worker did not start");
});
after(() => { worker?.kill(); fake.close(); });

const customer = { name: "בדיקת מורנינג", phone: "050-1112222", email: "m@example.com" };
const checkout = async (items) => (await fetch(BASE + "/api/checkout", { method: "POST", headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ idempotencyKey: "m" + crypto.randomUUID().replace(/-/g, ""), customer, items }) })).json();
const sig = (id) => createHmac("sha256", SECRET).update(id).digest("hex");
const notify = (id, s, payload) => fetch(`${BASE}/api/morning/notify?order=${id}&sig=${s}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
const status = async (o) => (await (await fetch(`${BASE}/api/orders/${o.orderId}?t=${o.token}`)).json()).status;

test("payment form request is built from the server-side catalog", async () => {
  const o = await checkout([{ id: "tshirt", qty: 2, priceAgorot: 1 }, { id: "nursery-sqm-year", qty: 1 }]);
  assert.match(o.paymentUrl, /\/hosted\//);
  const f = forms.at(-1);
  assert.equal(f.amount, 1740);
  assert.equal(f.currency, "ILS");
  assert.deepEqual(f.income.map((i) => [i.quantity, i.price]), [[2, 120], [1, 1500]]);
  assert.equal(f.custom, o.orderId);
  assert.match(f.successUrl, /\/pay\/return\?order=.*result=success/);
  assert.match(f.notifyUrl, new RegExp(`/api/morning/notify\\?order=${o.orderId}&sig=${sig(o.orderId)}$`));
  assert.ok(!JSON.stringify(f).includes("4111"), "no card data anywhere");
});

test("notify with a bad signature is refused and changes nothing", async () => {
  const o = await checkout([{ id: "tshirt", qty: 1 }]);
  const r = await notify(o.orderId, "0".repeat(64), { documentId: "doc-forged-0001" });
  assert.equal(r.status, 403);
  assert.equal(await status(o), "awaiting_payment");
});

test("notify → document read back → paid; redelivery is a no-op", async () => {
  const o = await checkout([{ id: "custom-pot", qty: 1 }]);
  documents["doc-ok-000001"] = { id: "doc-ok-000001", amount: 1200, currency: "ILS", remarks: `הזמנה ${o.orderId}` };
  const r1 = await notify(o.orderId, sig(o.orderId), { documentId: "doc-ok-000001" });
  assert.equal(r1.status, 200);
  assert.equal(await status(o), "paid");
  const r2 = await (await notify(o.orderId, sig(o.orderId), { documentId: "doc-ok-000001" })).json();
  assert.equal(r2.duplicate, true);
  assert.equal(await status(o), "paid");
});

test("notify whose document amount differs → needs_review, not paid", async () => {
  const o = await checkout([{ id: "akadama-10", qty: 2 }]);
  documents["doc-low-00001"] = { id: "doc-low-00001", amount: 1400, currency: "ILS", remarks: `הזמנה ${o.orderId}` };
  await notify(o.orderId, sig(o.orderId), { documentId: "doc-low-00001" });
  assert.equal(await status(o), "needs_review");
});

test("notify pointing at another order's document → needs_review", async () => {
  const a = await checkout([{ id: "tshirt", qty: 1 }]);
  const b = await checkout([{ id: "tshirt", qty: 1 }]);
  documents["doc-a-0000001"] = { id: "doc-a-0000001", amount: 120, currency: "ILS", remarks: `הזמנה ${a.orderId}` };
  await notify(b.orderId, sig(b.orderId), { documentId: "doc-a-0000001" });
  assert.equal(await status(b), "needs_review");
});

test("notify without a usable document id → needs_review (never paid on the payload's word)", async () => {
  const o = await checkout([{ id: "tshirt", qty: 1 }]);
  await notify(o.orderId, sig(o.orderId), { status: "success", amount: 120 });
  assert.equal(await status(o), "needs_review");
});

test("token is reused across requests", () => {
  assert.equal(tokenCalls, 1);
});
