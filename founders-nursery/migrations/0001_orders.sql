-- Orders for the founders round. One row per checkout attempt.
-- status: awaiting_payment | paid | needs_review | cancelled | failed_to_start
--   paid          — confirmed by the provider's server-side mechanism (or the mock provider in test mode)
--   needs_review  — the provider reported something we could not verify automatically; reconcile by hand
CREATE TABLE IF NOT EXISTS orders (
  id                       TEXT PRIMARY KEY,
  access_token             TEXT NOT NULL,
  idempotency_key          TEXT NOT NULL UNIQUE,
  request_fingerprint      TEXT NOT NULL,
  status                   TEXT NOT NULL,
  payment_mode             TEXT NOT NULL,
  currency                 TEXT NOT NULL,
  total_agorot             INTEGER NOT NULL CHECK (total_agorot > 0),
  customer_name            TEXT NOT NULL,
  customer_email           TEXT NOT NULL,
  customer_phone           TEXT NOT NULL,
  provider_payment_url     TEXT,
  provider_document_id     TEXT,
  provider_transaction_id  TEXT,
  status_reason            TEXT,
  created_at               TEXT NOT NULL,
  updated_at               TEXT NOT NULL,
  paid_at                  TEXT
);

CREATE TABLE IF NOT EXISTS order_items (
  order_id            TEXT NOT NULL REFERENCES orders(id),
  product_id          TEXT NOT NULL,
  name                TEXT NOT NULL,
  unit_label          TEXT NOT NULL,
  quantity_label      TEXT NOT NULL,
  unit_price_agorot   INTEGER NOT NULL,
  quantity            INTEGER NOT NULL CHECK (quantity > 0),
  line_total_agorot   INTEGER NOT NULL,
  PRIMARY KEY (order_id, product_id)
);

-- Every inbound provider notification, raw. event_key is unique so a redelivered
-- notification is recorded once and never applied twice.
CREATE TABLE IF NOT EXISTS payment_events (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  provider     TEXT NOT NULL,
  event_key    TEXT NOT NULL UNIQUE,
  order_id     TEXT,
  payload      TEXT NOT NULL,
  outcome      TEXT,
  received_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_payment_events_order ON payment_events(order_id);
