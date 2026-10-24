#!/usr/bin/env node
/**
 * Captures the rest of the real site for the short "tour" part of the video: the articles list
 * and one article, the ceramics page (gallery + the commission calculator in a few states) and
 * the shop. Full-page JPEGs + pages.json (page heights and element boxes for the camera).
 *
 *   node capture/record-pages.mjs <built-site-dir> <out-dir>
 *
 * Public data and images come through server.mjs's GET-only proxy when the build was made with
 * CAPTURE_LIVE_READS=1 and SUPABASE_REAL_URL / SUPABASE_PUBLISHABLE_KEY / CAPTURE_CACHE are set;
 * otherwise from the fixtures (without product/gallery photos).
 */
import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const { serve } = await import(path.join(path.dirname(fileURLToPath(import.meta.url)), 'server.mjs'));

const [root, out] = process.argv.slice(2).map((p) => p && path.resolve(p));
if (!root || !out) throw Error('usage: record-pages.mjs <built-site-dir> <out-dir>');
mkdirSync(out, { recursive: true });
const PORT = Number(process.env.CAPTURE_PORT || 8765);
const server = await serve(root, PORT);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1600, height: 888 }, deviceScaleFactor: 2 });
const errors = [];
await page.route('**/*', (r) => (new URL(r.request().url()).hostname === 'localhost' ? r.continue() : (errors.push('blocked ' + r.request().url()), r.abort())));
page.on('pageerror', (e) => errors.push('pageerror ' + e.message));

const shots = [];
async function settle() {
  await page.waitForLoadState('networkidle');
  await page.evaluate(async () => {
    await document.fonts.ready;
    document.querySelectorAll('img[loading="lazy"]').forEach((img) => { img.loading = 'eager'; });
    // Lazy images: scroll through once so every image decodes before the full-page shot.
    for (let y = 0; y < document.documentElement.scrollHeight; y += 400) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 200)); }
    window.scrollTo(0, 0);
    await Promise.all([...document.images].map((img) => img.complete ? img.decode().catch(() => null) : new Promise((r) => { img.onload = img.onerror = r; })));
  });
  await page.waitForTimeout(1200);
}
async function shot(name, boxes = {}) {
  const resolved = {};
  for (const [k, sel] of Object.entries(boxes)) {
    const b = await page.locator(sel).first().boundingBox().catch(() => null);
    const sy = await page.evaluate(() => window.scrollY);
    resolved[k] = b ? { x: Math.round(b.x), y: Math.round(b.y + sy), w: Math.round(b.width), h: Math.round(b.height) } : null;
  }
  const file = `p${String(shots.length).padStart(2, '0')}-${name}.jpg`;
  await page.screenshot({ path: path.join(out, file), fullPage: true, type: 'jpeg', quality: 88, animations: 'disabled' });
  const height = await page.evaluate(() => document.documentElement.scrollHeight);
  shots.push({ name, file, height, boxes: resolved, url: page.url() });
  console.log('shot', file, height);
}

// Articles: list, then the first article.
await page.goto(`http://localhost:${PORT}/articles`); await settle();
await shot('articles');
// Article cards open on click (no link); pick the elm development log, which has many photos.
await page.getByText('פיתוח אולמוס לאורך זמן', { exact: true }).first().click();
await page.waitForURL(/\/articles\/.+/);
await settle();
await shot('article');

// Ceramics: page, then the calculator in a few states.
await page.goto(`http://localhost:${PORT}/ceramics`); await settle();
const calc = 'section:has-text("מחשבון כלי בהזמנה")';
await shot('ceramics', { calculator: calc });
const field = (label) => page.getByLabel(label, { exact: true });
const states = [
  { shape: 1, L: '32', W: '24', H: '7' },
  { shape: 2, L: '28', W: '28', H: '10' },
  { shape: 0, L: '40', W: '30', H: '9' },
];
const shapeSelect = page.getByLabel('צורה', { exact: true });
const options = await shapeSelect.locator('option').evaluateAll((os) => os.map((o) => o.value));
for (const [i, s] of states.entries()) {
  await shapeSelect.selectOption(options[s.shape % options.length]);
  await field('אורך (ס״מ)').fill(s.L); await field('רוחב (ס״מ)').fill(s.W); await field('גובה (ס״מ)').fill(s.H);
  await page.waitForTimeout(250);
  await shot(`calc-${i + 1}`, { calculator: calc });
}

// Shop.
await page.goto(`http://localhost:${PORT}/shop`); await settle();
await shot('shop');

writeFileSync(path.join(out, 'pages.json'), JSON.stringify({ viewport: { w: 1600, h: 888, dpr: 2 }, shots, errors }, null, 1));
console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no errors');
await browser.close(); server.close();
