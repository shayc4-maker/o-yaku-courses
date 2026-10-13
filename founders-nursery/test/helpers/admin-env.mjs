// Test harness for the admin area: a throwaway RSA key, a local JWKS endpoint that stands in for
// <team>.cloudflareaccess.com/cdn-cgi/access/certs, signed test tokens, and a private Worker + D1.
// The key exists only in memory for the duration of a test run.
import http from "node:http";
import { generateKeyPairSync, createSign, randomUUID } from "node:crypto";
import { spawn, execFileSync } from "node:child_process";
import { rmSync, writeFileSync, mkdtempSync, openSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

export const AUD = "test-aud-0123456789";
export const OWNER = "owner@example.com";

const b64url = (buf) => Buffer.from(buf).toString("base64").replace(/=+$/, "").replace(/\+/g, "-").replace(/\//g, "_");

export function makeKey(kid = "test-kid-1") {
  const { privateKey, publicKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });
  const jwk = publicKey.export({ format: "jwk" });
  return { kid, privateKey, jwk: { ...jwk, kid, alg: "RS256", use: "sig" } };
}

export function signToken(key, claims, header = {}) {
  const h = b64url(JSON.stringify({ alg: "RS256", kid: key.kid, typ: "JWT", ...header }));
  const p = b64url(JSON.stringify(claims));
  const s = createSign("RSA-SHA256").update(`${h}.${p}`).sign(key.privateKey);
  return `${h}.${p}.${b64url(s)}`;
}

export async function startJwks(keys, port) {
  const server = http.createServer((req, res) => {
    if (req.url === "/cdn-cgi/access/certs") {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ keys: keys.map((k) => k.jwk) }));
    } else {
      res.writeHead(404);
      res.end();
    }
  });
  await new Promise((ok) => server.listen(port, "127.0.0.1", ok));
  return server;
}

export function claimsFor(team, overrides = {}) {
  const now = Math.floor(Date.now() / 1000);
  return { aud: [AUD], email: OWNER, exp: now + 3600, iat: now - 10, nbf: now - 10, iss: team, type: "app", sub: randomUUID(), ...overrides };
}

export async function startWorker({ port, jwksPort, persist, vars = {} }) {
  const team = `http://127.0.0.1:${jwksPort}`;
  const allVars = {
    PAYMENT_MODE: "mock", ACCESS_TEAM_DOMAIN: team, ACCESS_AUD: AUD, ADMIN_EMAILS: OWNER,
    NOTIFY_SIGNING_SECRET: "admin-test-notify-secret-0123456789", ...vars,
  };
  // --local-upstream keeps request.url on 127.0.0.1 (otherwise wrangler rewrites it to the production route host).
  const child = spawn("node_modules/.bin/wrangler", ["dev", "--port", String(port), "--ip", "127.0.0.1", "--local-upstream", `127.0.0.1:${port}`, "--persist-to", persist,
    ...Object.entries(allVars).flatMap(([k, v]) => ["--var", `${k}:${v}`])],
    { stdio: process.env.WORKER_LOG ? ["ignore", openSync(process.env.WORKER_LOG, "w"), openSync(process.env.WORKER_LOG, "a")] : "ignore", detached: true, env: { ...process.env, NO_PROXY: "127.0.0.1,localhost", no_proxy: "127.0.0.1,localhost" } });
  // Stops wrangler and its workerd child together (own process group).
  child.stop = () => { try { process.kill(-child.pid, "SIGTERM"); } catch {} };
  const base = `http://127.0.0.1:${port}`;
  for (let i = 0; i < 90; i++) {
    try { if ((await fetch(base + "/api/config")).ok) return { child, base, team }; } catch {}
    await new Promise((ok) => setTimeout(ok, 500));
  }
  child.stop();
  throw new Error("worker did not start");
}

export function d1(persist) {
  const run = (args) => execFileSync("npx", ["wrangler", "d1", "execute", "oyaku-founders-orders", "--local", "--persist-to", persist, "--json", ...args], { encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
  return {
    sql: (q) => JSON.parse(run(["--command", q]))[0].results,
    file: (path) => run(["--file", path]),
    script: (text) => {
      const dir = mkdtempSync(join(tmpdir(), "oy-sql-"));
      const f = join(dir, "s.sql");
      writeFileSync(f, text);
      try { return run(["--file", f]); } finally { rmSync(dir, { recursive: true, force: true }); }
    },
  };
}

// Applies 0001 + 0002, inserts legacy rows (as they exist before the admin migration), then 0003.
export function migrateWithLegacy(persist, legacySql) {
  rmSync(persist, { recursive: true, force: true });
  const db = d1(persist);
  db.file("migrations/0001_orders.sql");
  db.file("migrations/0002_purchase_terms.sql");
  if (legacySql) db.script(legacySql);
  db.file("migrations/0003_admin.sql");
  return db;
}

// The synchronous `wrangler d1 execute` calls in tests block the event loop long enough for the
// local server to drop idle keep-alive sockets; retry once on a dropped connection (never on an HTTP status).
export async function tfetch(url, init) {
  try {
    return await fetch(url, init);
  } catch (e) {
    if (e instanceof TypeError) return fetch(url, init);
    throw e;
  }
}

export function adminClient(base, token) {
  const headers = (extra = {}) => ({ ...(token ? { "Cf-Access-Jwt-Assertion": token } : {}), ...extra });
  return {
    get: async (path) => {
      const res = await tfetch(base + path, { headers: headers() });
      const text = await res.text();
      let data = null;
      try { data = JSON.parse(text); } catch {}
      return { status: res.status, data, text, headers: res.headers };
    },
    post: async (path, body, extra = {}) => {
      const res = await tfetch(base + path, {
        method: "POST",
        headers: headers({ "Content-Type": "application/json", Origin: base, "X-OY-Admin": "1", ...extra }),
        body: typeof body === "string" ? body : JSON.stringify(body),
      });
      const data = await res.json().catch(() => null);
      return { status: res.status, data };
    },
  };
}

export const key = () => "k" + randomUUID().replace(/-/g, "");
