import { test } from "node:test";
import assert from "node:assert/strict";
import { PRODUCTS, priceCart, parseQuantity, formatShekels, describeQuantity, PRODUCTS_BY_ID } from "../public/catalog.js";

test("catalog prices match the brief (agorot, VAT included)", () => {
  const expected = {
    tshirt: 12000, "ceramics-group": 30000, "ceramics-private": 120000,
    "custom-pot": 120000, "akadama-10": 140000, "nursery-sqm-year": 150000,
  };
  assert.deepEqual(Object.fromEntries(PRODUCTS.map((p) => [p.id, p.priceAgorot])), expected);
});

test("parseQuantity accepts only whole numbers 1..99", () => {
  for (const ok of [1, 2, 99, "3", " 7 "]) assert.notEqual(parseQuantity(ok), null, String(ok));
  for (const bad of [0, -1, 1.5, 100, "1.5", "-2", "1e2", "", "abc", null, undefined, NaN, Infinity, "0x10", [], {}, true, "٣"]) {
    assert.equal(parseQuantity(bad), null, JSON.stringify(bad));
  }
});

test("priceCart totals exactly across several products and quantities", () => {
  const r = priceCart([
    { id: "tshirt", qty: 3 },          // 360
    { id: "ceramics-group", qty: 4 },  // 1,200
    { id: "akadama-10", qty: 2 },      // 2,800
    { id: "nursery-sqm-year", qty: 5 },// 7,500
  ]);
  assert.equal(r.ok, true);
  assert.equal(r.totalAgorot, 1186000);
  assert.equal(formatShekels(r.totalAgorot), "₪11,860");
  assert.deepEqual(r.lines.map((l) => l.lineTotalAgorot), [36000, 120000, 280000, 750000]);
});

test("priceCart ignores any price sent with the items", () => {
  const r = priceCart([{ id: "custom-pot", qty: 1, priceAgorot: 1, price: 1, total: 1 }]);
  assert.equal(r.totalAgorot, 120000);
});

test("priceCart rejects invalid carts", () => {
  assert.equal(priceCart([]).error, "empty_cart");
  assert.equal(priceCart(null).error, "empty_cart");
  assert.equal(priceCart([{ id: "lesson", qty: 1 }]).error, "unknown_product");
  assert.equal(priceCart([{ id: "tshirt", qty: 0 }]).error, "invalid_quantity");
  assert.equal(priceCart([{ id: "tshirt", qty: 2.5 }]).error, "invalid_quantity");
  assert.equal(priceCart([{ id: "tshirt", qty: -3 }]).error, "invalid_quantity");
  assert.equal(priceCart([{ id: "tshirt", qty: 1 }, { id: "tshirt", qty: 1 }]).error, "duplicate_product");
});

test("akadama quantity reads as bags", () => {
  assert.equal(describeQuantity(PRODUCTS_BY_ID["akadama-10"], 2), "2 חבילות · 20 שקים");
  assert.equal(describeQuantity(PRODUCTS_BY_ID["nursery-sqm-year"], 3), "3 מ״ר לשנה");
});
