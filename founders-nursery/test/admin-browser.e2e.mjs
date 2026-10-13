// Admin UI in a real browser (desktop + phone), with a private Worker, local D1 full of fictional
// orders, and a test-only Access key delivered as the CF_Authorization cookie.
// Run: node test/admin-browser.e2e.mjs   → screenshots in test-results/admin-*.png
import { chromium } from "playwright";
import assert from "node:assert/strict";
import { mkdirSync, rmSync } from "node:fs";
import { makeKey, signToken, startJwks, claimsFor, startWorker, migrateWithLegacy } from "./helpers/admin-env.mjs";
import { legacyOrder, AKADAMA, SHIRT, SQM, LESSON, GROUP } from "./helpers/fixtures.mjs";

const OUT = "test-results";
mkdirSync(OUT, { recursive: true });
const PERSIST = ".wrangler/state-admin-browser";
const log = (...a) => console.log("✓", ...a);
const alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ";
const names = ["נועה ברק", "איתי שמעוני", "מיכל אדלר", "רון גפן", "שירה טל", "עמית הורוביץ", "יעל דגן", "אורי פז", "תמר נחום", "גיל רוזן"];
const productSets = [[SHIRT(2)], [AKADAMA(1)], [GROUP(4)], [LESSON(1), SHIRT(1)], [SQM(1)], [AKADAMA(2), SHIRT(3)]];

const rows = [
  legacyOrder({ id: "OY-AKADAMA2", name: "דנה לוי", email: "dana@example.com", phone: "050-1111111", items: [AKADAMA(1), SHIRT(2), SQM(1)] }),
  legacyOrder({ id: "OY-MCKDEM22", mode: "mock", name: "בדיקת הדמיה", email: "mock@example.com", phone: "050-5555555", items: [AKADAMA(2)] }),
  legacyOrder({ id: "OY-SNDBX222", mode: "morning_sandbox", name: "בדיקת סנדבוקס", email: "sb@example.com", phone: "050-6666666", items: [SHIRT(1)] }),
  ...Array.from({ length: 84 }, (_, n) => legacyOrder({
    id: `OY-LV${alphabet[Math.floor(n / 32)]}${alphabet[n % 32]}MANY`,
    name: `${names[n % names.length]}${n >= names.length ? ` ${Math.floor(n / names.length) + 1}` : ""}`,
    email: `buyer${n}@example.com`, phone: `052-${String(5550000 + n)}`,
    status: n % 9 === 0 ? "awaiting_payment" : "paid",
    paidAt: new Date(Date.UTC(2026, 9, 20 + (n % 10), 8, n)).toISOString(),
    items: productSets[n % productSets.length],
  })),
];

const signer = makeKey();
const jwks = await startJwks([signer], 9831);
const db = migrateWithLegacy(PERSIST, rows.join("\n"));
const { child, base, team } = await startWorker({ port: 8793, jwksPort: 9831, persist: PERSIST, vars: { TEST_NOW: "2027-03-01T10:00:00Z" } });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });

async function adminContext(viewport) {
  const ctx = await browser.newContext({ viewport, locale: "he-IL", timezoneId: "Asia/Jerusalem" });
  await ctx.addCookies([{ name: "CF_Authorization", value: signToken(signer, claimsFor(team)), domain: "127.0.0.1", path: "/", httpOnly: true, secure: false, sameSite: "Lax" }]);
  return ctx;
}
async function noHScroll(page, label) {
  const { sw, cw } = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
  assert.ok(sw <= cw, `${label}: horizontal overflow ${sw} > ${cw}`);
}
const ready = (page) => page.waitForFunction(() => !document.querySelector("#view [role=status]")?.textContent?.includes("טוען"));

try {
  // ---- no cookie → blocked page, no data
  {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    const res = await page.goto(base + "/admin");
    assert.equal(res.status(), 401);
    assert.ok(!(await page.content()).includes("דנה"));
    await page.screenshot({ path: `${OUT}/admin-blocked.png` });
    log("no Access cookie → blocked page");
    await ctx.close();
  }

  for (const [label, viewport] of [["desktop", { width: 1280, height: 900 }], ["mobile", { width: 390, height: 844 }]]) {
    const ctx = await adminContext(viewport);
    const page = await ctx.newPage();
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    page.on("console", (m) => m.type() === "error" && !/Failed to load resource/.test(m.text()) && errors.push(m.text()));

    await page.goto(base + "/admin#/");
    await page.waitForSelector(".stats");
    await page.evaluate(() => document.fonts.ready);
    await noHScroll(page, `${label} summary`);
    await page.screenshot({ path: `${OUT}/admin-${label}-summary.png`, fullPage: true });

    await page.click('[data-nav="orders"]');
    await page.waitForSelector(".data-table tbody tr");
    await noHScroll(page, `${label} orders`);
    assert.match(await page.textContent("#view"), /\d+ הזמנות/);
    await page.screenshot({ path: `${OUT}/admin-${label}-orders.png`, fullPage: label === "desktop" });

    await page.goto(base + "/admin#/orders?q=zzzz-none");
    await page.waitForSelector("text=אין הזמנות שמתאימות לסינון.");
    log(label, "empty state");

    await page.goto(base + "/admin#/products");
    await page.waitForSelector(".data-table");
    await noHScroll(page, `${label} products`);
    await page.screenshot({ path: `${OUT}/admin-${label}-products.png`, fullPage: true });

    await page.goto(base + "/admin#/orders/OY-AKADAMA2");
    await page.waitForSelector("h1:has-text('OY-AKADAMA2')");
    await noHScroll(page, `${label} order`);
    await page.screenshot({ path: `${OUT}/admin-${label}-order.png`, fullPage: true });
    assert.deepEqual(errors, [], `${label} console errors`);
    log(label, "summary, orders, products, order detail render without overflow");
    await ctx.close();
  }

  // ---- redemption through the UI, including a double click
  {
    const ctx = await adminContext({ width: 1280, height: 900 });
    const page = await ctx.newPage();
    await page.goto(base + "/admin#/orders/OY-AKADAMA2");
    await page.waitForSelector("h1:has-text('OY-AKADAMA2')");
    const line = page.locator(".line", { has: page.getByRole("heading", { name: "חבילת 10 שקי אקדמה" }) });
    await line.getByRole("button", { name: "מימוש", exact: true }).click();
    await line.getByLabel("כמות (שקים)").fill("4");
    await line.getByLabel("הערה (פנימית)").fill("איסוף 4 שקים");
    await line.evaluate((el) => { const b = el.querySelector("form button[type=submit]"); b.click(); b.click(); b.click(); });
    await page.waitForSelector("text=יתרה 6");
    const [r] = db.sql("SELECT COUNT(*) AS n, SUM(quantity) AS q FROM redemptions WHERE order_id = 'OY-AKADAMA2'");
    assert.deepEqual([r.n, r.q], [1, 4], "triple click → one redemption of 4");
    log("UI redemption 4 of 10 bags → balance 6, one row despite triple click");

    // Over-redemption is refused by the server even if the form is bypassed.
    await line.getByRole("button", { name: "מימוש", exact: true }).click();
    await line.getByLabel("כמות (שקים)").evaluate((el) => { el.removeAttribute("max"); el.value = "7"; });
    await line.locator("form button[type=submit]").click();
    await line.locator("[role=alert]").waitFor();
    assert.match(await line.locator("[role=alert]").textContent(), /הכמות גדולה מהיתרה\. יתרה: 6/);
    log("over-redemption refused with remaining balance shown");

    // Correction
    await page.getByRole("button", { name: "תיקון", exact: true }).click();
    await page.getByLabel("כמות לביטול (עד 4)").fill("1");
    await page.getByLabel("סיבת התיקון").fill("נמסרו 3 ולא 4");
    await page.getByRole("button", { name: "שמירת תיקון" }).click();
    await page.waitForSelector("text=יתרה 7");
    log("correction → balance 7, linked to original");

    // Coordination note
    await page.selectOption("#n-kind", "shirt_size");
    await page.selectOption("#n-product", "tshirt");
    await page.fill("#n-value", "M, L");
    await page.getByRole("button", { name: "שמירה", exact: true }).click();
    await page.waitForSelector("dd:has-text('M, L')");
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: `${OUT}/admin-desktop-order-after.png`, fullPage: true });
    log("coordination note saved");

    // Public voucher reflects the balance, without internal notes
    const [{ access_token: t }] = db.sql("SELECT access_token FROM orders WHERE id = 'OY-AKADAMA2'");
    const pub = await ctx.newPage();
    await pub.setViewportSize({ width: 390, height: 844 });
    await pub.goto(`${base}/order?order=OY-AKADAMA2&t=${t}`);
    await pub.waitForSelector("#voucher:not([hidden])");
    const vt = await pub.textContent("#voucher");
    assert.match(vt, /יתרה למימוש: 7 מתוך 10 שקים · מומש חלקית/);
    assert.ok(!vt.includes("איסוף 4 שקים") && !vt.includes("M, L") && !vt.includes("owner@"));
    assert.match(await pub.textContent("#voucher-state"), /מומש חלקית/);
    await pub.screenshot({ path: `${OUT}/public-voucher-partial.png`, fullPage: true });
    log("public voucher shows 7 of 10 bags, no internal data");

    // Cancel the voucher via UI
    await page.fill("#cancel-reason", "בקשת לקוח");
    await page.check("#cancel-confirm");
    await page.getByRole("button", { name: "ביטול השובר" }).click();
    await page.waitForSelector("text=השובר בוטל");
    assert.match(await page.textContent("#view"), /שולם/, "payment status unchanged");
    await pub.reload();
    await pub.waitForSelector("#voucher:not([hidden])");
    assert.match(await pub.textContent("#voucher-state"), /בוטל/);
    assert.match(await pub.textContent("#voucher"), /יתרה למימוש: 0 מתוך 10 שקים/);
    await pub.screenshot({ path: `${OUT}/public-voucher-cancelled.png`, fullPage: true });
    log("voucher cancelled: blocks redemption, payment stays paid, public view updated");

    // Buyer card
    await page.goto(base + "/admin#/buyers?q=" + encodeURIComponent("דנה"));
    await page.getByRole("link", { name: "דנה לוי" }).click();
    await page.waitForSelector("h2:has-text('שוברים ויתרות')");
    assert.ok(await page.locator('a[href^="tel:"]').count());
    assert.ok(await page.locator('a[href^="mailto:"]').count());
    await page.screenshot({ path: `${OUT}/admin-desktop-buyer.png`, fullPage: true });
    log("buyer card with tel/mailto");

    // Test scope
    await page.goto(base + "/admin#/orders");
    await page.check("#scope-test");
    await page.waitForSelector("#scope-banner:not([hidden])");
    await page.waitForSelector(".badge-test");
    const modes = await page.locator(".data-table .badge-test").allTextContents();
    assert.ok(modes.length >= 2 && modes.every((m) => ["הדמיה", "Sandbox"].includes(m)));
    await page.screenshot({ path: `${OUT}/admin-desktop-test-scope.png`, fullPage: true });
    log("test scope: banner + every row marked");

    // Loading and error states
    await page.uncheck("#scope-test");
    await page.route("**/api/admin/products**", async (route) => { await new Promise((r) => setTimeout(r, 1500)); await route.continue(); });
    await page.goto(base + "/admin?reload=1#/products", { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#view [role=status]");
    await page.screenshot({ path: `${OUT}/admin-desktop-loading.png` });
    await page.waitForSelector(".data-table");
    await page.unroute("**/api/admin/products**");
    await page.route("**/api/admin/buyers**", (route) => route.fulfill({ status: 500, contentType: "application/json", body: '{"error":"server_error"}' }));
    await page.goto(base + "/admin?reload=2#/buyers");
    await page.waitForSelector("[role=alert]");
    assert.ok(await page.getByRole("button", { name: "ניסיון חוזר" }).isVisible());
    await page.screenshot({ path: `${OUT}/admin-desktop-error.png` });
    log("loading and error states");
    await ctx.close();
  }

  // ---- phone: order detail + buyer card after activity
  {
    const ctx = await adminContext({ width: 390, height: 844 });
    const page = await ctx.newPage();
    await page.goto(base + "/admin#/orders/OY-AKADAMA2");
    await page.waitForSelector("h2:has-text('היסטוריה')");
    await noHScroll(page, "mobile order after");
    await page.screenshot({ path: `${OUT}/admin-mobile-order-after.png`, fullPage: true });
    await page.goto(base + "/admin#/buyers");
    await page.waitForSelector(".data-table tbody tr");
    await noHScroll(page, "mobile buyers");
    await page.screenshot({ path: `${OUT}/admin-mobile-buyers.png`, fullPage: false });
    log("phone: order history and buyers list");
    await ctx.close();
  }
  console.log("\nall admin browser checks passed");
} finally {
  await browser.close();
  child.stop();
  jwks.close();
  rmSync(PERSIST, { recursive: true, force: true });
}
