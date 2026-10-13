import { test } from "node:test";
import assert from "node:assert/strict";
import { voucherExpiry } from "../public/purchase-policy.js";

test("voucher expiry preserves two calendar years and clamps leap day", () => {
  assert.equal(voucherExpiry("2026-10-07T12:30:00.000Z"), "2028-10-07T12:30:00.000Z");
  assert.equal(voucherExpiry("2028-02-29T12:30:00.000Z"), "2030-02-28T12:30:00.000Z");
});
