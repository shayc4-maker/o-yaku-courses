// Entry point for everything under /admin and /api/admin. Authentication runs first, for every
// path and method, before any handler or database access. Admin UI files are bundled into the
// Worker (not in ./public), so the static-asset layer has nothing to serve for these paths.
import { verifyAccess, checkCsrf, AccessError } from "./access.js";
import * as api from "./api.js";
import { json, SECURITY_HEADERS } from "../util.js";
import indexHtml from "../../admin-ui/index.html";
import appJs from "../../admin-ui/admin.client.js";
import appCss from "../../admin-ui/admin.css";

export function isAdminPath(pathname) {
  return pathname === "/admin" || pathname.startsWith("/admin/") || pathname === "/api/admin" || pathname.startsWith("/api/admin/");
}

const NO_STORE = { "Cache-Control": "no-store", ...SECURITY_HEADERS };

function asset(body, type) {
  return new Response(body, { headers: { "Content-Type": type, ...NO_STORE } });
}

const BLOCKED_TEXT = {
  admin_not_configured: "אזור הניהול עדיין לא הוגדר (Cloudflare Access). הגישה חסומה.",
  token_missing: "נדרשת התחברות דרך Cloudflare Access.",
  not_an_admin: "למשתמש הזה אין הרשאת ניהול.",
};

function blockedPage(err) {
  const text = BLOCKED_TEXT[err.code] || "הגישה נדחתה.";
  return new Response(
    `<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>ניהול · גישה חסומה</title><link rel="stylesheet" href="/styles.css"></head>
<body><main class="wrap narrow page-simple"><h1 class="h2">ניהול</h1><p>${text}</p></main></body></html>`,
    { status: err.status, headers: { "Content-Type": "text/html; charset=utf-8", ...NO_STORE } },
  );
}

// Responding without reading a request body can break keep-alive connections for the next
// request. Drain small unread bodies (never large ones) before returning an error.
async function drained(request, response) {
  if (request.body && !request.bodyUsed && Number(request.headers.get("Content-Length") || 0) <= 64 * 1024) {
    await request.arrayBuffer().catch(() => {});
  }
  return response;
}

export async function handleAdmin(request, env, url) {
  const res = await handleAdminInner(request, env, url);
  return drained(request, res);
}

async function handleAdminInner(request, env, url) {
  const { pathname } = url;
  const isApi = pathname.startsWith("/api/admin");
  let admin;
  try {
    admin = await verifyAccess(request, env);
  } catch (err) {
    if (!(err instanceof AccessError)) throw err;
    console.warn("admin access denied", err.code); // reason code only — no token, email or IP
    return isApi ? json({ error: err.code }, err.status) : blockedPage(err);
  }

  try {
    if (!isApi) {
      if (request.method !== "GET") return json({ error: "method_not_allowed" }, 405);
      if (pathname === "/admin" || pathname === "/admin/") return asset(indexHtml, "text/html; charset=utf-8");
      if (pathname === "/admin/admin.js") return asset(appJs, "text/javascript; charset=utf-8");
      if (pathname === "/admin/admin.css") return asset(appCss, "text/css; charset=utf-8");
      return json({ error: "not_found" }, 404);
    }

    const route = pathname.slice("/api/admin".length);
    if (request.method === "GET") {
      if (route === "/me") return await api.me(request, env, admin);
      if (route === "/summary") return await api.summary(request, env);
      if (route === "/orders") return await api.listOrders(request, env);
      if (route === "/buyers") return await api.listBuyers(request, env);
      if (route === "/products") return await api.products(request, env);
      let m = route.match(/^\/orders\/([^/]+)$/);
      if (m) return await api.getOrderAdmin(request, env, m[1]);
      m = route.match(/^\/buyers\/([^/]+)$/);
      if (m) return await api.getBuyer(request, env, m[1]);
      m = route.match(/^\/export\/(buyers|orders|balances)\.csv$/);
      if (m) return await api.exportCsv(request, env, m[1]);
      return json({ error: "not_found" }, 404);
    }
    if (request.method === "POST") {
      checkCsrf(request);
      let m = route.match(/^\/orders\/([^/]+)\/redemptions$/);
      if (m) return await api.redeem(request, env, admin, m[1]);
      m = route.match(/^\/redemptions\/([^/]+)\/corrections$/);
      if (m) return await api.correct(request, env, admin, m[1]);
      m = route.match(/^\/orders\/([^/]+)\/cancel-voucher$/);
      if (m) return await api.cancelVoucher(request, env, admin, m[1]);
      m = route.match(/^\/orders\/([^/]+)\/notes$/);
      if (m) return await api.addNote(request, env, admin, m[1]);
      return json({ error: "not_found" }, 404);
    }
    return json({ error: "method_not_allowed" }, 405);
  } catch (err) {
    if (err instanceof AccessError) return json({ error: err.code }, err.status);
    if (err instanceof api.ApiError) return json({ error: err.code, ...err.extra }, err.status);
    console.error("admin error", err?.message);
    return json({ error: "server_error" }, 500);
  }
}
