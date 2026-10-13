// Fictional order rows written straight into a local test D1, shaped like real rows from before
// the admin migration (no buyer_id, no redeem_units). Test data only.
import { randomBytes } from "node:crypto";
import { TERMS_VERSION } from "../../public/purchase-policy.js";
import { key } from "./admin-env.mjs";

const tok = () => randomBytes(24).toString("hex");
const esc = (s) => String(s).replace(/'/g, "''");

export function legacyOrder({ id, mode = "morning_live", status = "paid", paidAt = "2026-10-20T09:00:00.000Z", createdAt, name, email, phone, items }) {
  const total = items.reduce((n, i) => n + i.price * i.qty, 0);
  const created = createdAt || paidAt || "2026-10-20T08:00:00.000Z";
  return [
    `INSERT INTO orders (id, access_token, idempotency_key, request_fingerprint, status, payment_mode, currency, total_agorot,
      customer_name, customer_email, customer_phone, created_at, updated_at, paid_at, terms_version, terms_accepted_at)
     VALUES ('${id}', '${tok()}', '${key()}', 'fp', '${status}', '${mode}', 'ILS', ${total}, '${esc(name)}', '${esc(email)}', '${esc(phone)}',
      '${created}', '${created}', ${status === "paid" ? `'${paidAt}'` : "NULL"}, '${TERMS_VERSION}', '${created}');`,
    ...items.map((i) => `INSERT INTO order_items (order_id, product_id, name, unit_label, quantity_label, unit_price_agorot, quantity, line_total_agorot, redemption_text)
      VALUES ('${id}', '${i.id}', '${esc(i.name)}', '${esc(i.unit)}', '${esc(i.label)}', ${i.price}, ${i.qty}, ${i.price * i.qty}, 'מימוש החל מינואר 2027');`),
  ].join("\n");
}
export const AKADAMA = (qty) => ({ id: "akadama-10", name: "חבילת 10 שקי אקדמה", unit: "חבילה", label: `${qty} חבילות · ${qty * 10} שקים`, price: 140000, qty });
export const SHIRT = (qty) => ({ id: "tshirt", name: "חולצת O‑Yaku", unit: "חולצה", label: `${qty} חולצות`, price: 12000, qty });
export const SQM = (qty) => ({ id: "nursery-sqm-year", name: "מטר רבוע לגידול במשתלה לשנה", unit: "מ״ר לשנה", label: `${qty} מ״ר לשנה`, price: 150000, qty });
export const LESSON = (qty) => ({ id: "bonsai-private-lesson", name: "שיעור בונסאי 1:1", unit: "שיעור", label: `${qty} שיעורים`, price: 70000, qty });
export const GROUP = (qty) => ({ id: "ceramics-group", name: "סדנת קרמיקה קבוצתית", unit: "משתתף", label: `${qty} משתתפים`, price: 30000, qty });

