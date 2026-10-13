# Morning integration — 2026-10-07

Prepared against the official specification: https://developers.morning.co/docs/openapi.bundled.json
API key instructions: https://www.greeninvoice.co.il/help-center/generating-api-key/

## Verified from the specification

- OAuth client credentials: POST /idp/v1/oauth/token. Production auth base https://api.morning.co; sandbox https://api.sandbox.morning.dev. Response accessToken and expiresAt (Unix seconds).
- API bases: https://api.greeninvoice.co.il/api/v1 and https://sandbox.d.greeninvoice.co.il/api/v1.
- POST /payments/form accepts multiple income lines, quantities, URLs and custom order reference. Grow requires group; 100 is credit card. Omitted pluginId uses the business default plugin.
- Type 320 is tax invoice/receipt. Item vatType 1 includes VAT in unit price; document vatType 0 follows business settings.
- Document GET returns VAT-inclusive amount, currency, type, status and payment rows. Status 0/1 is open/closed; 2 is manually closed; 3/4 cancelling/cancelled.

## Account and local configuration

Shay reports registering and installing the payment plugin. Its approval/activation status has not been confirmed. No account credentials have been provided.

The private, ignored .dev.vars file starts in mock mode, with blank MORNING_API_KEY_ID and MORNING_API_KEY_SECRET, sandbox endpoints and a locally generated notify signing secret. Never put credentials in chat, public assets or source control.

Create a separate sandbox account using the official instructions: fictional business, fictional Best subscription, API key under personal area → developer tools → API keys. Place sandbox ID and secret in .dev.vars. Production keys do not substitute for sandbox keys.

## Implemented checks

OAuth is the default. Payment forms use VAT-inclusive prices and Grow group 100. The server retrieves each candidate document with its own credentials and checks ID, exact order reference, type 320, acceptable status, ILS currency, online payment rows and their total. The amount must also match the order. Unverified payments never issue vouchers.

Identical notification retries remain processable after temporary lookup/authentication/network failures, returning 503. Successful and terminal events are deduplicated. Nine simulated-provider tests pass, including unpaid invoices, cancelled receipts, mismatched totals and delayed-document retry. They do not prove real sandbox behaviour or activation.

## Remaining before launch

1. Obtain sandbox credentials and confirm payment plugin/group availability in that account.
2. Arrange a public HTTPS test callback URL. Localhost cannot receive Morning notifications. Public exposure/deployment has not been performed.
3. Switch to morning_sandbox and set PUBLIC_BASE_URL when ready. Keep ALLOW_LIVE_PAYMENTS=no.
4. Verify real hosted checkout, VAT-inclusive amounts, receipt contents, actual notification structure, approved/declined payments, retries and vouchers.
5. Record account-specific response differences; do not weaken verification to bypass them.
6. After sandbox validation and launch authorization: production secrets, permanent domain, remote migrations and live mode.

No actual Morning API call with account credentials, real charge, document creation or live deployment has been performed.
