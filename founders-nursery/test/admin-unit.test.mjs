import { test } from "node:test";
import assert from "node:assert/strict";
import { readAccessConfig, checkCsrf, tokenFromRequest, verifyAccess } from "../src/admin/access.js";
import { csvCell, toCsv } from "../src/admin/api.js";
import { lineState, israelDayStartUtc, isValidDay, redeemUnitsFor, normalizeEmail } from "../src/fulfillment.js";

const prodUrl = new URL("https://nursery.o-yaku.com/api/admin/me");
const localUrl = new URL("http://127.0.0.1:8791/api/admin/me");
const full = { ACCESS_TEAM_DOMAIN: "https://oyaku.cloudflareaccess.com", ACCESS_AUD: "aud", ADMIN_EMAILS: "Owner@Example.com" };

test("Access config: all three values required, team domain format enforced", () => {
  assert.equal(readAccessConfig(full, prodUrl).ok, true);
  assert.deepEqual(readAccessConfig(full, prodUrl).admins, ["owner@example.com"]);
  for (const k of Object.keys(full)) assert.equal(readAccessConfig({ ...full, [k]: "" }, prodUrl).ok, false, k);
  assert.equal(readAccessConfig({}, prodUrl).ok, false);
  for (const bad of ["http://oyaku.cloudflareaccess.com", "https://evil.com", "https://oyaku.cloudflareaccess.com.evil.com", "https://a.cloudflareaccess.com/x"]) {
    assert.equal(readAccessConfig({ ...full, ACCESS_TEAM_DOMAIN: bad }, prodUrl).ok, false, bad);
  }
});

test("a loopback (test) team domain is refused unless the request itself is local", () => {
  const local = { ...full, ACCESS_TEAM_DOMAIN: "http://127.0.0.1:9811" };
  assert.equal(readAccessConfig(local, prodUrl).ok, false);
  assert.equal(readAccessConfig(local, localUrl).ok, true);
});

test("unconfigured verifyAccess fails closed even with a token present", async () => {
  const req = new Request(prodUrl, { headers: { "Cf-Access-Jwt-Assertion": "a.b.c" } });
  await assert.rejects(verifyAccess(req, {}), (e) => e.code === "admin_not_configured" && e.status === 503);
});

test("token is read from the Access header first, then the CF_Authorization cookie", () => {
  assert.equal(tokenFromRequest(new Request(prodUrl, { headers: { "Cf-Access-Jwt-Assertion": "h.h.h", Cookie: "CF_Authorization=c.c.c" } })), "h.h.h");
  assert.equal(tokenFromRequest(new Request(prodUrl, { headers: { Cookie: "a=1; CF_Authorization=c.c.c; b=2" } })), "c.c.c");
  assert.equal(tokenFromRequest(new Request(prodUrl, { headers: { Cookie: "XCF_Authorization=c.c.c" } })), null);
});

test("CSRF guard", () => {
  const ok = { "Content-Type": "application/json", Origin: "https://nursery.o-yaku.com", "X-OY-Admin": "1" };
  const mk = (h, method = "POST") => new Request(prodUrl, { method, headers: h, body: method === "POST" ? "{}" : undefined });
  assert.doesNotThrow(() => checkCsrf(mk(ok)));
  assert.doesNotThrow(() => checkCsrf(mk({ ...ok, "Content-Type": "application/json; charset=utf-8", "Sec-Fetch-Site": "same-origin" })));
  for (const [h, code] of [[{ ...ok, Origin: "https://evil.com" }, "csrf_origin"], [{ ...ok, Origin: undefined }, "csrf_origin"],
    [{ ...ok, "X-OY-Admin": undefined }, "csrf_header"], [{ ...ok, "Content-Type": "text/plain" }, "json_required"],
    [{ ...ok, "Sec-Fetch-Site": "same-site" }, "csrf_site"]]) {
    const clean = Object.fromEntries(Object.entries(h).filter(([, v]) => v !== undefined));
    assert.throws(() => checkCsrf(mk(clean)), (e) => e.code === code, code);
  }
  assert.throws(() => checkCsrf(mk(ok, "GET")), (e) => e.code === "method_not_allowed");
});

test("CSV cells: formulas neutralized, quotes escaped, numbers kept numeric, BOM present", () => {
  assert.equal(csvCell("=1+1"), "'=1+1");
  assert.equal(csvCell("+972501234567"), "'+972501234567");
  assert.equal(csvCell("-2"), "'-2");
  assert.equal(csvCell("@SUM(A1)"), "'@SUM(A1)");
  assert.equal(csvCell('a "b", c'), '"a ""b"", c"');
  assert.equal(csvCell(-2), "-2");
  assert.equal(csvCell(null), "");
  assert.equal(toCsv(["א"], [[1]]), "﻿א\r\n1\r\n");
});

test("redemption units and states", () => {
  assert.deepEqual(redeemUnitsFor("akadama-10", 2), { units: 20, label: "שקים" });
  assert.deepEqual(redeemUnitsFor("ceramics-group", 4), { units: 4, label: "משתתפים" });
  assert.equal(normalizeEmail("  Dana@Example.COM "), "dana@example.com");
  const base = { paid: true, cancelled: false, expired: false, units: 10 };
  assert.equal(lineState({ ...base, redeemed: 0 }), "not_redeemed");
  assert.equal(lineState({ ...base, redeemed: 4 }), "partial");
  assert.equal(lineState({ ...base, redeemed: 10 }), "full");
  assert.equal(lineState({ ...base, expired: true, redeemed: 4 }), "expired");
  assert.equal(lineState({ ...base, cancelled: true, redeemed: 10 }), "cancelled");
  assert.equal(lineState({ ...base, paid: false, redeemed: 0 }), "na");
});

test("Israel day bounds and date validation", () => {
  assert.equal(israelDayStartUtc("2027-01-15"), "2027-01-14T22:00:00.000Z");
  assert.equal(israelDayStartUtc("2027-07-15"), "2027-07-14T21:00:00.000Z");
  assert.equal(isValidDay("2027-02-29"), false);
  assert.equal(isValidDay("2028-02-29"), true);
  assert.equal(isValidDay("2027-1-1"), false);
});
