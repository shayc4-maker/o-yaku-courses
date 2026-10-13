// Voucher redemption rules shared by the public voucher view and the admin area.
import { PRODUCTS_BY_ID } from "../public/catalog.js";

// Redemption starts in January 2027 (Israel time). Not configurable on purpose.
export const REDEMPTION_STARTS_ON = "2027-01-01";

// Snapshot of how a purchased line is redeemed. Akadama is sold in packs of 10 and handed out in bags.
export function redeemUnitsFor(productId, quantity) {
  const p = PRODUCTS_BY_ID[productId];
  if (p?.perUnitCount) return { units: quantity * p.perUnitCount.size, label: p.perUnitCount.label };
  return { units: quantity, label: p ? p.unit.many : "יחידות" };
}

export function normalizeEmail(email) {
  return String(email).trim().toLowerCase();
}

// Expiry as SQL, matching voucherExpiry(): +24 months, with Feb 29 clamped to Feb 28.
// Output format is SQLite's "YYYY-MM-DD HH:MM:SS" (UTC).
export const SQL_EXPIRES_AT = `CASE WHEN o.paid_at IS NULL THEN NULL
  WHEN strftime('%m-%d', o.paid_at) = '02-29' THEN datetime(o.paid_at, '-1 day', '+24 months')
  ELSE datetime(o.paid_at, '+24 months') END`;

// Today's date in Israel, "YYYY-MM-DD".
export function israelDate(ms) {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Jerusalem", year: "numeric", month: "2-digit", day: "2-digit" })
    .format(new Date(ms));
}

// UTC instant of 00:00 Israel time on a given "YYYY-MM-DD".
export function israelDayStartUtc(day) {
  const guess = Date.parse(`${day}T00:00:00Z`);
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Jerusalem", hourCycle: "h23", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit",
  }).formatToParts(new Date(guess));
  const get = (t) => Number(parts.find((p) => p.type === t).value);
  const asIfUtc = Date.UTC(get("year"), get("month") - 1, get("day"), get("hour"), get("minute"));
  return new Date(guess - (asIfUtc - guess)).toISOString();
}

export function isValidDay(s) {
  if (typeof s !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return false;
  const d = new Date(`${s}T00:00:00Z`);
  return !Number.isNaN(d.getTime()) && d.toISOString().slice(0, 10) === s;
}

// State of one line / one voucher. Payment status is separate and never derived from this.
//   na · not_redeemed · partial · full · expired · cancelled
export function lineState({ paid, cancelled, expired, units, redeemed }) {
  if (!paid) return "na";
  if (cancelled) return "cancelled";
  if (redeemed >= units) return "full";
  if (expired) return "expired";
  return redeemed > 0 ? "partial" : "not_redeemed";
}

export function voucherState(lines, { paid, cancelled, expired }) {
  if (!paid) return "na";
  const units = lines.reduce((n, l) => n + l.units, 0);
  const redeemed = lines.reduce((n, l) => n + l.redeemed, 0);
  return lineState({ paid, cancelled, expired, units, redeemed });
}

export const STATE_LABELS = {
  na: "אין שובר",
  not_redeemed: "טרם מומש",
  partial: "מומש חלקית",
  full: "מומש במלואו",
  expired: "פג תוקף",
  cancelled: "בוטל",
};
