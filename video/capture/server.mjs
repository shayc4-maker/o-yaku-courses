/**
 * Static server for the captured site build. Also stands in for patreon-auth-start: instead of
 * going to Patreon, it redirects straight back with a capture ticket, exactly the URL shape the
 * real patreon-auth-callback produces (?patreon_ticket=…&patreon_return=…#/auth/patreon).
 */
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
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
