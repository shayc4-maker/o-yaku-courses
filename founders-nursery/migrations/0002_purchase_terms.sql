ALTER TABLE orders ADD COLUMN terms_version TEXT;
ALTER TABLE orders ADD COLUMN terms_accepted_at TEXT;
ALTER TABLE order_items ADD COLUMN redemption_text TEXT;
