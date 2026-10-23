// Video capture harness for the O-YAKU site (copied into a scratch copy of o-yaku-website at
// build time, next to its own tools/home-preview). Renders the real <App /> with a fake
// transport: no credentials, no provider/model calls, no network except this local server.
// Data comes from capture/fixtures.json (public site data read once, read-only).
import { createRoot } from 'react-dom/client';
import { App } from '../../src/App';
import '../../src/styles/index.css';
import fixtures from './fixtures.json';

type Stage = 'approved' | 'retrieval' | 'selection' | 'generation' | 'references';
const STAGES: Stage[] = ['approved', 'retrieval', 'selection', 'generation', 'references'];
const SUPABASE = `${location.origin}/sb`;

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

// The recorder drives the answer stream: each window.__advance() releases the next stage,
// the last one releases the result. window.__qaState tells it where the stream is.
const w = window as unknown as { __advance?: () => void; __qaState?: string; __qaCalls?: number };
w.__qaCalls = 0;
let release: (() => void) | null = null;
w.__advance = () => { const r = release; release = null; r?.(); };
const gate = () => new Promise<void>((resolve) => { release = resolve; });

function answerStream(): Response {
  const enc = new TextEncoder();
  const body = new ReadableStream<Uint8Array>({
    async start(controller) {
      for (const stage of STAGES) {
        await gate();
        w.__qaState = stage;
        controller.enqueue(enc.encode(JSON.stringify({ type: 'stage', stage }) + '\n'));
      }
      await gate();
      w.__qaState = 'result';
      controller.enqueue(enc.encode(JSON.stringify({ type: 'result', status: 200, body: fixtures.answer }) + '\n'));
      controller.close();
    },
  });
  return new Response(body, { status: 200, headers: { 'Content-Type': 'application/x-ndjson' } });
}

const realFetch = globalThis.fetch.bind(globalThis);
globalThis.fetch = async (input, init) => {
  const url = new URL(typeof input === 'string' ? input : input instanceof URL ? input.href : input.url, location.href);
  if (url.origin === location.origin && !url.pathname.startsWith('/sb/')) return realFetch(input, init);
  if (!url.pathname.startsWith('/sb/')) throw Error('capture_network_blocked: ' + url.href);
  const path = url.pathname.slice(3);
  const body = init?.body ? JSON.parse(String(init.body)) : {};
  const token = String((init?.headers as Record<string, string> | undefined)?.authorization || '');

  if (path === '/functions/v1/patreon-session-exchange') {
    return json({ ok: true, session_token: 'capture-session', paid_member: true, full_name: 'מנוי לדוגמה', patron_status: 'active_patron' });
  }
  if (path === '/functions/v1/patreon-access-check') {
    const member = body.session_token === 'capture-session';
    return json({ ok: true, authenticated: member, paid_member: member, full_name: member ? 'מנוי לדוגמה' : null });
  }
  if (path === '/functions/v1/lessons-catalog') return json({ ok: true, lessons: fixtures.lessons });
  if (path === '/functions/v1/lesson-qa-ask') {
    w.__qaCalls = (w.__qaCalls || 0) + 1;
    const member = token.includes('capture-session') || body.session_token === 'capture-session';
    if (!member) {
      w.__qaState = 'blocked';
      // Same body the server sends for a logged-out, non-juniper question (demo_scope_required).
      return json({ ok: false, error: 'demo_scope_required', message_he: fixtures.blockedMessage }, 403);
    }
    return answerStream();
  }
  if (path.startsWith('/rest/v1/')) {
    const table = path.slice('/rest/v1/'.length);
    if (table === 'species') return json(fixtures.species);
    if (table === 'site_content') return json(fixtures.siteContent);
    if (table === 'lessons') return json(fixtures.lessons);
    return json([]);
  }
  return json({ ok: false, error: 'capture_unmocked', path }, 404);
};

void SUPABASE;
createRoot(document.getElementById('root')!).render(<App />);
