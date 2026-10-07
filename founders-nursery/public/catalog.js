// Single source of truth for products and prices.
// The browser imports it for display only; the Worker imports the same file and
// recomputes every order total from it, ignoring any price sent by the browser.
//
// Prices are final consumer prices in agorot (₪1 = 100), VAT included.

export const CURRENCY = "ILS";

// Upper bound per cart line. Input validation only — not stock, not shown as scarcity.
export const MAX_QTY_PER_LINE = 99;

export const PRODUCTS = [
  {
    id: "tshirt",
    name: "חולצת O‑Yaku",
    priceAgorot: 12000,
    priceSuffix: "לחולצה",
    unit: { one: "חולצה", many: "חולצות" },
    details: [],
  },
  {
    id: "ceramics-group",
    name: "סדנת קרמיקה קבוצתית",
    priceAgorot: 30000,
    priceSuffix: "למשתתף",
    unit: { one: "משתתף", many: "משתתפים" },
    details: ["בקבוצה של ארבעה"],
  },
  {
    id: "ceramics-private",
    name: "סדנת קרמיקה פרטית",
    priceAgorot: 120000,
    priceSuffix: "לסדנה",
    unit: { one: "סדנה", many: "סדנאות" },
    details: [],
  },
  {
    id: "custom-pot",
    name: "כלי בונסאי בהזמנה אישית",
    priceAgorot: 120000,
    priceSuffix: "לכלי",
    unit: { one: "כלי", many: "כלים" },
    details: ["עד 45 ס״מ רוחב ועד 10 ס״מ גובה"],
  },
  {
    id: "akadama-10",
    name: "חבילת 10 שקי אקדמה",
    priceAgorot: 140000,
    priceSuffix: "לחבילה של 10 שקים",
    unit: { one: "חבילה", many: "חבילות" },
    unitFieldLabel: "חבילות של 10 שקים",
    // Shown next to the quantity so 2 packs clearly read as 20 bags.
    perUnitCount: { size: 10, label: "שקים" },
    details: ["2 חבילות הן 20 שקים"],
  },
  {
    id: "nursery-sqm-year",
    name: "מטר רבוע לגידול במשתלה לשנה",
    priceAgorot: 150000,
    priceSuffix: "למ״ר לשנה",
    unit: { one: "מ״ר לשנה", many: "מ״ר לשנה" },
    details: ["מקום לעצים שלכם", "כולל השקיה, דישון והשגחה"],
  },
];

export const PRODUCTS_BY_ID = Object.fromEntries(PRODUCTS.map((p) => [p.id, p]));

export function formatShekels(agorot) {
  const shekels = agorot / 100;
  const hasFraction = agorot % 100 !== 0;
  return (
    "₪" +
    shekels.toLocaleString("en-US", {
      minimumFractionDigits: hasFraction ? 2 : 0,
      maximumFractionDigits: 2,
    })
  );
}

export function unitLabel(product, qty) {
  return qty === 1 ? product.unit.one : product.unit.many;
}

// "2 חבילות של 10 שקים · 20 שקים" style description of a quantity.
export function describeQuantity(product, qty) {
  const base = `${qty} ${unitLabel(product, qty)}`;
  if (product.perUnitCount) {
    return `${base} · ${qty * product.perUnitCount.size} ${product.perUnitCount.label}`;
  }
  return base;
}

// Accepts only whole numbers 1..MAX_QTY_PER_LINE given as a JS integer or a
// plain digit string. Returns the integer or null.
export function parseQuantity(value) {
  if (typeof value === "number") {
    return Number.isInteger(value) && value >= 1 && value <= MAX_QTY_PER_LINE ? value : null;
  }
  if (typeof value === "string" && /^[0-9]{1,3}$/.test(value.trim())) {
    return parseQuantity(Number(value.trim()));
  }
  return null;
}

// Validates a cart of the form [{ id, qty }] and prices it from the catalog.
// Duplicate ids are rejected rather than merged so the caller sees exactly what was priced.
export function priceCart(rawItems) {
  if (!Array.isArray(rawItems) || rawItems.length === 0) {
    return { ok: false, error: "empty_cart" };
  }
  if (rawItems.length > PRODUCTS.length) {
    return { ok: false, error: "too_many_lines" };
  }
  const seen = new Set();
  const lines = [];
  for (const raw of rawItems) {
    if (!raw || typeof raw !== "object") return { ok: false, error: "invalid_line" };
    const product = PRODUCTS_BY_ID[raw.id];
    if (!product) return { ok: false, error: "unknown_product" };
    if (seen.has(product.id)) return { ok: false, error: "duplicate_product" };
    seen.add(product.id);
    const qty = parseQuantity(raw.qty);
    if (qty === null) return { ok: false, error: "invalid_quantity" };
    lines.push({
      productId: product.id,
      name: product.name,
      unitLabel: product.unit.one,
      quantityLabel: describeQuantity(product, qty),
      unitPriceAgorot: product.priceAgorot,
      quantity: qty,
      lineTotalAgorot: product.priceAgorot * qty,
    });
  }
  const totalAgorot = lines.reduce((sum, l) => sum + l.lineTotalAgorot, 0);
  return { ok: true, lines, totalAgorot, currency: CURRENCY };
}
