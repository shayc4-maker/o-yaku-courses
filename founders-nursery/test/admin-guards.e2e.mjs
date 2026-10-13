// Admin guards that need their own Worker configuration:
//   1. no Access configuration → every admin path blocked (503), public site unaffected
//   2. real clock (no TEST_NOW) → redemption refused before January 2027
// Run: node --test test/admin-guards.e2e.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { rmSync } from "node:fs";
import { makeKey, signToken, startJwks, claimsFor, startWorker, migrateWithLegacy, adminClient, key, tfetch } from "./helpers/admin-env.mjs";
import { TERMS_VERSION } from "../public/purchase-policy.js";

test("missing Access configuration blocks the whole admin area; public site and Morning notify path stay reachable", async (t) => {
  const persist = ".wrangler/state-admin-guard-a";
  migrateWithLegacy(persist, "");
  const signer = makeKey();
  const jwks = await startJwks([signer], 9821);
  for (const missing of ["ACCESS_TEAM_DOMAIN", "ACCESS_AUD", "ADMIN_EMAILS"]) {
    const { child, base, team } = await startWorker({ port: 8796, jwksPort: 9821, persist, vars: { [missing]: "" } });
    try {
      const c = adminClient(base, signToken(signer, claimsFor(team)));
      for (const p of ["/admin", "/admin/admin.js", "/api/admin/me", "/api/admin/export/orders.csv"]) {
        assert.equal((await c.get(p)).status, 503, `${missing} empty → ${p}`);
      }
      assert.equal((await c.post("/api/admin/orders/OY-AAAAAAA2/notes", { kind: "note", value: "x" })).status, 503);
      assert.equal((await tfetch(base + "/")).status, 200);
      assert.equal((await tfetch(base + "/api/config")).status, 200);
      // Notify path is not behind Access (it answers 404 only because PAYMENT_MODE is mock here).
      assert.notEqual((await tfetch(base + "/api/morning/notify?order=OY-AAAAAAA2&sig=x", { method: "POST", body: "{}" })).status, 503);
    } finally {
      child.stop();
      await new Promise((ok) => setTimeout(ok, 800));
    }
  }
  jwks.close();
  rmSync(persist, { recursive: true, force: true });
});

test("with the real clock (2026) redemption is refused: it starts in January 2027", async () => {
  const persist = ".wrangler/state-admin-guard-b";
  migrateWithLegacy(persist, "");
  const signer = makeKey();
  const jwks = await startJwks([signer], 9822);
  const { child, base, team } = await startWorker({ port: 8797, jwksPort: 9822, persist });
  try {
    const checkout = await (await tfetch(base + "/api/checkout", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idempotencyKey: key(), termsAccepted: true, termsVersion: TERMS_VERSION,
        customer: { name: "בדיקת שעון", phone: "050-1231234", email: "clock@example.com" }, items: [{ id: "akadama-10", qty: 1 }] }) })).json();
    await tfetch(base + "/pay/mock", { method: "POST", body: new URLSearchParams({ order: checkout.orderId, t: checkout.token, outcome: "success" }), redirect: "manual" });
    const c = adminClient(base, signToken(signer, claimsFor(team)));
    const o = await c.get(`/api/admin/orders/${checkout.orderId}`);
    assert.equal(o.data.status, "paid");
    assert.equal(o.data.lines[0].units, 10, "new checkout snapshots 10 bags per pack");
    assert.ok(o.data.buyerId, "new checkout is linked to a buyer");
    const today = new Date().toISOString().slice(0, 10);
    const r = await c.post(`/api/admin/orders/${checkout.orderId}/redemptions`, { idempotencyKey: key(), productId: "akadama-10", quantity: 1, date: today });
    assert.equal(r.status, 409);
    assert.equal(r.data.error, "redemption_not_started");
  } finally {
    child.stop();
    jwks.close();
    rmSync(persist, { recursive: true, force: true });
  }
});
