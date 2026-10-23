/**
 * Static server for the captured site build. Also stands in for patreon-auth-start: instead of
 * going to Patreon, it redirects straight back with a capture ticket, exactly the URL shape the
 * real patreon-auth-callback produces (?patreon_ticket=…&patreon_return=…#/auth/patreon).
 */
import { createServer } from 'node:http';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';

const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.webp': 'image/webp', '.json': 'application/json' };

export function serve(root, port) {
  const server = createServer(async (req, res) => {
    const url = new URL(req.url, `http://localhost:${port}`);
    if (url.pathname === '/sb/functions/v1/patreon-auth-start') {
      const back = new URL(`http://localhost:${port}/`);
      back.searchParams.set('patreon_ticket', 'capture-ticket');
      back.searchParams.set('patreon_return', url.searchParams.get('return_path') || '#/lessons');
      res.writeHead(302, { location: back.href + '#/auth/patreon' });
      return res.end();
    }
    // Public reads only (GET on PostgREST + public Storage), forwarded to the real project with its
    // publishable key and cached under CAPTURE_CACHE so a capture can be replayed offline.
    if (req.method === 'GET' && (url.pathname.startsWith('/sb/rest/v1/') || url.pathname.startsWith('/sb/storage/v1/object/public/'))) {
      return proxyRead(url, res);
    }
    if (url.pathname.startsWith('/sb/')) { res.writeHead(404); return res.end(); }
    let file = path.join(root, decodeURIComponent(url.pathname));
    if (!file.startsWith(root)) { res.writeHead(403); return res.end(); }
    try {
      const body = await readFile(file).catch(async () => { file = path.join(root, 'index.html'); return readFile(file); });
      res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' });
      res.end(body);
    } catch { res.writeHead(404); res.end(); }
  });
  return new Promise((resolve) => server.listen(port, () => resolve(server)));
}

async function proxyRead(url, res) {
  const cacheDir = process.env.CAPTURE_CACHE;
  const key = createHash('sha1').update(url.pathname + url.search).digest('hex');
  const cached = cacheDir && await readFile(path.join(cacheDir, key + '.json')).then((b) => JSON.parse(b), () => null);
  if (cached) {
    res.writeHead(cached.status, { 'content-type': cached.type });
    return res.end(Buffer.from(cached.body, 'base64'));
  }
  const base = process.env.SUPABASE_REAL_URL, apikey = process.env.SUPABASE_PUBLISHABLE_KEY;
  if (!base || !apikey) { res.writeHead(404); return res.end(); }
  const upstream = await fetch(base + url.pathname.slice(3) + url.search, { headers: { apikey, accept: 'application/json' } }).catch(() => null);
  if (!upstream) { res.writeHead(502); return res.end(); }
  const body = Buffer.from(await upstream.arrayBuffer());
  const type = upstream.headers.get('content-type') || 'application/octet-stream';
  if (cacheDir && upstream.ok) {
    await mkdir(cacheDir, { recursive: true });
    await writeFile(path.join(cacheDir, key + '.json'), JSON.stringify({ path: url.pathname + url.search, status: upstream.status, type, body: body.toString('base64') }));
  }
  res.writeHead(upstream.status, { 'content-type': type });
  res.end(body);
}
