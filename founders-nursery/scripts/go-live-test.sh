#!/usr/bin/env bash
# Guided LIVE payment test with a temporary ₪1 product. Run from anywhere:
#
#   ./scripts/go-live-test.sh                    check everything, then (after you type LIVE) turn live payments + the ₪1 test product ON
#   ./scripts/go-live-test.sh --remove-test-product   keep live payments ON, remove the ₪1 test product
#   ./scripts/go-live-test.sh --revert                turn live payments and the test product OFF (back to the safe test mode)
#
# REAL MONEY: while live mode is on, anyone who has the site link can pay for real. Do not share the link
# until you decide to launch, keep the test short, and run --revert (or --remove-test-product) when done.
# Nothing is changed in Cloudflare until you type LIVE (or confirm the revert) at the prompt.
set -euo pipefail
cd "$(dirname "$0")/.."

SITE="https://nursery.o-yaku.com"
DB="oyaku-founders-orders"
MODE="live"
case "${1:-}" in
  "") MODE="live" ;;
  --remove-test-product) MODE="remove-test" ;;
  --revert) MODE="revert" ;;
  *) echo "Unknown option: $1" >&2; exit 2 ;;
esac

say() { printf '\n== %s ==\n' "$1"; }
die() { echo "STOP: $1" >&2; exit 1; }
# The question goes to stderr so it is shown even when the answer is captured with $( ).
ask() { local a; printf '%s ' "$1" >&2; read -r a || a=""; printf '%s' "$a"; }

command -v node >/dev/null 2>&1 || die "Node.js 18+ is required (https://nodejs.org)"
[ "$(node -p 'process.versions.node.split(".")[0]')" -ge 18 ] || die "Node.js 18 or newer is required"
command -v curl >/dev/null 2>&1 || die "curl is required"

[ -d node_modules ] || { say "Installing dependencies (first run only)"; npm install --no-audit --no-fund; }
WR="npx --no-install wrangler"

# ---- variables that make a deploy "live". Everything else comes from wrangler.jsonc.
live_vars() {
  printf '%s\n' \
    "--var" "PAYMENT_MODE:morning_live" \
    "--var" "ALLOW_LIVE_PAYMENTS:yes" \
    "--var" "MORNING_AUTH_FLOW:oauth" \
    "--var" "MORNING_API_BASE:https://api.greeninvoice.co.il/api/v1" \
    "--var" "MORNING_AUTH_BASE:https://api.morning.co" \
    "--var" "MORNING_GROUP:100" \
    "--var" "PUBLIC_BASE_URL:$SITE"
}
deploy_live() { # $1 = yes|no for the test product
  local args=()
  while IFS= read -r l; do args+=("$l"); done < <(live_vars)
  args+=("--var" "LIVE_TEST_PRODUCT:$1")
  $WR deploy "${args[@]}"
}

# ---- 0. Cloudflare login and account check
say "Cloudflare login"
ACCOUNT_ID="$(grep -o '"account_id": *"[0-9a-f]*"' wrangler.jsonc | grep -o '[0-9a-f]\{32\}' || true)"
[ -n "$ACCOUNT_ID" ] || die "account_id not found in wrangler.jsonc"
if ! $WR whoami 2>/dev/null | grep -q "$ACCOUNT_ID"; then
  echo "Not logged in to the right Cloudflare account. Opening the login in your browser..."
  $WR login
  $WR whoami 2>/dev/null | grep -q "$ACCOUNT_ID" || die "You are logged in to a different Cloudflare account than wrangler.jsonc expects ($ACCOUNT_ID)."
fi
echo "Logged in to the expected Cloudflare account."

# ---- revert / remove-test modes
if [ "$MODE" = "revert" ]; then
  say "Revert to safe test mode"
  echo "This redeploys with the defaults from wrangler.jsonc: payments in test mode (mock), no live charges, no test product."
  [ "$(ask 'Type REVERT to continue:')" = "REVERT" ] || die "Cancelled. Nothing was changed."
  $WR deploy
  curl -fsS "$SITE/api/config"; echo
  echo "Done. Live payments are OFF."
  exit 0
fi
if [ "$MODE" = "remove-test" ]; then
  say "Remove the ₪1 test product (live payments stay ON)"
  [ "$(ask 'Type LIVE to continue:')" = "LIVE" ] || die "Cancelled. Nothing was changed."
  deploy_live no
  curl -fsS "$SITE/api/config"; echo
  exit 0
fi

# ---- 1. What is live right now, and what would be replaced
say "1/5 Snapshot of the live site (nothing is changed)"
SNAP="live-snapshot-$(date +%Y%m%d-%H%M)"
mkdir -p "$SNAP"
CHANGED=""
for pair in "/:index.html" "/app.js:app.js" "/order:order.html" "/order.js:order.js" "/styles.css:styles.css" \
            "/catalog.js:catalog.js" "/purchase-policy.js:purchase-policy.js" "/cart-store.js:cart-store.js" "/terms:terms.html"; do
  url="${pair%%:*}"; file="${pair##*:}"
  if curl -fsSL "$SITE$url" -o "$SNAP/$file" 2>/dev/null; then
    if ! cmp -s "$SNAP/$file" "public/$file"; then
      n="$(diff "$SNAP/$file" "public/$file" | grep -c '^[<>]' || true)"
      CHANGED="$CHANGED\n   - $file ($n changed lines)"
    fi
  else
    CHANGED="$CHANGED\n   - $file (could not be fetched from the live site)"
  fi
done
echo "Saved a copy of the live pages in ./$SNAP (keep it; it is your backup of what is online now)."
if [ -n "$CHANGED" ]; then
  echo "These live files DIFFER from the code in this folder and will be REPLACED by this folder's version:"
  printf "$CHANGED\n"
  echo "If the live site contains changes that are not in this repository, send me or Codex the $SNAP folder before continuing."
else
  echo "The live pages are identical to this folder."
fi

# ---- 2. Secrets that already exist (names only)
say "2/5 Secrets in Cloudflare (names only, never values)"
SECRETS="$($WR secret list 2>/dev/null || true)"
have() { printf '%s' "$SECRETS" | grep -q "\"$1\""; }
for s in MORNING_API_KEY_ID MORNING_API_KEY_SECRET NOTIFY_SIGNING_SECRET; do
  if have "$s"; then echo "  present: $s"; else echo "  MISSING: $s"; fi
done

# ---- 3. Pending database migrations
say "3/5 Database migrations pending on the live database"
$WR d1 migrations list "$DB" --remote 2>&1 | tail -8 || true

# ---- 4. Confirm
say "4/5 Confirmation"
cat <<EOF
If you continue, this will:
  - store any MISSING secrets above (you will be asked for the PRODUCTION Morning key id and secret;
    they are typed into wrangler, not into this script or into any chat)
  - back up the live database to a file here, then apply any pending migrations (additive)
  - deploy this folder to $SITE with REAL payments ON and the temporary ₪1 test product enabled
After that, anyone with the link can pay for real. Do not share the link yet.
EOF
[ "$(ask 'Type LIVE to continue, anything else cancels:')" = "LIVE" ] || die "Cancelled. Nothing was changed."

# ---- 5. Do it
say "5/5 Applying"
if ! have NOTIFY_SIGNING_SECRET; then
  node -e 'process.stdout.write(require("crypto").randomBytes(24).toString("hex"))' | $WR secret put NOTIFY_SIGNING_SECRET
fi
if ! have MORNING_API_KEY_ID; then
  echo "Paste the PRODUCTION Morning API key id when wrangler asks."
  $WR secret put MORNING_API_KEY_ID
fi
if ! have MORNING_API_KEY_SECRET; then
  echo "Paste the PRODUCTION Morning API secret when wrangler asks (it is hidden)."
  $WR secret put MORNING_API_KEY_SECRET
fi

BACKUP="backup-before-live-$(date +%Y%m%d-%H%M).sql"
$WR d1 export "$DB" --remote --output "$BACKUP"
echo "Database backup saved: $BACKUP"
$WR d1 migrations apply "$DB" --remote

deploy_live yes

say "Check"
CFG="$(curl -fsS "$SITE/api/config")"
echo "$CFG"
printf '%s' "$CFG" | grep -q '"liveCharges":true' || echo "WARNING: liveCharges is not true. The site is not in live mode; do not test a payment."
printf '%s' "$CFG" | grep -q '"testProduct":true' || echo "WARNING: testProduct is not true."
code="$(curl -s -o /dev/null -w '%{http_code}' "$SITE/api/admin/me")"
echo "Admin API without login answers HTTP $code (503 or 401/403 is correct; 200 would be wrong)."

cat <<EOF

LIVE TEST IS ON. Next:
 1. Open  $SITE/?test=1   — the ₪1 product "בדיקת סליקה (₪1)" appears at the end of the list.
 2. Add it to the cart, pay with a real card. You should return to the site and see the order as paid.
 3. In Morning, check the new receipt: amount ₪1, correct customer details. Then refund it from the Morning/Grow side.
 4. Tell me what you saw (screenshots are fine, no secrets).
 5. When done, run one of:
      ./scripts/go-live-test.sh --remove-test-product   (keep live, remove the ₪1 product)
      ./scripts/go-live-test.sh --revert                (back to safe test mode)
EOF
