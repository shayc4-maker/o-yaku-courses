#!/usr/bin/env bash
# Guided Morning SANDBOX test. Run from anywhere:   ./scripts/run-sandbox-test.sh        (add --decline for the failure case)
#
# What it does
#   1. Asks for your SANDBOX API key id + secret and a public https URL (a tunnel), stores them in the
#      local, git-ignored .dev.vars (permissions 600). The secret is never printed or passed on a command line.
#   2. Runs  node scripts/sandbox-verify.mjs form  and shows PASS/FAIL checks.
#   3. After you pay with the sandbox test card, asks for the receipt's document id and runs  confirm.
# What it never does: deploy, change Cloudflare, touch production, or enable live payments.
# (sandbox-verify.mjs itself refuses any host except the Morning sandbox.)
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v node >/dev/null 2>&1 || [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 18 ]; then
  echo "Node.js 18 or newer is required (https://nodejs.org)." >&2
  exit 1
fi

DECLINE=""
[ "${1:-}" = "--decline" ] && DECLINE="--decline"

[ -f .dev.vars ] || { cp .dev.vars.example .dev.vars; echo "Created .dev.vars from the example."; }
chmod 600 .dev.vars

# Reads one KEY from .dev.vars (empty if missing). Used only to offer defaults.
current() { node -e '
  const fs=require("fs");const k=process.argv[1];
  for (const l of fs.readFileSync(".dev.vars","utf8").split(/\r?\n/)) {
    const m=l.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/); if (m && m[1]===k && !l.trim().startsWith("#")) { console.log(m[2]); break; }
  }' "$1"; }

# Writes KEY=value into .dev.vars. The value travels in the environment, not in argv.
upsert() { K="$1" VAL="$2" node -e '
  const fs=require("fs");const k=process.env.K, v=process.env.VAL.replace(/[\r\n]/g,"");
  let lines=fs.existsSync(".dev.vars")?fs.readFileSync(".dev.vars","utf8").split(/\r?\n/):[];
  let found=false;
  lines=lines.map(l=>{ if(new RegExp("^\\s*"+k+"\\s*=").test(l)){found=true;return k+"="+v;} return l; });
  if(!found) lines.push(k+"="+v);
  fs.writeFileSync(".dev.vars", lines.join("\n").replace(/\n*$/,"\n"), {mode:0o600});'; }

echo
echo "=== Morning SANDBOX test (no real money) ==="
echo "Use keys from your SANDBOX account. Production keys will not work here."
echo

cur_id="$(current MORNING_API_KEY_ID)"
if [ -n "$cur_id" ]; then
  printf "Sandbox API key id [%s…]: " "${cur_id:0:4}"
else
  printf "Sandbox API key id: "
fi
read -r key_id
key_id="${key_id:-$cur_id}"

cur_secret="$(current MORNING_API_KEY_SECRET)"
if [ -n "$cur_secret" ]; then printf "Sandbox API secret (Enter keeps the saved one): "; else printf "Sandbox API secret: "; fi
read -r -s key_secret
echo
key_secret="${key_secret:-$cur_secret}"

if [ -z "$key_id" ] || [ -z "$key_secret" ]; then
  echo "Both the key id and the secret are required." >&2
  exit 1
fi

echo
echo "Morning must be able to reach this machine. In ANOTHER terminal run:"
echo "    cloudflared tunnel --url http://localhost:8787"
echo "and paste the https://….trycloudflare.com address it prints."
cur_url="$(current PUBLIC_BASE_URL)"
case "$cur_url" in https://*) printf "Public https URL [%s]: " "$cur_url" ;; *) cur_url=""; printf "Public https URL: " ;; esac
read -r public_url
public_url="${public_url:-$cur_url}"
case "$public_url" in https://*) ;; *) echo "A public https URL is required." >&2; exit 1 ;; esac

upsert PAYMENT_MODE morning_sandbox
upsert ALLOW_LIVE_PAYMENTS no
upsert MORNING_AUTH_FLOW oauth
upsert MORNING_API_BASE https://sandbox.d.greeninvoice.co.il/api/v1
upsert MORNING_AUTH_BASE https://api.sandbox.morning.dev
upsert MORNING_GROUP 100
upsert MORNING_API_KEY_ID "$key_id"
upsert MORNING_API_KEY_SECRET "$key_secret"
upsert PUBLIC_BASE_URL "${public_url%/}"
if [ -z "$(current NOTIFY_SIGNING_SECRET)" ] || [ "$(current NOTIFY_SIGNING_SECRET)" = "change-me-to-a-long-random-string" ]; then
  upsert NOTIFY_SIGNING_SECRET "$(node -e 'console.log(require("crypto").randomBytes(24).toString("hex"))')"
fi
unset key_secret cur_secret

echo
echo "Saved to .dev.vars (local only, not committed): PAYMENT_MODE=morning_sandbox, ALLOW_LIVE_PAYMENTS=no, sandbox endpoints."
echo
echo "--- Step 1: create a sandbox payment page and check the request ---"
out="$(mktemp)"
trap 'rm -f "$out"' EXIT
set +e
node scripts/sandbox-verify.mjs form $DECLINE | tee "$out"
code=${PIPESTATUS[0]}
set -e
if [ "$code" -ne 0 ]; then
  echo
  echo "Step 1 failed. Send me the lines above (they contain no keys) and I'll adjust the adapter or the settings." >&2
  exit "$code"
fi
[ -n "$DECLINE" ] && { echo; echo "Now check in the Morning sandbox that the payment failed and NO receipt was created."; exit 0; }

confirm_line="$(grep -o 'confirm OY-[A-Z0-9]\{8\} <documentId> --expect-agorot [0-9]*' "$out" | head -1 || true)"
order_id="$(printf '%s' "$confirm_line" | awk '{print $2}')"
amount="$(printf '%s' "$confirm_line" | awk '{print $5}')"

echo
echo "--- Step 2 (manual) ---"
echo "Open the payment URL above and pay with the TEST card from Morning's sandbox documentation."
echo "Then open the Morning sandbox dashboard, find the new receipt and copy its document id."
printf "Paste the document id (Enter to stop here): "
read -r doc_id
[ -z "$doc_id" ] && { echo "Stopped. Later run: node scripts/sandbox-verify.mjs ${confirm_line}"; exit 0; }

echo
echo "--- Step 3: verify the receipt exactly as the server will ---"
node scripts/sandbox-verify.mjs confirm "$order_id" "$doc_id" --expect-agorot "$amount"
echo
echo "Record the results in docs/SANDBOX-TEST.md. This is not yet a launch approval; see docs/LAUNCH-RUNBOOK.md."
