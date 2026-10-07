// Browser checks against a running local Worker (npm run dev). Screenshots go to test-results/.
import { chromium } from "playwright";
import assert from "node:assert/strict";
import { mkdirSync } from "node:fs";
import { execFileSync } from "node:child_process";

const BASE = process.env.BASE || "http://127.0.0.1:8787";
const OUT = "test-results";
mkdirSync(OUT, { recursive: true });
const sql = (q) => JSON.parse(execFileSync("npx", ["wrangler", "d1", "execute", "oyaku-founders-orders", "--local", "--json", "--command", q], { encoding: "utf8" }))[0].results;

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
const log = (...a) => console.log("✓", ...a);

async function noHorizontalScroll(page, label) {
  const { sw, cw } = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
  assert.ok(sw <= cw, `${label}: horizontal overflow ${sw} > ${cw}`);
}

// ---- layout at several widths
for (const [name, viewport] of [["mobile-360", { width: 360, height: 780 }], ["mobile-390", { width: 390, height: 844 }], ["tablet-768", { width: 768, height: 1024 }], ["desktop-1280", { width: 1280, height: 900 }]]) {
  const ctx = await browser.newContext({ viewport, locale: "he-IL" });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  await page.goto(BASE + "/");
  await page.waitForSelector(".product-card h3");
  await page.evaluate(() => document.fonts.ready);
  await noHorizontalScroll(page, name);
  assert.equal(await page.locator(".product-card").count(), 6);
  assert.equal(await page.getAttribute("html", "dir"), "rtl");
  assert.ok(await page.isVisible("#test-banner"), "test banner visible in mock mode");
  await page.screenshot({ path: `${OUT}/${name}-full.png`, fullPage: true });
  assert.deepEqual(errors, [], `${name} console errors`);
  log("layout", name);
  await ctx.close();
}

// ---- cart behaviour
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: "he-IL" });
const page = await ctx.newPage();
await page.goto(BASE + "/");
await page.waitForSelector(".product-card h3");

const card = (name) => page.locator(".product-card", { has: page.getByRole("heading", { name, exact: true }) });

// Shirt ×3 using the + button
await card("חולצת O‑Yaku").getByRole("button", { name: /^הוספה — / }).click();
await card("חולצת O‑Yaku").getByRole("button", { name: /^הוספה — / }).click();
assert.equal(await card("חולצת O‑Yaku").locator("input").inputValue(), "3");
await card("חולצת O‑Yaku").getByRole("button", { name: "הוספה לסל" }).click();
assert.match(await page.textContent("#toast-text"), /נוסף לסל: 3 חולצות/);
log("toast after add");

// Akadama ×2 by typing; hint shows 20 bags
const ak = card("חבילת 10 שקי אקדמה");
await ak.locator("input").fill("2");
assert.match(await ak.locator(".qty-hint").textContent(), /20 שקים · ₪2,800/);
await ak.getByRole("button", { name: "הוספה לסל" }).click();

// Invalid typed quantities are flagged and not added
const pot = card("כלי בונסאי בהזמנה אישית");
for (const bad of ["1.5", "-2", "0", "abc"]) {
  await pot.locator("input").fill(bad);
  assert.equal(await pot.locator("input").getAttribute("aria-invalid"), "true", bad);
}
await pot.locator("input").fill("1");
await pot.getByRole("button", { name: "הוספה לסל" }).click();
log("invalid quantities rejected in the UI");

assert.equal(await page.textContent("#cart-count"), "6");
await page.click("#open-cart");
await page.waitForSelector("#cart-dialog[open]");
const totals = async () => ({
  lines: await page.locator(".cart-line [data-role=line-total]").allTextContents(),
  total: await page.textContent("#cart-total"),
});
assert.deepEqual(await totals(), { lines: ["₪360", "₪2,800", "₪1,200"], total: "₪4,360" });
assert.match(await page.textContent(".cart-total"), /כולל מע״מ/);
await page.screenshot({ path: `${OUT}/cart-mobile.png` });
log("cart totals 3×120 + 2×1,400 + 1×1,200 = 4,360");

// Change quantity in the cart, remove a line
await page.locator(".cart-line[data-id=tshirt]").getByRole("button", { name: /^הפחתה — / }).click();
await page.locator(".cart-line[data-id=akadama-10] input").fill("5");
assert.deepEqual(await totals(), { lines: ["₪240", "₪7,000", "₪1,200"], total: "₪8,440" });
await page.locator(".cart-line[data-id=custom-pot]").getByRole("button", { name: /הסרת/ }).click();
assert.deepEqual(await totals(), { lines: ["₪240", "₪7,000"], total: "₪7,240" });
log("change quantity + remove");

// Reload keeps the cart
await page.reload();
await page.waitForSelector(".product-card h3");
assert.equal(await page.textContent("#cart-count"), "7");
log("cart survives reload");

// Tampered storage: injected prices are ignored, bad lines dropped
await page.evaluate(() => localStorage.setItem("oyaku-founders-cart-v1", JSON.stringify({ v: 1, items: [
  { id: "tshirt", qty: 2, priceAgorot: 1 }, { id: "nursery-sqm-year", qty: -4 }, { id: "fake", qty: 1 }, { id: "custom-pot", qty: 1.5 }, { id: "ceramics-private", qty: 1 },
] })));
await page.reload();
await page.waitForSelector(".product-card h3");
await page.click("#open-cart");
assert.deepEqual(await totals(), { lines: ["₪240", "₪1,200"], total: "₪1,440" });
log("tampered localStorage sanitized; prices from catalog");

// Keyboard: Escape closes and focus returns to the cart button
await page.keyboard.press("Escape");
assert.equal(await page.evaluate(() => document.activeElement?.id), "open-cart");
await page.keyboard.press("Enter");
assert.ok(await page.isVisible("#cart-dialog[open]"));
log("keyboard open/close");

// Validation errors
await page.click("#checkout-button");
assert.equal(await page.getAttribute("#c-name", "aria-invalid"), "true");
assert.equal(await page.evaluate(() => document.activeElement?.id), "c-name");
log("form validation focuses first invalid field");

// Payment start failure (provider unavailable) → message, button re-enabled, no redirect
const email = `e2e-${Date.now()}@example.com`;
await page.fill("#c-name", "בדיקת דפדפן");
await page.fill("#c-phone", "052-7654321");
await page.fill("#c-email", email);
await page.route("**/api/checkout", (r) => r.fulfill({ status: 502, contentType: "application/json", body: JSON.stringify({ error: "payment_unavailable" }) }));
await page.click("#checkout-button");
await page.waitForSelector("#checkout-error:not([hidden])");
assert.match(await page.textContent("#checkout-error"), /לא בוצע חיוב/);
assert.equal(await page.isDisabled("#checkout-button"), false);
await page.unroute("**/api/checkout");
log("payment start failure handled");

// Price tampering from the browser: rewrite the outgoing request body
await page.route("**/api/checkout", async (r) => {
  const body = JSON.parse(r.request().postData());
  body.items = body.items.map((i) => ({ ...i, priceAgorot: 1, qty: i.qty }));
  body.totalAgorot = 1;
  await r.continue({ postData: JSON.stringify(body) });
});
// Double click → one order
// Three clicks in the same tick, before the UI can disable the button.
await page.evaluate(() => { const b = document.querySelector("#checkout-button"); b.click(); b.click(); b.click(); });
await page.waitForURL(/\/pay\/mock/);
await page.unroute("**/api/checkout");
const orders = sql(`SELECT id, total_agorot, status FROM orders WHERE customer_email = '${email}'`);
assert.equal(orders.length, 1, "exactly one order after multiple submits");
assert.equal(orders[0].total_agorot, 144000);
log("double submit → 1 order; tampered price ignored (₪1,440)");
const mockUrl = page.url();

// Back from the payment page, submit again → same order (idempotent)
await page.goBack();
await page.waitForSelector(".product-card h3");
await page.click("#open-cart");
await page.click("#checkout-button");
await page.waitForURL(/\/pay\/mock/);
assert.equal(sql(`SELECT COUNT(*) AS n FROM orders WHERE customer_email = '${email}'`)[0].n, 1);
log("back + resubmit reuses the same order");

// Cancel on the payment page → cancelled; cart kept; retry → new order → success
await page.getByRole("button", { name: "ביטול וחזרה לאתר" }).click();
await page.waitForURL(/\/order\?/);
await page.waitForFunction(() => document.querySelector("#status-title").textContent.includes("לא הושלם"));
await page.screenshot({ path: `${OUT}/order-cancelled.png`, fullPage: true });
await page.getByRole("link", { name: "חזרה לסל" }).click();
await page.waitForSelector("#cart-dialog[open]");
assert.equal(await page.textContent("#cart-total"), "₪1,440");
await page.click("#checkout-button");
try { await page.waitForURL(/\/pay\/mock/, { timeout: 8000 }); } catch (e) {
  await page.screenshot({ path: `${OUT}/debug.png` });
  console.log("DEBUG", await page.evaluate(() => ({ err: document.querySelector("#checkout-error").textContent, dis: document.querySelector("#checkout-button").disabled, attempt: sessionStorage.getItem("oyaku-founders-attempt-v1") })));
  throw e;
}
assert.equal(sql(`SELECT COUNT(*) AS n FROM orders WHERE customer_email = '${email}'`)[0].n, 2);
log("cancel → retry creates a fresh order");

// Simulated failure, then retry and success
await page.getByRole("button", { name: "סימולציה: תשלום נכשל" }).click();
await page.waitForFunction(() => document.querySelector("#status-title").textContent.includes("לא הושלם"));
await page.getByRole("link", { name: "חזרה לסל" }).click();
await page.waitForSelector("#cart-dialog[open]");
await page.click("#checkout-button");
await page.waitForURL(/\/pay\/mock/);
await page.getByRole("button", { name: "סימולציה: תשלום הצליח" }).click();
await page.waitForFunction(() => document.querySelector("#status-title").textContent.includes("אושר"));
assert.match(await page.textContent("#status-text"), /לא בוצע חיוב/);
await page.screenshot({ path: `${OUT}/order-paid-test.png`, fullPage: true });
const final = sql(`SELECT status FROM orders WHERE customer_email = '${email}' ORDER BY created_at`);
assert.deepEqual(final.map((r) => r.status), ["cancelled", "cancelled", "paid"]);
log("failure → retry → paid (test mode, labelled as no charge)");

// Cart cleared after confirmed payment
await page.goto(BASE + "/");
await page.waitForSelector(".product-card h3");
assert.equal(await page.textContent("#cart-count"), "0");
await page.click("#open-cart");
assert.ok(await page.isVisible("#cart-empty"));
log("cart emptied after paid order; empty state shown");

await ctx.close();

// ---- desktop cart screenshot
const d = await browser.newContext({ viewport: { width: 1280, height: 900 }, locale: "he-IL" });
const dp = await d.newPage();
await dp.goto(BASE + "/");
await dp.waitForSelector(".product-card h3");
await dp.evaluate(() => localStorage.setItem("oyaku-founders-cart-v1", JSON.stringify({ v: 1, items: [{ id: "ceramics-group", qty: 4 }, { id: "nursery-sqm-year", qty: 2 }] })));
await dp.reload();
await dp.waitForSelector(".product-card h3");
await dp.click("#open-cart");
await dp.waitForTimeout(300);
await noHorizontalScroll(dp, "desktop cart");
await dp.screenshot({ path: `${OUT}/cart-desktop.png` });
assert.equal(await dp.textContent("#cart-total"), "₪4,200");
log("desktop cart ₪4,200 (4×300 + 2×1,500)");
await d.close();

// ---- mock payment page in a fresh context (screenshot only)
const m = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: "he-IL" });
const mp = await m.newPage();
const fresh = await (await fetch(BASE + "/api/checkout", { method: "POST", headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ idempotencyKey: "shot" + Date.now() + "abcdefgh", customer: { name: "צילום מסך", phone: "050-0000000", email: "shot@example.com" },
    items: [{ id: "tshirt", qty: 2 }, { id: "akadama-10", qty: 2 }, { id: "custom-pot", qty: 1 }] }) })).json();
await mp.goto(fresh.paymentUrl);
await noHorizontalScroll(mp, "mock pay page");
await mp.screenshot({ path: `${OUT}/mock-payment-page.png`, fullPage: true });
log("mock payment page", mockUrl ? "" : "");
await m.close();

await browser.close();
console.log("\nall browser checks passed");
