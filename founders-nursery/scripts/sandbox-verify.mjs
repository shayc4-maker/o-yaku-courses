#!/usr/bin/env node
// Morning SANDBOX verification. Uses the project's real adapter (src/payments/morning.js) against the
// Morning sandbox only, with a fictional order. It cannot be pointed at production:
// the API and auth hosts must be exactly the sandbox hosts, PAYMENT_MODE must be morning_sandbox, and
// ALLOW_LIVE_PAYMENTS must not be "yes". Anything else exits before a single request is sent.
//
//   node scripts/sandbox-verify.mjs form [--decline]
//   node scripts/sandbox-verify.mjs confirm <orderId> <documentId> --expect-agorot <n>
//
// Config comes from the environment, then from .dev.vars (never printed):
//   PAYMENT_MODE=morning_sandbox  MORNING_API_BASE  MORNING_AUTH_BASE  MORNING_AUTH_FLOW=oauth
//   MORNING_API_KEY_ID  MORNING_API_KEY_SECRET  MORNING_GROUP  PUBLIC_BASE_URL (https)  NOTIFY_SIGNING_SECRET
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { createHmac } from "node:crypto";
import { priceCart } from "../public/catalog.js";
import { newOrderId } from "../src/util.js";
import * as morning from "../src/payments/morning.js";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SANDBOX_API_HOST = "sandbox.d.greeninvoice.co.il";
const SANDBOX_AUTH_HOST = "api.sandbox.morning.dev";
// Morning's sandbox turns any card payment above this amount into a simulated failure.
const SANDBOX_DECLINE_ABOVE_AGOROT = 500000;

const results = [];
const record = (status, name, detail = "") => {
  results.push({ status, name });
  console.log(`${status.padEnd(6)} ${name}${detail ? `  — ${detail}` : ""}`);
};
const fail = (msg) => {
  console.error(`REFUSED: ${msg}`);
  process.exit(2);
};

function loadConfig() {
  const cfg = {};
  try {
    for (const line of readFileSync(join(ROOT, ".dev.vars"), "utf8").split(/\r?\n/)) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
      if (m && !line.trim().startsWith("#")) cfg[m[1]] = m[2].replace(/^["']|["']$/g, "");
    }
  } catch {
    /* no .dev.vars: environment only */
  }
  for (const k of ["PAYMENT_MODE", "ALLOW_LIVE_PAYMENTS", "MORNING_API_BASE", "MORNING_AUTH_BASE", "MORNING_AUTH_FLOW",
    "MORNING_API_KEY_ID", "MORNING_API_KEY_SECRET", "MORNING_GROUP", "MORNING_PLUGIN_ID", "MORNING_SEND_INCOME_LINES",
    "MORNING_INCOME_VAT_TYPE", "PUBLIC_BASE_URL", "NOTIFY_SIGNING_SECRET"]) {
    if (process.env[k] !== undefined) cfg[k] = process.env[k];
  }
  return cfg;
}

// The only gate between this script and a real account. Allow-list, not block-list.
function guard(cfg) {
  const selfTest = process.env.SANDBOX_VERIFY_SELFTEST === "1";
  const hostOk = (value, sandboxHost) => {
    let u;
    try { u = new URL(value); } catch { return false; }
    if (u.protocol === "https:" && u.hostname === sandboxHost) return true;
    // Local self-test against a fake server on this machine. Loopback can never be a real Morning account.
    return selfTest && u.protocol === "http:" && u.hostname === "127.0.0.1";
  };
  if (cfg.PAYMENT_MODE !== "morning_sandbox") fail(`PAYMENT_MODE must be "morning_sandbox" (got "${cfg.PAYMENT_MODE || ""}")`);
  if (cfg.ALLOW_LIVE_PAYMENTS === "yes") fail('ALLOW_LIVE_PAYMENTS is "yes". This script never runs with live payments enabled');
  if (!hostOk(cfg.MORNING_API_BASE || "", SANDBOX_API_HOST)) fail(`MORNING_API_BASE must be https://${SANDBOX_API_HOST}/api/v1`);
  if ((cfg.MORNING_AUTH_FLOW || "oauth") === "oauth" && !hostOk(cfg.MORNING_AUTH_BASE || "", SANDBOX_AUTH_HOST)) {
    fail(`MORNING_AUTH_BASE must be https://${SANDBOX_AUTH_HOST}`);
  }
  if (!cfg.MORNING_API_KEY_ID || !cfg.MORNING_API_KEY_SECRET) fail("MORNING_API_KEY_ID / MORNING_API_KEY_SECRET are empty (use SANDBOX keys)");
  if (!cfg.NOTIFY_SIGNING_SECRET || cfg.NOTIFY_SIGNING_SECRET.length < 16) fail("NOTIFY_SIGNING_SECRET is missing or too short");
  const base = cfg.PUBLIC_BASE_URL || "";
  if (!(base.startsWith("https://") || (selfTest && base.startsWith("http://127.0.0.1")))) {
    fail("PUBLIC_BASE_URL must be a public https URL that Morning can reach (e.g. a Cloudflare tunnel)");
  }
}

// Records every request the adapter makes without touching its behaviour. Secrets are never logged.
const calls = [];
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, init = {}) => {
  const res = await realFetch(url, init);
  const u = new URL(url);
  const entry = { method: init.method || "GET", path: u.pathname, status: res.status };
  if (u.pathname.endsWith("/payments/form") && typeof init.body === "string") entry.body = JSON.parse(init.body);
  calls.push(entry);
  return res;
};

const shekels = (a) => `₪${(a / 100).toLocaleString("en-US")}`;

async function runForm(cfg, { decline }) {
  const items = decline ? [{ id: "akadama-10", qty: 4 }] : [{ id: "tshirt", qty: 2 }, { id: "akadama-10", qty: 1 }, { id: "nursery-sqm-year", qty: 1 }];
  const priced = priceCart(items);
  const order = {
    id: newOrderId(),
    currency: priced.currency,
    totalAgorot: priced.totalAgorot,
    customer: { name: "Sandbox Test", email: "sandbox-test@example.com", phone: "050-0000000" },
    lines: priced.lines,
  };
  console.log(`Fictional order ${order.id}: ${priced.lines.map((l) => `${l.quantity}× ${l.name}`).join(", ")} = ${shekels(order.totalAgorot)} incl. VAT\n`);

  const base = cfg.PUBLIC_BASE_URL.replace(/\/$/, "");
  const q = `order=${order.id}&t=${"0".repeat(48)}`;
  const sig = createHmac("sha256", cfg.NOTIFY_SIGNING_SECRET).update(order.id).digest("hex");
  let page;
  try {
    page = await morning.createPaymentPage(cfg, order, {
      successUrl: `${base}/pay/return?${q}&result=success`,
      failureUrl: `${base}/pay/return?${q}&result=failure`,
      notifyUrl: `${base}/api/morning/notify?order=${order.id}&sig=${sig}`,
    });
  } catch (err) {
    const auth = calls.find((c) => /oauth\/token$|account\/token$/.test(c.path));
    record(auth && auth.status === 200 ? "PASS" : "FAIL", "authentication", auth ? `HTTP ${auth.status}` : "no request made");
    record("FAIL", "payment page created", err.message);
    return;
  }

  const auth = calls.find((c) => /oauth\/token$|account\/token$/.test(c.path));
  record(auth && auth.status === 200 ? "PASS" : "FAIL", "authentication", auth ? `HTTP ${auth.status}` : "no token request seen");
  const form = calls.find((c) => c.path.endsWith("/payments/form"));
  record(form?.status === 200 ? "PASS" : "FAIL", "payment page created", `HTTP ${form?.status}`);

  const body = form?.body;
  if (body) {
    const incomeAgorot = (body.income || []).reduce((n, i) => n + Math.round(i.price * 100) * i.quantity, 0);
    record(Math.round(body.amount * 100) === order.totalAgorot ? "PASS" : "FAIL", "request amount equals server-priced order", `${body.amount} ILS`);
    record(incomeAgorot === order.totalAgorot ? "PASS" : "FAIL", "income lines sum to the order total (VAT included)", `${incomeAgorot / 100}`);
    record(body.group != null ? "PASS" : "FAIL", "payment group sent", `group ${body.group}`);
    record(body.custom === order.id && body.remarks.includes(order.id) ? "PASS" : "FAIL", "order id is in custom + remarks (needed for read-back)");
    record(/\/api\/morning\/notify\?order=OY-[A-Z0-9]{8}&sig=[0-9a-f]{64}$/.test(body.notifyUrl) ? "PASS" : "FAIL", "notifyUrl carries the signed order id");
  }
  record(page.paymentUrl.startsWith("https://") || page.paymentUrl.startsWith("http://127.0.0.1") ? "PASS" : "FAIL", "hosted payment URL is https", new URL(page.paymentUrl).origin);

  console.log(`\nOpen this URL in a browser and pay with the test card from Morning's sandbox documentation:\n  ${page.paymentUrl}\n`);
  if (decline) {
    console.log(`MANUAL: this order is ${shekels(order.totalAgorot)}, above the sandbox's ₪5,000 limit. The payment MUST fail.`);
    console.log("        Then check in the Morning sandbox dashboard that NO receipt was created. Record the result in docs/SANDBOX-TEST.md.");
  } else {
    console.log("MANUAL: complete the payment. Confirm you were returned to the success URL.");
    console.log("        Then open the Morning sandbox dashboard, find the new receipt, and copy its document id. Run:");
    console.log(`        node scripts/sandbox-verify.mjs confirm ${order.id} <documentId> --expect-agorot ${order.totalAgorot}`);
  }
}

async function sandboxToken(cfg) {
  const oauth = (cfg.MORNING_AUTH_FLOW || "oauth") === "oauth";
  const res = await realFetch(oauth ? `${cfg.MORNING_AUTH_BASE}/idp/v1/oauth/token` : `${cfg.MORNING_API_BASE}/account/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(oauth
      ? { grant_type: "client_credentials", client_id: cfg.MORNING_API_KEY_ID, client_secret: cfg.MORNING_API_KEY_SECRET }
      : { id: cfg.MORNING_API_KEY_ID, secret: cfg.MORNING_API_KEY_SECRET }),
  });
  const b = await res.json().catch(() => ({}));
  return b.accessToken || b.access_token || b.token || null;
}

async function runConfirm(cfg, orderId, documentId, expectAgorot) {
  // 1. The adapter's own verdict, exactly as the Worker would reach it.
  const verdict = await morning.confirmPayment(cfg, orderId, { documentId });
  record(verdict.confirmed ? "PASS" : "FAIL", "adapter confirms the payment from the document", verdict.confirmed ? "" : `reason: ${verdict.reason}`);
  if (verdict.confirmed) {
    record(verdict.amountAgorot === expectAgorot ? "PASS" : "FAIL", "paid amount equals the order total", `${verdict.amountAgorot / 100} vs ${expectAgorot / 100} ILS`);
    record(verdict.currency === "ILS" ? "PASS" : "FAIL", "currency is ILS", verdict.currency);
    record(verdict.transactionId ? "PASS" : "WARN", "transaction id present", verdict.transactionId ? "" : "payment row has no transactionId; reconcile by document id");
  }

  // 2. Independent read of the document, printed so real response differences can be recorded.
  const token = await sandboxToken(cfg);
  if (!token) return record("WARN", "independent document read", "could not obtain a token");
  const res = await realFetch(`${cfg.MORNING_API_BASE}/documents/${encodeURIComponent(documentId)}`, { headers: { Authorization: `Bearer ${token}` } });
  const doc = await res.json().catch(() => null);
  if (!res.ok || !doc) return record("WARN", "independent document read", `HTTP ${res.status}`);
  console.log("\nDocument as returned by Morning (record anything that differs from the docs):");
  console.log(JSON.stringify({
    id: doc.id, type: doc.type, status: doc.status, currency: doc.currency, amount: doc.amount, vat: doc.vat, vatType: doc.vatType,
    remarks: doc.remarks, description: doc.description, custom: doc.custom,
    income: (doc.income || []).map((i) => ({ description: i.description, quantity: i.quantity, price: i.price, vatType: i.vatType })),
    payment: (doc.payment || []).map((p) => ({ type: p.type, price: p.price, currency: p.currency, transactionId: p.transactionId })),
  }, null, 2));
  const vatIncluded = doc.vatType === 0 || (doc.income || []).every((i) => i.vatType === 1 || i.vatType === 0);
  record(Math.round(doc.amount * 100) === expectAgorot ? "PASS" : "FAIL", "document total equals the order total (no double VAT)", `${doc.amount} ILS`);
  record(vatIncluded ? "INFO" : "WARN", "VAT mode on the lines", "check the printed income rows against the receipt PDF");
}

async function main() {
  const [mode, ...rest] = process.argv.slice(2);
  const cfg = loadConfig();
  if (!["form", "confirm"].includes(mode)) fail("usage: sandbox-verify.mjs form [--decline] | confirm <orderId> <documentId> --expect-agorot <n>");
  guard(cfg);
  record("PASS", "safety guard", `sandbox only · key ${cfg.MORNING_API_KEY_ID.slice(0, 4)}…`);

  if (mode === "form") await runForm(cfg, { decline: rest.includes("--decline") });
  else {
    const [orderId, documentId] = rest;
    const i = rest.indexOf("--expect-agorot");
    const expect = i >= 0 ? Number(rest[i + 1]) : NaN;
    if (!/^OY-[23456789A-HJ-NP-Z]{8}$/.test(orderId || "") || !/^[A-Za-z0-9-]{8,64}$/.test(documentId || "") || !Number.isInteger(expect) || expect <= 0) {
      fail("confirm needs <orderId> <documentId> --expect-agorot <integer>");
    }
    await runConfirm(cfg, orderId, documentId, expect);
  }

  const failed = results.filter((r) => r.status === "FAIL").length;
  console.log(`\n${results.filter((r) => r.status === "PASS").length} passed, ${failed} failed, ${results.filter((r) => r.status === "WARN").length} warnings.`);
  process.exit(failed ? 1 : 0);
}

main().catch((err) => {
  console.error("ERROR:", err.message);
  process.exit(1);
});
