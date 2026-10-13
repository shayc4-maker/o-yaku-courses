# Public review deployment — 2026-10-07

URL: https://nursery.o-yaku.com
Cloudflare Worker: oyaku-founders-nursery
Version: 0f617d71-ae1d-4e1c-93a9-9c71ce0f9246
D1 database: oyaku-founders-orders (8dcd1f6e-a580-4326-8892-02d97f7dedf5)
Remote migrations: 0001 and 0002 applied.

User authorized publication. Published in mock payment mode, ALLOW_LIVE_PAYMENTS=no, with no Morning credentials uploaded. No round opening date set; the 14-day window has not started. Main domain and existing Workers remain attached to their previous services.

Public checks passed: homepage, terms, noindex headers, config in mock mode, private .dev.vars inaccessible, multi-item checkout, simulated paid status and visibly labelled example voucher. The single synthetic deployment-check order was removed after verification.

Morning production credentials saved locally authenticate successfully; they are not sandbox credentials. Real hosted-payment/account-plugin verification is still pending. This public review deployment does not enable real sales or represent Grow approval.
