// The sandbox verification script, exercised against a FAKE Morning on 127.0.0.1.
// Proves the script's own guards and checks. Says nothing about Morning's real behaviour.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { spawn } from "node:child_process";

const PORT = 9841;
const FAKE = `http://127.0.0.1:${PORT}`;
const ORDER = "OY-AAAAAAA2";
const requests = [];
const docs = {};
let server;

before(async () => {
  server = http.createServer((req, res) => {
    let body = "";
    req.on("data", (c) => (body += c));
    req.on("end", () => {
      requests.push(`${req.method} ${req.url}`);
      const send = (code, obj) => { res.writeHead(code, { "Content-Type": "application/json" }); res.end(JSON.stringify(obj)); };
      if (req.url === "/idp/v1/oauth/token") return send(200, { accessToken: "fake", expiresAt: Math.floor(Date.now() / 1000) + 3600 });
      if (req.headers.authorization !== "Bearer fake") return send(401, {});
      if (req.url === "/payments/form") return send(200, { errorCode: 0, url: `${FAKE}/hosted/1` });
      const m = req.url.match(/^\/documents\/(.+)$/);
      if (m) return docs[m[1]] ? send(200, docs[m[1]]) : send(404, {});
      send(404, {});
    });
  });
  await new Promise((ok) => server.listen(PORT, "127.0.0.1", ok));
});
after(() => server.close());

const baseEnv = {
  SANDBOX_VERIFY_SELFTEST: "1", PAYMENT_MODE: "morning_sandbox", ALLOW_LIVE_PAYMENTS: "no", MORNING_API_BASE: FAKE, MORNING_AUTH_BASE: FAKE,
  MORNING_AUTH_FLOW: "oauth", MORNING_API_KEY_ID: "testid1234", MORNING_API_KEY_SECRET: "testsecret", MORNING_GROUP: "100",
  PUBLIC_BASE_URL: "http://127.0.0.1:9", NOTIFY_SIGNING_SECRET: "selftest-notify-secret-0123456789",
};

function run(args, env = {}, { selfTest = true } = {}) {
  return new Promise((resolve) => {
    const e = { ...process.env, ...baseEnv, ...env };
    if (!selfTest) delete e.SANDBOX_VERIFY_SELFTEST;
    const child = spawn(process.execPath, ["scripts/sandbox-verify.mjs", ...args], { env: e });
    let out = "";
    child.stdout.on("data", (d) => (out += d));
    child.stderr.on("data", (d) => (out += d));
    child.on("close", (code) => resolve({ code, out }));
  });
}

test("refuses production and unsafe configuration before any request is sent", async () => {
  const cases = {
    "live API host": { MORNING_API_BASE: "https://api.greeninvoice.co.il/api/v1" },
    "live auth host": { MORNING_AUTH_BASE: "https://api.morning.co" },
    "lookalike host": { MORNING_API_BASE: "https://sandbox.d.greeninvoice.co.il.evil.example/api/v1" },
    "http sandbox host": { MORNING_API_BASE: "http://sandbox.d.greeninvoice.co.il/api/v1" },
    "mock mode": { PAYMENT_MODE: "mock" },
    "live mode": { PAYMENT_MODE: "morning_live" },
    "live payments on": { ALLOW_LIVE_PAYMENTS: "yes" },
    "no keys": { MORNING_API_KEY_ID: "", MORNING_API_KEY_SECRET: "" },
    "no public https url": { PUBLIC_BASE_URL: "http://example.com" },
    "weak notify secret": { NOTIFY_SIGNING_SECRET: "short" },
  };
  const before = requests.length;
  for (const [name, env] of Object.entries(cases)) {
    const r = await run(["form"], env);
    assert.equal(r.code, 2, `${name}: ${r.out}`);
    assert.match(r.out, /REFUSED/, name);
  }
  assert.equal(requests.length, before, "no request reached any server");
});

test("loopback hosts are accepted only with the self-test flag", async () => {
  const r = await run(["form"], {}, { selfTest: false });
  assert.equal(r.code, 2);
  assert.match(r.out, /MORNING_API_BASE must be https:\/\/sandbox\.d\.greeninvoice\.co\.il/);
});

test("form: builds a fictional multi-line order, checks the request, prints the hosted URL and the manual steps", async () => {
  const r = await run(["form"]);
  assert.equal(r.code, 0, r.out);
  assert.match(r.out, /2× חולצת O‑Yaku, 1× חבילת 10 שקי אקדמה, 1× מטר רבוע/);
  assert.match(r.out, /= ₪3,140 incl\. VAT/);
  for (const check of ["authentication", "payment page created", "request amount equals server-priced order", "income lines sum to the order total",
    "payment group sent", "order id is in custom", "notifyUrl carries the signed order id", "hosted payment URL is https"]) {
    assert.match(r.out, new RegExp(`PASS +${check}`), check);
  }
  assert.match(r.out, new RegExp(`${FAKE}/hosted/1`));
  assert.match(r.out, /confirm OY-[A-Z0-9]{8} <documentId> --expect-agorot 314000/);
  assert.ok(!r.out.includes("testsecret"), "secret never printed");
});

test("form --decline builds an order above the sandbox limit and says the payment must fail", async () => {
  const r = await run(["form", "--decline"]);
  assert.equal(r.code, 0, r.out);
  assert.match(r.out, /= ₪5,600 incl\. VAT/);
  assert.match(r.out, /MUST fail/);
});

test("form reports failure when authentication fails", async () => {
  const r = await run(["form"], { MORNING_AUTH_BASE: `http://127.0.0.1:${PORT}/nope` });
  assert.equal(r.code, 1);
  assert.match(r.out, /FAIL +authentication/);
});

const goodDoc = (over = {}) => ({
  id: "doc-sandbox-0001", type: 320, status: 1, currency: "ILS", amount: 3140, vat: 479.15, vatType: 0,
  remarks: `הזמנה ${ORDER}`, description: "", custom: ORDER,
  income: [{ description: "x", quantity: 1, price: 3140, vatType: 1 }],
  payment: [{ type: 3, price: 3140, currency: "ILS", transactionId: "tx-1" }], ...over,
});

test("confirm: a correct receipt passes every check and prints the document", async () => {
  docs["doc-sandbox-0001"] = goodDoc();
  const r = await run(["confirm", ORDER, "doc-sandbox-0001", "--expect-agorot", "314000"]);
  assert.equal(r.code, 0, r.out);
  assert.match(r.out, /PASS +adapter confirms the payment from the document/);
  assert.match(r.out, /PASS +paid amount equals the order total/);
  assert.match(r.out, /PASS +document total equals the order total/);
  assert.match(r.out, /"transactionId": "tx-1"/);
});

test("confirm: wrong expected amount, other order, cancelled receipt, unpaid receipt and unknown document all fail", async () => {
  docs["doc-sandbox-0002"] = goodDoc({ id: "doc-sandbox-0002" });
  docs["doc-sandbox-0003"] = goodDoc({ id: "doc-sandbox-0003", remarks: "הזמנה OY-BBBBBBB2", custom: "OY-BBBBBBB2" });
  docs["doc-sandbox-0004"] = goodDoc({ id: "doc-sandbox-0004", status: 4 });
  docs["doc-sandbox-0005"] = goodDoc({ id: "doc-sandbox-0005", payment: [] });
  const cases = [
    ["doc-sandbox-0002", "300000", /FAIL +paid amount equals the order total/],
    ["doc-sandbox-0003", "314000", /FAIL +adapter confirms.*document_does_not_reference_order/],
    ["doc-sandbox-0004", "314000", /FAIL +adapter confirms.*document_cancelled_or_unverified_status/],
    ["doc-sandbox-0005", "314000", /FAIL +adapter confirms.*document_has_no_verified_online_payments/],
    ["doc-sandbox-9999", "314000", /FAIL +adapter confirms.*document_lookup_http_404/],
  ];
  for (const [doc, amount, pattern] of cases) {
    const r = await run(["confirm", ORDER, doc, "--expect-agorot", amount]);
    assert.equal(r.code, 1, `${doc}: ${r.out}`);
    assert.match(r.out, pattern, doc);
  }
});

test("confirm validates its arguments", async () => {
  for (const args of [["confirm"], ["confirm", "bad", "doc-sandbox-0001", "--expect-agorot", "1"], ["confirm", ORDER, "doc-sandbox-0001"]]) {
    assert.equal((await run(args)).code, 2, args.join(" "));
  }
});
