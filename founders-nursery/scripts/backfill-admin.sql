-- Re-runnable backfill for the admin tables. Same statements as the backfill in
-- migrations/0003_admin.sql, safe to run any number of times. Run it right after deploying the
-- new Worker code, to cover orders created between applying 0003 and the deploy finishing:
--   npx wrangler d1 execute oyaku-founders-orders --remote --file scripts/backfill-admin.sql
INSERT OR IGNORE INTO buyers (email_normalized, name, phone, created_at)
SELECT lower(trim(customer_email)), customer_name, customer_phone, MIN(created_at)
FROM orders
GROUP BY lower(trim(customer_email));

UPDATE orders
SET buyer_id = (SELECT b.id FROM buyers b WHERE b.email_normalized = lower(trim(orders.customer_email)))
WHERE buyer_id IS NULL;

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
