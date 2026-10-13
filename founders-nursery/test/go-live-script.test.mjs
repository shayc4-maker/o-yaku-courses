// scripts/go-live-test.sh is the one script that can turn real payments on, so its safety gating is tested
// with FAKE `npx` and `curl` commands: nothing ever reaches Cloudflare or Morning.
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, copyFileSync, cpSync, readFileSync, rmSync, chmodSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const ACCOUNT = "f6748e8d1bcd76c6d4234fd177d488a9";

const NPX = `#!/bin/bash
echo "npx $*" >> "$SHIM_LOG"
shift 2
case "$1" in
  whoami) echo "Account ID | $SHIM_ACCOUNT" ;;
  login) ;;
  secret)
    if [ "$2" = "list" ]; then echo "$SHIM_SECRETS"; fi
    # Like wrangler, read the value from stdin so the script's pipe does not break.
    if [ "$2" = "put" ]; then cat > /dev/null; fi ;;
  d1)
    if [ "$2" = "export" ]; then
      while [ $# -gt 0 ]; do [ "$1" = "--output" ] && : > "$2"; shift; done
    fi ;;
  deploy) touch "$SHIM_DIR/deployed" ;;
esac
exit 0
`;

const CURL = `#!/bin/bash
out=""; url=""; code=0
while [ $# -gt 0 ]; do
  case "$1" in
    -o) out="$2"; shift ;;
    -w) code=1; shift ;;
    http*) url="$1" ;;
  esac
  shift
done
path="\${url#https://nursery.o-yaku.com}"
case "$path" in
  /api/config) body='{"liveCharges":true,"testProduct":true}' ;;
  /api/admin/me) [ "$code" = 1 ] && { printf 503; exit 0; }; body='{}' ;;
  /) f=public/index.html ;;
  /order) f=public/order.html ;;
  /terms) f=public/terms.html ;;
  /*) f="public\${path}" ;;
esac
if [ -n "\${f:-}" ]; then
  [ -f "$f" ] || exit 22
  body="$(cat "$f")"
  if [ -n "\${SHIM_LIVE_DIFF:-}" ] && [ "$f" = "public/app.js" ]; then body="$body
// live-only change"; fi
fi
if [ -n "$out" ]; then
  if [ "$out" = "/dev/null" ]; then :; else printf '%s' "$body" > "$out"; fi
else
  printf '%s' "$body"
fi
exit 0
`;

function setup() {
  const root = mkdtempSync(join(tmpdir(), "oy-golive-"));
  const proj = join(root, "proj");
  const bin = join(root, "bin");
  mkdirSync(join(proj, "scripts"), { recursive: true });
  mkdirSync(join(proj, "node_modules"));
  mkdirSync(bin);
  copyFileSync("scripts/go-live-test.sh", join(proj, "scripts/go-live-test.sh"));
  copyFileSync("wrangler.jsonc", join(proj, "wrangler.jsonc"));
  cpSync("public", join(proj, "public"), { recursive: true });
  writeFileSync(join(bin, "npx"), NPX);
  writeFileSync(join(bin, "curl"), CURL);
  chmodSync(join(bin, "npx"), 0o755);
  chmodSync(join(bin, "curl"), 0o755);
  return { root, proj, bin, log: join(root, "log.txt") };
}

function run(args, input, { secrets = "[]", account = ACCOUNT, liveDiff = false } = {}) {
  const s = setup();
  writeFileSync(s.log, "");
  const r = spawnSync("bash", [join(s.proj, "scripts/go-live-test.sh"), ...args], {
    input,
    cwd: s.root,
    encoding: "utf8",
    env: { ...process.env, PATH: `${s.bin}:${process.env.PATH}`, SHIM_LOG: s.log, SHIM_DIR: s.root, SHIM_ACCOUNT: account, SHIM_SECRETS: secrets, ...(liveDiff ? { SHIM_LIVE_DIFF: "1" } : {}) },
  });
  const log = readFileSync(s.log, "utf8");
  const deployed = existsSync(join(s.root, "deployed"));
  rmSync(s.root, { recursive: true, force: true });
  return { ...r, log, deployed };
}

const CHANGES = /secret put|d1 export|migrations apply|deploy/;

test("anything other than LIVE cancels, and nothing in Cloudflare is touched", () => {
  for (const answer of ["", "live", "yes", "nope"]) {
    const r = run([], `${answer}\n`);
    assert.equal(r.status, 1, `answer "${answer}"`);
    assert.match(r.stderr, /Cancelled. Nothing was changed/);
    assert.doesNotMatch(r.log, CHANGES, `answer "${answer}" changed something:\n${r.log}`);
  }
});

test("a different Cloudflare account stops the script before any change", () => {
  const r = run([], "LIVE\n", { account: "0".repeat(32) });
  assert.equal(r.status, 1);
  assert.match(r.stderr, /different Cloudflare account/);
  assert.doesNotMatch(r.log, CHANGES);
});

test("LIVE: stores missing secrets, backs up, migrates, then deploys live with the test product — in that order", () => {
  const r = run([], "LIVE\n");
  assert.equal(r.status, 0, r.stderr + r.stdout);
  const lines = r.log.split("\n");
  const at = (re) => lines.findIndex((l) => re.test(l));
  const [put1, put2, put3, exp, mig, dep] = [/secret put NOTIFY_SIGNING_SECRET/, /secret put MORNING_API_KEY_ID/, /secret put MORNING_API_KEY_SECRET/, /d1 export/, /migrations apply/, /wrangler deploy|\bdeploy\b/].map(at);
  for (const [name, i] of Object.entries({ put1, put2, put3, exp, mig, dep })) assert.ok(i >= 0, `${name} missing:\n${r.log}`);
  assert.ok(put1 < exp && put2 < exp && put3 < exp && exp < mig && mig < dep, "wrong order:\n" + r.log);
  const deploy = lines[dep];
  for (const v of ["PAYMENT_MODE:morning_live", "ALLOW_LIVE_PAYMENTS:yes", "LIVE_TEST_PRODUCT:yes", "MORNING_API_BASE:https://api.greeninvoice.co.il/api/v1",
    "MORNING_AUTH_BASE:https://api.morning.co", "MORNING_AUTH_FLOW:oauth", "MORNING_GROUP:100", "PUBLIC_BASE_URL:https://nursery.o-yaku.com"]) {
    assert.ok(deploy.includes(`--var ${v}`), `${v} missing in: ${deploy}`);
  }
  assert.match(r.stdout, /LIVE TEST IS ON/);
  assert.match(r.stdout, /nursery\.o-yaku\.com\/\?test=1/);
  assert.match(r.stdout, /Admin API without login answers HTTP 503/);
});

test("secrets that already exist are not overwritten", () => {
  const r = run([], "LIVE\n", { secrets: '[{"name":"MORNING_API_KEY_ID"},{"name":"MORNING_API_KEY_SECRET"},{"name":"NOTIFY_SIGNING_SECRET"}]' });
  assert.equal(r.status, 0, r.stderr);
  assert.doesNotMatch(r.log, /secret put/);
  assert.match(r.log, /deploy/);
});

test("files that differ from the live site are listed before the confirmation, and a snapshot is kept", () => {
  const r = run([], "nope\n", { liveDiff: true });
  assert.match(r.stdout, /will be REPLACED/);
  assert.match(r.stdout, /app\.js \(\d+ changed lines\)/);
  assert.match(r.stdout, /live-snapshot-/);
  assert.doesNotMatch(r.log, CHANGES);
});

test("--revert needs REVERT, then deploys with the repository defaults only (no --var)", () => {
  assert.doesNotMatch(run(["--revert"], "yes\n").log, /deploy/);
  const r = run(["--revert"], "REVERT\n");
  assert.equal(r.status, 0, r.stderr);
  const dep = r.log.split("\n").find((l) => /\bdeploy\b/.test(l));
  assert.ok(dep && !dep.includes("--var"), dep);
  assert.doesNotMatch(r.log, /secret put|d1 export|migrations apply/);
});

test("--remove-test-product keeps live on and switches only the test product off", () => {
  assert.doesNotMatch(run(["--remove-test-product"], "no\n").log, /deploy/);
  const r = run(["--remove-test-product"], "LIVE\n");
  assert.equal(r.status, 0, r.stderr);
  const dep = r.log.split("\n").find((l) => /\bdeploy\b/.test(l));
  assert.ok(dep.includes("--var LIVE_TEST_PRODUCT:no") && dep.includes("--var PAYMENT_MODE:morning_live"), dep);
});

test("unknown options are rejected", () => {
  const r = run(["--yolo"], "");
  assert.equal(r.status, 2);
  assert.doesNotMatch(r.log, CHANGES);
});
