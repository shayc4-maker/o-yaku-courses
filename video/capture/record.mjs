#!/usr/bin/env node
/**
 * Captures the real O-YAKU site, state by state, for the explainer video.
 *
 *   node capture/record.mjs <built-site-dir> <out-dir>
 *
 * Writes full-page JPEG snapshots plus timeline.json: for each shot its file, page height and
 * the page-coordinate boxes of the elements the video's cursor and camera need. No outside
 * network: every non-localhost request is aborted. The flow follows the current site exactly:
 * logged-out question outside the juniper demo → demo_scope_required + "התחברות לפטרון" →
 * (Patreon stands in by redirect) → lessons page as member → home → juniper question →
 * five server stages → answer with grouped sources.
 */
import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const { serve } = await import(path.join(path.dirname(fileURLToPath(import.meta.url)), 'server.mjs'));

const [root, out] = process.argv.slice(2).map((p) => p && path.resolve(p));
if (!root || !out) throw Error('usage: record.mjs <built-site-dir> <out-dir>');
mkdirSync(out, { recursive: true });

const QUESTION = 'איך מרכיבים עלווה חדשה על ערער?';
const PORT = Number(process.env.CAPTURE_PORT || 8765);
const W = 1600, H = 888, DPR = 2;

const server = await serve(root, PORT);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: DPR });
const errors = [];
await page.route('**/*', (r) => (new URL(r.request().url()).hostname === 'localhost' ? r.continue() : (errors.push('blocked ' + r.request().url()), r.abort())));
page.on('pageerror', (e) => errors.push('pageerror ' + e.message));

const shots = [];
const box = async (locator) => {
  const b = await locator.first().boundingBox();
  if (!b) return null;
  const sy = await page.evaluate(() => window.scrollY);
  return { x: Math.round(b.x), y: Math.round(b.y + sy), w: Math.round(b.width), h: Math.round(b.height) };
};
async function shot(name, boxes = {}) {
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(250);
  const resolved = {};
  for (const [k, loc] of Object.entries(boxes)) resolved[k] = await box(loc);
  const file = `${String(shots.length).padStart(3, '0')}-${name}.jpg`;
  await page.screenshot({ path: path.join(out, file), fullPage: true, type: 'jpeg', quality: 90, animations: 'disabled', caret: 'initial' });
  const height = await page.evaluate(() => document.documentElement.scrollHeight);
  shots.push({ name, file, height, boxes: resolved, url: page.url() });
  console.log('shot', file, height);
}

const input = () => page.getByRole('textbox', { name: 'השאלה שלכם על בונסאי' });
const submit = () => page.locator('.oy-home-question-form button[type="submit"]');

// 1. Home, logged out.
await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'networkidle' });
await shot('home', {
  input: input(), submit: submit(),
  exampleFicus: page.getByRole('button', { name: 'מתי לבצע עבודת שורשים בפיקוס?' }),
  questionArea: page.locator('.oy-home-hero'),
});

// 2. Example question fills the box (no request yet), then submit.
await page.getByRole('button', { name: 'מתי לבצע עבודת שורשים בפיקוס?' }).click();
await shot('ficus-filled', { input: input(), submit: submit(), questionArea: page.locator('.oy-home-hero') });
await submit().click();
const login = page.getByRole('button', { name: 'התחברות לפטרון' });
await login.waitFor();
await shot('blocked', { login, alert: page.getByRole('alert'), questionArea: page.locator('.oy-home-hero') });

// 3. Login → (redirect stands in for Patreon) → lessons page as a member.
await login.click();
await page.waitForURL((u) => !u.search.includes('patreon_ticket') && !u.pathname.includes('/sb/'), { timeout: 15000 });
await page.getByRole('heading', { name: 'שיעורים מוקלטים' }).waitFor();
await page.waitForLoadState('networkidle');
await shot('lessons', { homeLink: page.getByRole('navigation').getByRole('link', { name: 'בית', exact: true }) });

// 4. Back home as a member.
await page.getByRole('navigation').getByRole('link', { name: 'בית', exact: true }).first().click();
await input().waitFor();
await page.waitForLoadState('networkidle');
await shot('home-member', { input: input(), submit: submit(), questionArea: page.locator('.oy-home-hero') });

// 5. Type the question, one snapshot per character.
await input().click();
for (let i = 1; i <= QUESTION.length; i++) {
  await input().fill(QUESTION.slice(0, i));
  await shot(`type-${String(i).padStart(2, '0')}`, i === QUESTION.length ? { input: input(), submit: submit() } : {});
}

// 6. Submit → the five server-reported stages → answer.
await submit().click();
await page.getByRole('status').waitFor();
await shot('stage-sent', { waiting: page.getByRole('status') });
for (const stage of ['approved', 'retrieval', 'selection', 'generation', 'references']) {
  await page.evaluate(() => window.__advance());
  await page.waitForFunction((s) => window.__qaState === s, stage);
  await page.waitForTimeout(150);
  await shot(`stage-${stage}`, { waiting: page.locator('ol[aria-label="שלבי הכנת התשובה"]') });
}
await page.evaluate(() => window.__advance());
await page.getByText('מקורות התשובה').waitFor();
const patreonLinks = page.getByRole('link', { name: /צפייה בפטראון/ });
await shot('answer', {
  answer: page.locator('.oy-home-answer'),
  sourcesHeading: page.getByText('מקורות התשובה'),
  source3: page.getByText('ביצוע חתך ב-90 מעלות והשחלת הייחור'),
  source3Link: patreonLinks.nth(2),
  followUp: page.locator('[data-follow-up-links]'),
});

writeFileSync(path.join(out, 'timeline.json'), JSON.stringify({ viewport: { w: W, h: H, dpr: DPR }, question: QUESTION, shots, errors }, null, 1));
console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no errors');
await browser.close();
server.close();
