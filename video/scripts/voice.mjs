#!/usr/bin/env node
/**
 * Generates the voice-over with ElevenLabs from the `narration` lines in src/content.ts.
 * Writes public/voice/<cue>.mp3, which the video picks up automatically.
 *
 *   npm run voice -- --list-voices          list the voices on the account (find your clone's id)
 *   npm run voice -- --voice <id>           generate every line that changed since last run
 *   npm run voice -- --voice <id> --only intro,ask --force
 *
 * Env: ELEVENLABS_API_KEY (unless a network secret injects the xi-api-key header), ELEVENLABS_VOICE_ID (instead of --voice),
 *      ELEVENLABS_MODEL (default eleven_v3, which reads Hebrew).
 */
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = join(ROOT, 'public', 'voice');
const MANIFEST = join(OUT, 'manifest.json');
const API = 'https://api.elevenlabs.io/v1';

const args = process.argv.slice(2);
const flag = (name) => args.includes(`--${name}`);
const opt = (name) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 ? args[i + 1] : undefined;
};

// Either ELEVENLABS_API_KEY is set, or (cloud sessions) the network proxy injects the
// xi-api-key header for api.elevenlabs.io from a network secret, so the key never reaches here.
const key = process.env.ELEVENLABS_API_KEY;

async function api(path, init = {}) {
  const res = await fetch(`${API}${path}`, { ...init, headers: { ...(key ? { 'xi-api-key': key } : {}), ...(init.headers || {}) } }).catch((err) => {
    console.error(`Can't reach ${API} (${err.cause?.message || err.message}). Is api.elevenlabs.io allowed by the network policy?`);
    process.exit(1);
  });
  if (res.status === 401) {
    console.error('ElevenLabs rejected the request (401): no valid key. Set ELEVENLABS_API_KEY, or add a network secret for api.elevenlabs.io with header xi-api-key.');
    process.exit(1);
  }
  if (!res.ok) throw new Error(`${init.method || 'GET'} ${path} → ${res.status} ${await res.text()}`);
  return res;
}

if (flag('list-voices')) {
  const { voices } = await (await api('/voices')).json();
  for (const v of voices) console.log(`${v.voice_id}  ${v.category.padEnd(12)} ${v.name}`);
  process.exit(0);
}

const voice = opt('voice') || process.env.ELEVENLABS_VOICE_ID;
if (!voice) {
  console.error('Pass --voice <id> or set ELEVENLABS_VOICE_ID. Run with --list-voices to find it.');
  process.exit(1);
}
const model = process.env.ELEVENLABS_MODEL || 'eleven_v3';
const only = opt('only')?.split(',');

const { defaultProps } = await import(join(ROOT, 'src', 'content.ts'));
const lines = Object.entries(defaultProps.narration).filter(([cue]) => !only || only.includes(cue));

mkdirSync(OUT, { recursive: true });
const manifest = existsSync(MANIFEST) ? JSON.parse(readFileSync(MANIFEST, 'utf8')) : {};

function seconds(file) {
  try {
    const out = execFileSync('npx', ['remotion', 'ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', file], { cwd: ROOT, encoding: 'utf8' });
    return Number(out.trim());
  } catch {
    return NaN;
  }
}

let tooLong = 0;
for (const [cue, line] of lines) {
  const file = join(OUT, `${cue}.mp3`);
  const hash = createHash('sha1').update(`${voice}|${model}|${line.voice}`).digest('hex');
  if (!flag('force') && manifest[cue] === hash && existsSync(file)) {
    console.log(`= ${cue.padEnd(8)} unchanged`);
  } else {
    const res = await api(`/text-to-speech/${voice}?output_format=mp3_44100_128`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: line.voice, model_id: model }),
    });
    writeFileSync(file, Buffer.from(await res.arrayBuffer()));
    manifest[cue] = hash;
    writeFileSync(MANIFEST, JSON.stringify(manifest, null, 2) + '\n');
  }
  const dur = seconds(file);
  const over = dur > line.maxSec;
  if (over) tooLong++;
  console.log(`${over ? '!' : '✓'} ${cue.padEnd(8)} ${dur.toFixed(1)}s / max ${line.maxSec}s  ${line.voice}`);
}

if (tooLong) console.log(`\n${tooLong} line(s) run past their window — shorten the text, or regenerate (--only <cue> --force).`);
console.log('\nDone. Render with: npm run render');
