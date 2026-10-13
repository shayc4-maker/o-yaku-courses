-- Admin area: buyers, voucher redemption ledger, coordination notes, activity log.
-- Additive only: no existing column, row or table is changed except the new nullable columns
-- below and their backfill. Safe to apply to a database that already holds orders.

-- 1. Buyers. One row per normalized email (trim + lower-case only). Orders keep the original
--    name/phone/email they were placed with; buyers.name/phone are the first values seen.
--    No automatic merging by name or phone.
CREATE TABLE IF NOT EXISTS buyers (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  email_normalized  TEXT NOT NULL UNIQUE,
  name              TEXT NOT NULL,
  phone             TEXT NOT NULL,
  created_at        TEXT NOT NULL
);

ALTER TABLE orders ADD COLUMN buyer_id INTEGER REFERENCES buyers(id);

-- Backfill from existing orders: earliest order per email supplies the buyer's display details.
INSERT OR IGNORE INTO buyers (email_normalized, name, phone, created_at)
SELECT lower(trim(customer_email)), customer_name, customer_phone, MIN(created_at)
FROM orders
GROUP BY lower(trim(customer_email));

UPDATE orders
SET buyer_id = (SELECT b.id FROM buyers b WHERE b.email_normalized = lower(trim(orders.customer_email)))
WHERE buyer_id IS NULL;

CREATE INDEX IF NOT EXISTS idx_orders_buyer ON orders(buyer_id);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_mode_status ON orders(payment_mode, status);

-- 2. Redemption units, snapshotted per order line so later catalog changes never alter old vouchers.
--    Akadama is redeemed in bags (10 per pack); everything else in its own sale unit.
ALTER TABLE order_items ADD COLUMN redeem_units INTEGER;
ALTER TABLE order_items ADD COLUMN redeem_unit_label TEXT;

UPDATE order_items SET
  redeem_units = CASE product_id WHEN 'akadama-10' THEN quantity * 10 ELSE quantity END,
  redeem_unit_label = CASE product_id
    WHEN 'akadama-10' THEN 'שקים'
    WHEN 'tshirt' THEN 'חולצות'
    WHEN 'ceramics-group' THEN 'משתתפים'
    WHEN 'ceramics-private' THEN 'סדנאות'
    WHEN 'bonsai-private-lesson' THEN 'שיעורים'
    WHEN 'bonsai-wiring-workshop' THEN 'משתתפים'
    WHEN 'pine-grafting-workshop' THEN 'משתתפים'
    WHEN 'custom-pot' THEN 'כלים'
    WHEN 'nursery-sqm-year' THEN 'מ״ר לשנה'
    ELSE unit_label END
WHERE redeem_units IS NULL;

-- 3. Voucher cancellation (blocks redemption only — it is not a refund and never changes payment status).
ALTER TABLE orders ADD COLUMN voucher_cancelled_at TEXT;
ALTER TABLE orders ADD COLUMN voucher_cancelled_by TEXT;
ALTER TABLE orders ADD COLUMN voucher_cancel_reason TEXT;

-- 4. Redemption ledger. Append-only: a correction is a new row (negative quantity) that points at
--    the redemption it corrects. Rows are never updated or deleted by the application.
CREATE TABLE IF NOT EXISTS redemptions (
  id                   INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id             TEXT NOT NULL REFERENCES orders(id),
  product_id           TEXT NOT NULL,
  kind                 TEXT NOT NULL CHECK (kind IN ('redeem', 'correction')),
  quantity             INTEGER NOT NULL CHECK (quantity != 0),
  corrects_id          INTEGER REFERENCES redemptions(id),
  redeemed_on          TEXT NOT NULL,
  note                 TEXT,
  reason               TEXT,
  admin_email          TEXT NOT NULL,
  idempotency_key      TEXT NOT NULL UNIQUE,
  request_fingerprint  TEXT NOT NULL,
  created_at           TEXT NOT NULL,
  CHECK ((kind = 'redeem' AND quantity > 0 AND corrects_id IS NULL)
      OR (kind = 'correction' AND quantity < 0 AND corrects_id IS NOT NULL AND reason IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS idx_redemptions_line ON redemptions(order_id, product_id);
CREATE INDEX IF NOT EXISTS idx_redemptions_corrects ON redemptions(corrects_id);

-- 5. Coordination notes (internal). Latest row per (order, product, kind) is the current value.
CREATE TABLE IF NOT EXISTS order_notes (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id     TEXT NOT NULL REFERENCES orders(id),
  product_id   TEXT,
  kind         TEXT NOT NULL,
  value        TEXT NOT NULL,
  admin_email  TEXT NOT NULL,
  created_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_order_notes_order ON order_notes(order_id);

-- 6. Admin activity that is not already a ledger/note row (e.g. voucher cancellation).
CREATE TABLE IF NOT EXISTS admin_activity (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id     TEXT,
  action       TEXT NOT NULL,
  details      TEXT,
  reason       TEXT,
  admin_email  TEXT NOT NULL,
  created_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_admin_activity_order ON admin_activity(order_id);
