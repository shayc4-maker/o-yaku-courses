// Cloudflare Access JWT verification for /admin and /api/admin/*.
// https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json/
//
// Every admin request must carry an Access application token (Cf-Access-Jwt-Assertion header, or the
// CF_Authorization cookie) that:
//   – is RS256 and verifies against a key published at <team domain>/cdn-cgi/access/certs
//   – has iss === ACCESS_TEAM_DOMAIN and an aud containing ACCESS_AUD
//   – is within exp / nbf
//   – carries an email that is listed in ADMIN_EMAILS
// Missing configuration blocks the admin area. There is no bypass flag.

const PROD_TEAM_RE = /^https:\/\/[a-z0-9-]+\.cloudflareaccess\.com$/;
// Loopback team domains exist only for local tests: they are accepted solely when the request
// itself is addressed to a loopback host, which never happens behind the production route.
const LOOPBACK_TEAM_RE = /^http:\/\/127\.0\.0\.1:\d{2,5}$/;
const CLOCK_SKEW_S = 60;

export class AccessError extends Error {
  constructor(status, code) {
    super(code);
    this.status = status;
    this.code = code;
  }
}

export function isLoopbackRequest(url) {
  return url.hostname === "127.0.0.1" || url.hostname === "localhost";
}

export function readAccessConfig(env, url) {
  const team = (env.ACCESS_TEAM_DOMAIN || "").trim().replace(/\/$/, "");
  const aud = (env.ACCESS_AUD || "").trim();
  const admins = (env.ADMIN_EMAILS || "")
    .split(",")
    .map((e) => e.trim().toLowerCase())
    .filter(Boolean);
  const teamOk = PROD_TEAM_RE.test(team) || (LOOPBACK_TEAM_RE.test(team) && isLoopbackRequest(url));
  if (!team || !aud || admins.length === 0 || !teamOk) {
    const missing = [!team && "ACCESS_TEAM_DOMAIN", !aud && "ACCESS_AUD", admins.length === 0 && "ADMIN_EMAILS",
      team && !teamOk && "ACCESS_TEAM_DOMAIN (format)"].filter(Boolean);
    return { ok: false, missing };
  }
  return { ok: true, team, aud, admins };
}

function b64urlToBytes(s) {
  if (typeof s !== "string" || !/^[A-Za-z0-9_-]*$/.test(s)) throw new AccessError(403, "token_malformed");
  const b64 = s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4);
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function decodeJsonPart(s) {
  try {
    return JSON.parse(new TextDecoder().decode(b64urlToBytes(s)));
  } catch (e) {
    if (e instanceof AccessError) throw e;
    throw new AccessError(403, "token_malformed");
  }
}

// JWKS cache per team domain. Refetched on expiry or when an unknown kid appears (key rotation).
const jwksCache = new Map(); // team -> { keys: Map(kid -> CryptoKey), fetchedAt }
const JWKS_TTL_MS = 10 * 60 * 1000;

async function fetchKeys(team) {
  const res = await fetch(`${team}/cdn-cgi/access/certs`);
  if (!res.ok) throw new AccessError(503, "access_keys_unavailable");
  const body = await res.json().catch(() => null);
  if (!body || !Array.isArray(body.keys)) throw new AccessError(503, "access_keys_unavailable");
  const keys = new Map();
  for (const jwk of body.keys) {
    if (jwk.kty !== "RSA" || !jwk.kid) continue;
    try {
      const key = await crypto.subtle.importKey(
        "jwk",
        { kty: "RSA", n: jwk.n, e: jwk.e, alg: "RS256", ext: true },
        { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
        false,
        ["verify"],
      );
      keys.set(jwk.kid, key);
    } catch {
      /* skip unusable key */
    }
  }
  const entry = { keys, fetchedAt: Date.now() };
  jwksCache.set(team, entry);
  return entry;
}

async function keyFor(team, kid) {
  let entry = jwksCache.get(team);
  if (!entry || Date.now() - entry.fetchedAt > JWKS_TTL_MS) entry = await fetchKeys(team);
  let key = entry.keys.get(kid);
  if (!key && Date.now() - entry.fetchedAt > 30_000) key = (await fetchKeys(team)).keys.get(kid);
  return key || null;
}

export function tokenFromRequest(request) {
  const header = request.headers.get("Cf-Access-Jwt-Assertion");
  if (header) return header.trim();
  const cookie = request.headers.get("Cookie") || "";
  const m = cookie.match(/(?:^|;\s*)CF_Authorization=([^;]+)/);
  return m ? m[1].trim() : null;
}

// Returns { email } for an authorized admin, or throws AccessError.
export async function verifyAccess(request, env, nowMs = Date.now()) {
  const url = new URL(request.url);
  const cfg = readAccessConfig(env, url);
  if (!cfg.ok) throw new AccessError(503, "admin_not_configured");

  const token = tokenFromRequest(request);
  if (!token) throw new AccessError(401, "token_missing");
  const parts = token.split(".");
  if (parts.length !== 3) throw new AccessError(403, "token_malformed");
  const [h, p, sig] = parts;
  const header = decodeJsonPart(h);
  if (header.alg !== "RS256" || typeof header.kid !== "string") throw new AccessError(403, "token_alg");

  const key = await keyFor(cfg.team, header.kid);
  if (!key) throw new AccessError(403, "token_unknown_key");
  const valid = await crypto.subtle.verify(
    "RSASSA-PKCS1-v1_5",
    key,
    b64urlToBytes(sig),
    new TextEncoder().encode(`${h}.${p}`),
  );
  if (!valid) throw new AccessError(403, "token_signature");

  const claims = decodeJsonPart(p);
  const now = Math.floor(nowMs / 1000);
  if (claims.iss !== cfg.team) throw new AccessError(403, "token_issuer");
  const auds = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
  if (!auds.includes(cfg.aud)) throw new AccessError(403, "token_audience");
  if (typeof claims.exp !== "number" || claims.exp <= now - CLOCK_SKEW_S) throw new AccessError(403, "token_expired");
  if (typeof claims.nbf === "number" && claims.nbf > now + CLOCK_SKEW_S) throw new AccessError(403, "token_not_yet_valid");
  if (typeof claims.iat === "number" && claims.iat > now + CLOCK_SKEW_S) throw new AccessError(403, "token_not_yet_valid");

  const email = typeof claims.email === "string" ? claims.email.trim().toLowerCase() : "";
  if (!email || !cfg.admins.includes(email)) throw new AccessError(403, "not_an_admin");
  return { email };
}

// CSRF guard for state-changing admin requests. The Access cookie is sent automatically by the
// browser, so writes must also prove they come from this origin's admin page:
//   – method POST, JSON body (a cross-site form cannot send application/json without CORS preflight)
//   – Origin equal to this origin; Sec-Fetch-Site, when present, same-origin
//   – custom header X-OY-Admin: 1 (not settable cross-site without preflight)
export function checkCsrf(request) {
  const url = new URL(request.url);
  if (request.method !== "POST") throw new AccessError(405, "method_not_allowed");
  const origin = request.headers.get("Origin");
  if (!origin || origin !== url.origin) throw new AccessError(403, "csrf_origin");
  const site = request.headers.get("Sec-Fetch-Site");
  if (site && site !== "same-origin") throw new AccessError(403, "csrf_site");
  if (request.headers.get("X-OY-Admin") !== "1") throw new AccessError(403, "csrf_header");
  const ct = (request.headers.get("Content-Type") || "").split(";")[0].trim().toLowerCase();
  if (ct !== "application/json") throw new AccessError(415, "json_required");
}
