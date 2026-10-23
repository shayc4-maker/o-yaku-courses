#!/usr/bin/env node
/**
 * Builds the real O-YAKU site (from a checkout of shayc4-maker/o-yaku-website, never modified)
 * with the capture harness, into an output folder served by server.mjs.
 *
 *   node capture/build.mjs <site-checkout-copy> <out-dir>
 *
 * The site checkout must have its locked dependencies installed (npm ci). The harness files are
 * copied into <site>/tools/video-capture/ of THAT copy, so pass a scratch copy, not your clone.
 */
import { cpSync, mkdirSync, readFileSync, readdirSync, writeFileSync, copyFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const [site, out] = process.argv.slice(2).map((p) => p && path.resolve(p));
if (!site || !out) throw Error('usage: build.mjs <site-checkout-copy> <out-dir>');
if (!existsSync(path.join(site, 'src/App.tsx'))) throw Error('not an o-yaku-website checkout: ' + site);

const dest = path.join(site, 'tools/video-capture');
mkdirSync(dest, { recursive: true });
for (const f of ['entry.tsx', 'fixtures.json']) copyFileSync(path.join(HERE, f), path.join(dest, f));

const { build } = createRequire(path.join(site, 'package.json'))('esbuild');
mkdirSync(out, { recursive: true });
const PORT = process.env.CAPTURE_PORT || '8765';
await build({
  absWorkingDir: site,
  entryPoints: ['tools/video-capture/entry.tsx'],
  outfile: path.join(out, 'app.js'),
  bundle: true, platform: 'browser', format: 'esm', jsx: 'automatic', loader: { '.png': 'file', '.svg': 'file', '.jpg': 'file' },
  define: {
    'import.meta.env': '{}',
    'import.meta.env.VITE_SUPABASE_URL': JSON.stringify(`http://localhost:${PORT}/sb`),
    'import.meta.env.VITE_SUPABASE_ANON_KEY': JSON.stringify('capture-anon'),
    'import.meta.env.DEV': 'false', 'import.meta.env.PROD': 'true',
  },
  logLevel: 'warning',
});

// Fonts: the site imports Assistant + Frank Ruhl Libre from Google Fonts; serve the same
// families locally (the render browser can't reach Google through this sandbox's proxy).
const fontsDir = path.join(HERE, '..', 'public', 'fonts');
cpSync(fontsDir, path.join(out, 'fonts'), { recursive: true });
const HEB = 'U+0307-0308, U+0590-05FF, U+200C-2010, U+20AA, U+25CC, U+FB1D-FB4F';
const LAT = 'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD';
const face = (family, file, range, weight) => `@font-face{font-family:'${family}';src:url(/fonts/${file}) format('woff2');font-weight:${weight};font-display:block;unicode-range:${range}}`;
const fontCss = [
  face('Assistant', 'assistant-hebrew.woff2', HEB, '200 800'), face('Assistant', 'assistant-latin.woff2', LAT, '200 800'),
  face('Frank Ruhl Libre', 'frank-hebrew.woff2', HEB, '300 900'), face('Frank Ruhl Libre', 'frank-latin.woff2', LAT, '300 900'),
].join('\n');
const cssFile = path.join(out, 'app.css');
const css = readFileSync(cssFile, 'utf8').replace(/@import\s+url\("https:\/\/fonts\.googleapis\.com[^)]*\);?/g, '');
writeFileSync(cssFile, fontCss + '\n' + css);

for (const f of readdirSync(path.join(site, 'public'), { withFileTypes: true })) {
  if (f.isFile()) copyFileSync(path.join(site, 'public', f.name), path.join(out, f.name));
}
writeFileSync(path.join(out, 'index.html'), `<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>O-YAKU</title><link rel="stylesheet" href="/app.css"></head><body><div id="root"></div><script type="module" src="/app.js"></script></body></html>`);
console.log('built', out);
