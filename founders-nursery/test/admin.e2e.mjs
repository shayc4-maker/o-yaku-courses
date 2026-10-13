// Admin area end-to-end tests. Starts its own Worker (port 8791) with a private local D1 and a
// local JWKS endpoint holding a throwaway test key. Never touches the real account.
// Run: node --test test/admin.e2e.mjs
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { rmSync } from "node:fs";
import {
  AUD, OWNER, makeKey, signToken, startJwks, claimsFor, startWorker, migrateWithLegacy, adminClient, key, tfetch,
} from "./helpers/admin-env.mjs";
import { legacyOrder, AKADAMA, SHIRT, SQM, LESSON, GROUP } from "./helpers/fixtures.mjs";

const JWKS_PORT = 9811, PORT = 8791, PERSIST = ".wrangler/state-admin-test";
const NOW = "2027-03-01T10:00:00Z"; // test clock: inside the redemption period
let jwks, worker, base, team, signer, owner, db;

const ids = {
  dana1: "OY-AAAAAAA2", dana2: "OY-AAAAAAA3", expired: "OY-AAAAAAA4", pending: "OY-AAAAAAA5", mock: "OY-AAAAAAA6",
  sandbox: "OY-AAAAAAA7", formula: "OY-AAAAAAA8", multi: "OY-AAAAAAA9", unpaidLive: "OY-AAAAAAAB",
};

before(async () => {
  signer = makeKey("kid-good");
  jwks = await startJwks([signer], JWKS_PORT);
  // 57 more live buyers for paging and search (alphabet excludes 0/1/I/O like real order ids).
  const alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ";
  const bulk = Array.from({ length: 57 }, (_, n) => legacyOrder({
    id: `OY-BBBB${alphabet[Math.floor(n / 32)]}${alphabet[n % 32]}CD`,
    name: `קונה ${n}`, email: `buyer${n}@example.com`, phone: `052-55500${String(n).padStart(2, "0")}`,
    paidAt: new Date(Date.UTC(2026, 9, 21, 8, n)).toISOString(), items: [SHIRT(1 + (n % 3))],
  }));
  db = migrateWithLegacy(PERSIST, [
    legacyOrder({ id: ids.dana1, name: "דנה לוי", email: " Dana@Example.com ", phone: "050-1111111", items: [AKADAMA(1), SHIRT(2)] }),
    legacyOrder({ id: ids.dana2, name: "דנה כהן-לוי", email: "dana@example.com", phone: "054-2222222", paidAt: "2026-10-22T09:00:00.000Z", items: [SQM(1)] }),
    legacyOrder({ id: ids.expired, name: "יוסי ותיק", email: "yossi@example.com", phone: "050-3333333", paidAt: "2024-06-01T09:00:00.000Z", items: [SQM(2)] }),
    legacyOrder({ id: ids.pending, name: "ממתין", email: "pending@example.com", phone: "050-4444444", status: "awaiting_payment", paidAt: null, createdAt: "2026-10-23T09:00:00.000Z", items: [SHIRT(1)] }),
    legacyOrder({ id: ids.mock, mode: "mock", name: "בדיקת הדמיה", email: "mock@example.com", phone: "050-5555555", items: [AKADAMA(2)] }),
    legacyOrder({ id: ids.sandbox, mode: "morning_sandbox", name: "בדיקת סנדבוקס", email: "sandbox@example.com", phone: "050-6666666", items: [SHIRT(1)] }),
    legacyOrder({ id: ids.formula, name: '=HYPERLINK("http://evil","x")', email: "formula@example.com", phone: "050-1111111", items: [SHIRT(1)] }),
    legacyOrder({ id: ids.multi, name: "רב מוצרים", email: "multi@example.com", phone: "050-7777777", items: [LESSON(2), GROUP(4), AKADAMA(2)] }),
    legacyOrder({ id: ids.unpaidLive, name: "לא שולם", email: "unpaid@example.com", phone: "050-8888888", status: "cancelled", paidAt: null, createdAt: "2026-10-23T10:00:00.000Z", items: [AKADAMA(1)] }),
    ...bulk,
  ].join("\n"));
  ({ child: worker, base, team } = await startWorker({ port: PORT, jwksPort: JWKS_PORT, persist: PERSIST, vars: { TEST_NOW: NOW } }));
  owner = adminClient(base, signToken(signer, claimsFor(team)));
});
after(() => { worker?.stop(); jwks?.close(); rmSync(PERSIST, { recursive: true, force: true }); });

// ------------------------------------------------------------------------------------- authorization

test("every admin path refuses requests without a valid Access token — before any data", async () => {
  const anon = adminClient(base, null);
  for (const p of ["/admin", "/admin/", "/admin/admin.js", "/admin/admin.css", "/admin/index.html", "/admin/anything",
    "/api/admin/me", "/api/admin/orders", `/api/admin/orders/${ids.dana1}`, "/api/admin/buyers", "/api/admin/products",
    "/api/admin/export/orders.csv", "/api/admin/export/buyers.csv", "/api/admin/export/balances.csv"]) {
    const r = await anon.get(p);
    assert.equal(r.status, 401, p);
    assert.ok(!r.text.includes("דנה"), `${p} leaks data`);
    assert.equal(r.headers.get("cache-control"), "no-store", p);
  }
  const w = await anon.post(`/api/admin/orders/${ids.dana1}/redemptions`, { idempotencyKey: key(), productId: "tshirt", quantity: 1, date: "2027-02-01" });
  assert.equal(w.status, 401);
  // An email header alone is not identity.
  const spoof = await fetch(base + "/api/admin/me", { headers: { "Cf-Access-Authenticated-User-Email": OWNER } });
  assert.equal(spoof.status, 401);
});

test("tokens with bad signature, expiry, audience, issuer, algorithm or email are rejected", async () => {
  const other = makeKey("kid-good"); // same kid, different key → signature mismatch
  const now = Math.floor(Date.now() / 1000);
  const cases = {
    signature: signToken(other, claimsFor(team)),
    unknown_kid: signToken(makeKey("kid-unknown"), claimsFor(team)),
    expired: signToken(signer, claimsFor(team, { exp: now - 600 })),
    future: signToken(signer, claimsFor(team, { nbf: now + 3600, iat: now + 3600 })),
    audience: signToken(signer, claimsFor(team, { aud: ["someone-else"] })),
    issuer: signToken(signer, claimsFor(team, { iss: "https://evil.cloudflareaccess.com" })),
    not_owner: signToken(signer, claimsFor(team, { email: "intruder@example.com" })),
    no_email: signToken(signer, claimsFor(team, { email: undefined })),
    alg_none: (() => { const [, p] = signToken(signer, claimsFor(team)).split("."); return `${Buffer.from('{"alg":"none","kid":"kid-good"}').toString("base64url")}.${p}.`; })(),
    garbage: "not.a.jwt",
    tampered: (() => { const [h, , s] = signToken(signer, claimsFor(team)).split("."); return `${h}.${Buffer.from(JSON.stringify(claimsFor(team, { email: OWNER, aud: [AUD], exp: now + 99999 }))).toString("base64url")}.${s}`; })(),
  };
  for (const [name, t] of Object.entries(cases)) {
    const r = await adminClient(base, t).get("/api/admin/me");
    assert.equal(r.status, 403, name);
  }
  // Owner match is case-insensitive on the token side; cookie transport works as well as the header.
  const ok = await adminClient(base, signToken(signer, claimsFor(team, { email: "Owner@Example.com" }))).get("/api/admin/me");
  assert.equal(ok.status, 200);
  const cookie = await fetch(base + "/api/admin/me", { headers: { Cookie: `x=1; CF_Authorization=${signToken(signer, claimsFor(team))}` } });
  assert.equal(cookie.status, 200);
  assert.equal((await cookie.json()).email, OWNER);
});

test("admin UI is served only after authentication, with no-store", async () => {
  const r = await owner.get("/admin");
  assert.equal(r.status, 200);
  assert.match(r.text, /ניהול/);
  assert.equal(r.headers.get("cache-control"), "no-store");
  assert.equal((await owner.get("/admin/admin.js")).status, 200);
  assert.equal((await owner.get("/admin/nope.js")).status, 404);
});

test("writes require same-origin JSON with the admin header (CSRF)", async () => {
  const body = { idempotencyKey: key(), productId: "tshirt", quantity: 1, date: "2027-02-01" };
  const path = `/api/admin/orders/${ids.dana1}/redemptions`;
  const t = signToken(signer, claimsFor(team));
  const send = (headers, b = JSON.stringify(body)) => fetch(base + path, { method: "POST", headers: { "Cf-Access-Jwt-Assertion": t, ...headers }, body: b });
  assert.equal((await send({ "Content-Type": "application/json", "X-OY-Admin": "1" })).status, 403, "no origin");
  assert.equal((await send({ "Content-Type": "application/json", "X-OY-Admin": "1", Origin: "https://evil.example" })).status, 403, "foreign origin");
  assert.equal((await send({ "Content-Type": "application/json", Origin: base })).status, 403, "no custom header");
  assert.equal((await send({ "Content-Type": "application/json", "X-OY-Admin": "1", Origin: base, "Sec-Fetch-Site": "cross-site" })).status, 403, "cross-site fetch");
  assert.equal((await send({ "Content-Type": "text/plain", "X-OY-Admin": "1", Origin: base })).status, 415, "form-like content type");
  const viaGet = await fetch(base + path, { headers: { "Cf-Access-Jwt-Assertion": t } });
  assert.equal(viaGet.status, 404);
  const put = await fetch(base + path, { method: "PUT", headers: { "Cf-Access-Jwt-Assertion": t } });
  assert.equal(put.status, 405);
  const rows = db.sql(`SELECT COUNT(*) AS n FROM redemptions WHERE order_id = '${ids.dana1}'`);
  assert.equal(rows[0].n, 0, "nothing written by rejected requests");
});

test("there is no way to mark an order paid from the admin API", async () => {
  for (const p of ["mark-paid", "pay", "status"]) {
    assert.equal((await owner.post(`/api/admin/orders/${ids.pending}/${p}`, { status: "paid" })).status, 404);
  }
  const r = await owner.post(`/api/admin/orders/${ids.pending}/redemptions`, { idempotencyKey: key(), productId: "tshirt", quantity: 1, date: "2027-02-01" });
  assert.equal(r.status, 409);
  assert.equal(r.data.error, "order_not_paid");
});

// ------------------------------------------------------------------------------------- buyers / backfill

test("migration backfilled buyers by normalized email and kept original order details", async () => {
  const rows = db.sql(`SELECT id, buyer_id, customer_email, customer_name FROM orders WHERE id IN ('${ids.dana1}', '${ids.dana2}')`);
  assert.equal(rows.length, 2);
  assert.equal(rows[0].buyer_id, rows[1].buyer_id, "same buyer for ' Dana@Example.com ' and 'dana@example.com'");
  assert.ok(rows.some((r) => r.customer_email === " Dana@Example.com "), "original email kept on the order");
  const units = db.sql(`SELECT product_id, redeem_units, redeem_unit_label FROM order_items WHERE order_id = '${ids.dana1}' ORDER BY product_id`);
  assert.deepEqual(units.map((u) => [u.product_id, u.redeem_units, u.redeem_unit_label]), [["akadama-10", 10, "שקים"], ["tshirt", 2, "חולצות"]]);

  const b = await owner.get(`/api/admin/buyers/${rows[0].buyer_id}`);
  assert.equal(b.status, 200);
  assert.equal(b.data.email, "dana@example.com");
  assert.equal(b.data.orders.length, 2);
  assert.equal(b.data.detailVariants.length, 2, "different names/phones are reported, not merged");
  assert.ok(b.data.samePhoneOtherBuyers.some((x) => x.email === "formula@example.com"), "same phone flagged, not merged");
  assert.equal(b.data.paidLiveAgorot, 140000 + 24000 + 150000);
  // Legacy order without any admin data opens fine.
  const o = await owner.get(`/api/admin/orders/${ids.dana2}`);
  assert.equal(o.status, 200);
  assert.deepEqual(o.data.redemptions, []);
  assert.deepEqual(o.data.coordination, []);
});

test("buyer search by name, phone digits and email; server-side paging", async () => {
  const byName = await owner.get(`/api/admin/buyers?q=${encodeURIComponent("דנה")}`);
  assert.equal(byName.data.total, 1);
  const byPhone = await owner.get("/api/admin/buyers?q=0541222222".replace("0541", "054"));
  assert.equal(byPhone.data.buyers[0].email, "dana@example.com");
  const byPhoneDashed = await owner.get("/api/admin/buyers?q=" + encodeURIComponent("050-111"));
  assert.ok(byPhoneDashed.data.total >= 2);
  const byEmail = await owner.get("/api/admin/buyers?q=YOSSI@example");
  assert.equal(byEmail.data.total, 1);
  const p1 = await owner.get("/api/admin/buyers?pageSize=20&page=1");
  const p4 = await owner.get("/api/admin/buyers?pageSize=20&page=4");
  assert.equal(p1.data.buyers.length, 20);
  assert.ok(p1.data.total >= 60);
  assert.equal(p4.data.buyers.length, p1.data.total - 60);
  const wildcard = await owner.get("/api/admin/buyers?q=%25");
  assert.equal(wildcard.data.total, 0, "LIKE wildcards are escaped");
});

test("order filters, sorting and paging run on the server", async () => {
  const all = await owner.get("/api/admin/orders?pageSize=100");
  assert.ok(all.data.orders.every((o) => o.paymentMode === "morning_live"), "live scope has live orders only");
  const page2 = await owner.get("/api/admin/orders?pageSize=10&page=2&sort=id&dir=asc");
  assert.equal(page2.data.orders.length, 10);
  assert.equal(page2.data.total, all.data.total);
  const ids2 = page2.data.orders.map((o) => o.id);
  assert.deepEqual(ids2, [...ids2].sort());
  const akadama = await owner.get("/api/admin/orders?product=akadama-10");
  assert.deepEqual(akadama.data.orders.map((o) => o.id).sort(), [ids.dana1, ids.multi, ids.unpaidLive].sort());
  const paidAkadama = await owner.get("/api/admin/orders?product=akadama-10&payment=paid");
  assert.equal(paidAkadama.data.total, 2);
  const expired = await owner.get("/api/admin/orders?redemption=expired");
  assert.deepEqual(expired.data.orders.map((o) => o.id), [ids.expired]);
  const dated = await owner.get("/api/admin/orders?from=2026-10-23&to=2026-10-23");
  assert.deepEqual(dated.data.orders.map((o) => o.id).sort(), [ids.pending, ids.unpaidLive].sort());
  const bigTotal = await owner.get("/api/admin/orders?sort=total&dir=desc&pageSize=1");
  assert.equal(bigTotal.data.orders[0].id, ids.multi);
  assert.equal((await owner.get("/api/admin/orders?sort=drop_table")).status, 400);
  assert.equal((await owner.get("/api/admin/orders?scope=everything")).status, 400);
});

// ------------------------------------------------------------------------------------- redemption

const redeem = (orderId, productId, quantity, extra = {}) =>
  owner.post(`/api/admin/orders/${orderId}/redemptions`, { idempotencyKey: key(), productId, quantity, date: "2027-02-15", ...extra });
const publicView = async (orderId) => {
  const [row] = db.sql(`SELECT access_token FROM orders WHERE id = '${orderId}'`);
  const res = await tfetch(`${base}/api/orders/${orderId}?t=${row.access_token}`);
  return { text: await res.clone().text(), data: await res.json() };
};

test("akadama: 1 pack = 10 bags; partial redemption of 4 leaves 6, visible on the public voucher", async () => {
  const r = await redeem(ids.dana1, "akadama-10", 4, { note: "איסוף 4 שקים — הערה פנימית" });
  assert.equal(r.status, 201);
  const o = await owner.get(`/api/admin/orders/${ids.dana1}`);
  const line = o.data.lines.find((l) => l.productId === "akadama-10");
  assert.deepEqual([line.units, line.redeemed, line.remaining, line.unitLabel, line.state], [10, 4, 6, "שקים", "partial"]);
  assert.equal(o.data.voucher.state, "partial");
  const pub = await publicView(ids.dana1);
  const pl = pub.data.items.find((i) => i.productId === "akadama-10");
  assert.deepEqual([pl.redeemUnits, pl.redeemedUnits, pl.remainingUnits, pl.state], [10, 4, 6, "partial"]);
  assert.ok(!pub.text.includes("הערה פנימית") && !pub.text.includes(OWNER), "no internal notes or admin identity in the customer view");
  assert.equal(pub.data.status, "paid", "payment status is unchanged by redemption");
});

test("cannot redeem more than was paid for, fractions, or zero", async () => {
  assert.equal((await redeem(ids.dana1, "akadama-10", 7)).data.error, "insufficient_balance");
  for (const q of [0, -1, 1.5, "2", null]) assert.equal((await redeem(ids.dana1, "akadama-10", q)).status, 400, String(q));
  assert.equal((await redeem(ids.dana1, "ceramics-private", 1)).data.error, "invalid_product");
});

test("two concurrent redemptions on the same balance: exactly one succeeds", async () => {
  // multi order: 2 packs = 20 bags. Fire 2 × 15 at once, then 12 × 1 against the rest.
  const [a, b] = await Promise.all([redeem(ids.multi, "akadama-10", 15), redeem(ids.multi, "akadama-10", 15)]);
  assert.deepEqual([a.status, b.status].sort(), [201, 409]);
  const burst = await Promise.all(Array.from({ length: 12 }, () => redeem(ids.multi, "akadama-10", 1)));
  assert.equal(burst.filter((r) => r.status === 201).length, 5);
  assert.ok(burst.filter((r) => r.status !== 201).every((r) => r.data.error === "insufficient_balance"));
  const [sum] = db.sql(`SELECT SUM(quantity) AS n FROM redemptions WHERE order_id = '${ids.multi}' AND product_id = 'akadama-10'`);
  assert.equal(sum.n, 20);
  const o = await owner.get(`/api/admin/orders/${ids.multi}`);
  assert.equal(o.data.lines.find((l) => l.productId === "akadama-10").state, "full");
});

test("same idempotency key twice records once; same key with a different body is a conflict", async () => {
  const k = key();
  const body = { idempotencyKey: k, productId: "bonsai-private-lesson", quantity: 1, date: "2027-02-10" };
  const [r1, r2] = await Promise.all([
    owner.post(`/api/admin/orders/${ids.multi}/redemptions`, body),
    owner.post(`/api/admin/orders/${ids.multi}/redemptions`, body),
  ]);
  assert.deepEqual([r1.status, r2.status].sort(), [200, 201]);
  assert.equal(r1.data.redemption.id, r2.data.redemption.id);
  const r3 = await owner.post(`/api/admin/orders/${ids.multi}/redemptions`, body);
  assert.equal(r3.data.replayed, true);
  const [c] = db.sql(`SELECT COUNT(*) AS n FROM redemptions WHERE idempotency_key = '${k}'`);
  assert.equal(c.n, 1);
  const conflict = await owner.post(`/api/admin/orders/${ids.multi}/redemptions`, { ...body, quantity: 2 });
  assert.equal(conflict.status, 409);
  assert.equal(conflict.data.error, "idempotency_conflict");
  const o = await owner.get(`/api/admin/orders/${ids.multi}`);
  assert.equal(o.data.lines.find((l) => l.productId === "bonsai-private-lesson").remaining, 1);
});

test("a correction is a linked, reasoned ledger entry — history is kept", async () => {
  const r = await redeem(ids.multi, "ceramics-group", 3);
  const rid = r.data.redemption.id;
  assert.equal((await owner.post(`/api/admin/redemptions/${rid}/corrections`, { idempotencyKey: key(), quantity: 1 })).data.error, "reason_required");
  const c = await owner.post(`/api/admin/redemptions/${rid}/corrections`, { idempotencyKey: key(), quantity: 2, reason: "נרשם בטעות 3 במקום 1" });
  assert.equal(c.status, 201);
  const over = await owner.post(`/api/admin/redemptions/${rid}/corrections`, { idempotencyKey: key(), quantity: 2, reason: "שוב" });
  assert.equal(over.data.error, "correction_exceeds_redemption");
  const corrOfCorr = await owner.post(`/api/admin/redemptions/${c.data.redemption.id}/corrections`, { idempotencyKey: key(), quantity: 1, reason: "x y z" });
  assert.equal(corrOfCorr.data.error, "not_a_redemption");
  const o = await owner.get(`/api/admin/orders/${ids.multi}`);
  const line = o.data.lines.find((l) => l.productId === "ceramics-group");
  assert.deepEqual([line.redeemed, line.remaining], [1, 3]);
  const rows = o.data.redemptions.filter((x) => x.productId === "ceramics-group");
  assert.equal(rows.length, 2);
  assert.equal(rows[1].correctsId, rid);
  assert.equal(rows[1].by, OWNER);
  assert.ok(o.data.history.some((h) => h.type === "correction" && h.reason === "נרשם בטעות 3 במקום 1"));
});

test("dates: not before January 2027, not in the future, not after expiry; expired vouchers are closed", async () => {
  assert.equal((await redeem(ids.dana2, "nursery-sqm-year", 1, { date: "2026-12-31" })).data.error, "date_before_redemption_start");
  assert.equal((await redeem(ids.dana2, "nursery-sqm-year", 1, { date: "2027-03-02" })).data.error, "date_in_future");
  assert.equal((await redeem(ids.dana2, "nursery-sqm-year", 1, { date: "2027-02-30" })).data.error, "invalid_date");
  const exp = await redeem(ids.expired, "nursery-sqm-year", 1, { date: "2027-01-05" });
  assert.equal(exp.data.error, "voucher_expired");
  const pub = await publicView(ids.expired);
  assert.equal(pub.data.voucher.state, "expired");
  assert.equal(pub.data.items[0].remainingUnits, 0);
});

test("voucher cancellation blocks redemption only; payment status stays paid", async () => {
  assert.equal((await owner.post(`/api/admin/orders/${ids.dana2}/cancel-voucher`, { reason: "בקשת לקוח", confirm: false })).data.error, "confirm_required");
  assert.equal((await owner.post(`/api/admin/orders/${ids.dana2}/cancel-voucher`, { confirm: true })).data.error, "reason_required");
  const c = await owner.post(`/api/admin/orders/${ids.dana2}/cancel-voucher`, { reason: "בקשת לקוח — טיפול בהחזר בנפרד", confirm: true });
  assert.equal(c.status, 200);
  const again = await owner.post(`/api/admin/orders/${ids.dana2}/cancel-voucher`, { reason: "שוב", confirm: true });
  assert.equal(again.data.alreadyCancelled, true);
  assert.equal((await redeem(ids.dana2, "nursery-sqm-year", 1)).data.error, "voucher_cancelled");
  const o = await owner.get(`/api/admin/orders/${ids.dana2}`);
  assert.equal(o.data.status, "paid");
  assert.equal(o.data.voucher.state, "cancelled");
  assert.equal(o.data.history.filter((h) => h.type === "voucher_cancelled").length, 1);
  const pub = await publicView(ids.dana2);
  assert.equal(pub.data.status, "paid");
  assert.equal(pub.data.voucher.state, "cancelled");
  assert.equal(pub.data.items[0].remainingUnits, 0, "no full entitlement shown after cancellation");
  assert.ok(!pub.text.includes("טיפול בהחזר"), "cancel reason is internal");
});

test("coordination notes are internal and never change redeemed quantities", async () => {
  const before = (await owner.get(`/api/admin/orders/${ids.dana1}`)).data.lines.map((l) => l.redeemed);
  assert.equal((await owner.post(`/api/admin/orders/${ids.dana1}/notes`, { kind: "shirt_size", productId: "tshirt", value: "M ו־L" })).status, 201);
  assert.equal((await owner.post(`/api/admin/orders/${ids.dana1}/notes`, { kind: "note", value: "מעדיפה איסוף בבוקר" })).status, 201);
  assert.equal((await owner.post(`/api/admin/orders/${ids.dana2}/notes`, { kind: "trees_in", productId: "nursery-sqm-year", value: "2027-01-10" })).status, 201);
  assert.equal((await owner.post(`/api/admin/orders/${ids.dana2}/notes`, { kind: "service_end", productId: "nursery-sqm-year", value: "2028-01-09" })).status, 201);
  assert.equal((await owner.post(`/api/admin/orders/${ids.dana1}/notes`, { kind: "trees_in", value: "next week" })).data.error, "invalid_date");
  assert.equal((await owner.post(`/api/admin/orders/${ids.dana1}/notes`, { kind: "evil", value: "x" })).data.error, "invalid_kind");
  assert.equal((await owner.post(`/api/admin/orders/${ids.dana1}/notes`, { kind: "note", productId: "custom-pot", value: "x" })).data.error, "invalid_product");
  const o = await owner.get(`/api/admin/orders/${ids.dana1}`);
  assert.deepEqual(o.data.lines.map((l) => l.redeemed), before);
  assert.ok(o.data.coordination.some((c) => c.kind === "shirt_size" && c.value === "M ו־L"));
  const pub = await publicView(ids.dana1);
  assert.ok(!pub.text.includes("איסוף בבוקר") && !pub.text.includes("M ו־L"));
});

// ------------------------------------------------------------------------------------- live vs test

test("sales summaries count only paid morning_live orders; test data only in explicit test scope", async () => {
  const live = await owner.get("/api/admin/summary?scope=live");
  const [exp] = db.sql("SELECT COUNT(*) AS n, SUM(total_agorot) AS s FROM orders WHERE status = 'paid' AND payment_mode = 'morning_live'");
  assert.equal(live.data.paidOrders, exp.n);
  assert.equal(live.data.revenueAgorot, exp.s);
  assert.equal(live.data.notSales.awaiting_payment, 1);
  const test = await owner.get("/api/admin/summary?scope=test");
  assert.equal(test.data.paidOrders, 2);
  assert.equal(test.data.revenueAgorot, 280000 + 12000);
  const liveOrders = await owner.get("/api/admin/orders?q=" + encodeURIComponent("בדיקת"));
  assert.equal(liveOrders.data.total, 0);
  const testOrders = await owner.get("/api/admin/orders?scope=test");
  assert.deepEqual(testOrders.data.orders.map((o) => o.paymentMode).sort(), ["mock", "morning_sandbox"]);
  const prod = await owner.get("/api/admin/products");
  const ak = prod.data.products.find((p) => p.productId === "akadama-10");
  assert.equal(prod.data.products.length, 9);
  assert.deepEqual([ak.soldQty, ak.soldUnits, ak.redeemedUnits, ak.remainingUnits], [3, 30, 24, 6], "live only: dana1 (1 pack) + multi (2 packs)");
  const prodTest = await owner.get("/api/admin/products?scope=test");
  assert.equal(prodTest.data.products.find((p) => p.productId === "akadama-10").soldUnits, 20);
});

test("CSV exports: owner only, UTF-8 BOM, environment column, formula-safe, no tokens or payloads", async () => {
  for (const kind of ["buyers", "orders", "balances"]) {
    const r = await owner.get(`/api/admin/export/${kind}.csv`);
    assert.equal(r.status, 200, kind);
    assert.match(r.headers.get("content-type"), /text\/csv; charset=utf-8/);
    assert.equal(r.headers.get("cache-control"), "no-store");
    const buf = Buffer.from(await (await fetch(`${base}/api/admin/export/${kind}.csv`, { headers: { "Cf-Access-Jwt-Assertion": signToken(signer, claimsFor(team)) } })).arrayBuffer());
    assert.deepEqual([...buf.subarray(0, 3)], [0xef, 0xbb, 0xbf], `${kind} BOM`);
    assert.ok(!r.text.includes("הדמיה") && !r.text.includes("Sandbox"), `${kind} live export excludes test data`);
    const tokens = db.sql("SELECT access_token FROM orders").map((x) => x.access_token);
    assert.ok(tokens.every((t) => !r.text.includes(t)), `${kind} contains no access tokens`);
  }
  const orders = await owner.get("/api/admin/export/orders.csv");
  assert.match(orders.text, /"'=HYPERLINK\(""http:\/\/evil"",""x""\)"/, "formula neutralized");
  assert.ok(!/(^|,)=HYPERLINK/m.test(orders.text));
  assert.match(orders.text, /אמיתי,OY-/);
  const testCsv = await owner.get("/api/admin/export/orders.csv?scope=test");
  assert.ok(testCsv.text.split("\r\n").slice(1).filter(Boolean).every((l) => /^(הדמיה|Sandbox),/.test(l)), "every test row labelled");
  const balances = await owner.get("/api/admin/export/balances.csv");
  assert.match(balances.text, new RegExp(`${ids.dana1}.*אקדמה.*,10,שקים,4,6,מומש חלקית`));
});

test("non-owner cannot export", async () => {
  const intruder = adminClient(base, signToken(signer, claimsFor(team, { email: "intruder@example.com" })));
  assert.equal((await intruder.get("/api/admin/export/orders.csv")).status, 403);
});
