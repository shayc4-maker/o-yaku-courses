// Cart state kept in localStorage so it survives reloads and the round trip to the payment page.
// The stored cart is only a list of { id, qty }; prices are always read from the catalog.
import { PRODUCTS_BY_ID, parseQuantity, priceCart } from "./catalog.js";

const CART_KEY = "oyaku-founders-cart-v1";
const CUSTOMER_KEY = "oyaku-founders-customer-v1";
const ATTEMPT_KEY = "oyaku-founders-attempt-v1";

function safeGet(storage, key) {
  try {
    return JSON.parse(storage.getItem(key) || "null");
  } catch {
    return null;
  }
}
function safeSet(storage, key, value) {
  try {
    if (value === null) storage.removeItem(key);
    else storage.setItem(key, JSON.stringify(value));
  } catch {
    /* storage unavailable (private mode / blocked): the cart still works for this page view */
  }
}

// Drops unknown products, invalid quantities and duplicates from whatever was stored.
export function sanitizeItems(items) {
  if (!Array.isArray(items)) return [];
  const out = [];
  const seen = new Set();
  for (const it of items) {
    if (!it || !PRODUCTS_BY_ID[it.id] || seen.has(it.id)) continue;
    const qty = parseQuantity(it.qty);
    if (qty === null) continue;
    seen.add(it.id);
    out.push({ id: it.id, qty });
  }
  return out;
}

export function createCartStore() {
  let items = sanitizeItems(safeGet(localStorage, CART_KEY)?.items);
  const listeners = new Set();
  const emit = () => {
    safeSet(localStorage, CART_KEY, { v: 1, items });
    listeners.forEach((fn) => fn());
  };

  // Another tab changed the cart.
  window.addEventListener("storage", (e) => {
    if (e.key === CART_KEY) {
      items = sanitizeItems(safeGet(localStorage, CART_KEY)?.items);
      listeners.forEach((fn) => fn());
    }
  });

  return {
    subscribe(fn) {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
    items: () => items.slice(),
    priced: () => (items.length ? priceCart(items) : { ok: true, lines: [], totalAgorot: 0 }),
    count: () => items.reduce((n, i) => n + i.qty, 0),
    // Adds to an existing line. Returns the resulting quantity, or null if it would be invalid.
    add(id, qty) {
      const line = items.find((i) => i.id === id);
      const next = parseQuantity((line ? line.qty : 0) + qty);
      if (!PRODUCTS_BY_ID[id] || next === null) return null;
      items = line ? items.map((i) => (i.id === id ? { id, qty: next } : i)) : [...items, { id, qty: next }];
      emit();
      return next;
    },
    set(id, qty) {
      const q = parseQuantity(qty);
      if (q === null) return false;
      items = items.map((i) => (i.id === id ? { id, qty: q } : i));
      emit();
      return true;
    },
    remove(id) {
      items = items.filter((i) => i.id !== id);
      emit();
    },
    clear() {
      items = [];
      emit();
    },
  };
}

export const customerStore = {
  load: () => safeGet(sessionStorage, CUSTOMER_KEY) || {},
  save: (c) => safeSet(sessionStorage, CUSTOMER_KEY, c),
};

// One idempotency key per (cart + customer) attempt. Re-submitting the same cart reuses the key,
// so a double click, a retry after a network error, or "back" from the payment page returns the
// same server order and the same payment page instead of creating a second one.
export const attemptStore = {
  keyFor(signature) {
    const a = safeGet(sessionStorage, ATTEMPT_KEY);
    if (a && a.signature === signature && typeof a.key === "string") return a.key;
    const bytes = new Uint8Array(18);
    crypto.getRandomValues(bytes);
    const key = [...bytes].map((b) => b.toString(16).padStart(2, "0")).join("");
    safeSet(sessionStorage, ATTEMPT_KEY, { signature, key });
    return key;
  },
  reset: () => safeSet(sessionStorage, ATTEMPT_KEY, null),
};
