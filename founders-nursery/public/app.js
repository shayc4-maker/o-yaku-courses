import { PRODUCTS, PRODUCTS_BY_ID, MAX_QTY_PER_LINE, formatShekels, describeQuantity, parseQuantity } from "./catalog.js";
import { createCartStore, customerStore, attemptStore } from "./cart-store.js";

const $ = (sel, root = document) => root.querySelector(sel);
const el = (tag, attrs = {}, ...children) => {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === false || v == null) continue;
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat()) if (c != null) node.append(c);
  return node;
};
const MINUS = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M5 12h14"/></svg>';
const PLUS = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>';

const cart = createCartStore();
let config = { paymentMode: "mock", liveCharges: false, roundOpensAt: null, roundDays: 14 };

// ---------------------------------------------------------------- quantity stepper

// A − [n] + control bound to a number. onChange receives a valid integer; invalid typing is
// flagged and never propagated.
function stepper({ id, label, value, onChange }) {
  const input = el("input", {
    id, type: "text", inputmode: "numeric", pattern: "[0-9]*", autocomplete: "off",
    value: String(value), "aria-label": label, maxlength: "2",
  });
  const dec = el("button", { type: "button", "aria-label": `הפחתה — ${label}` });
  const inc = el("button", { type: "button", "aria-label": `הוספה — ${label}` });
  dec.innerHTML = MINUS;
  inc.innerHTML = PLUS;
  let current = value;
  const sync = () => {
    input.value = String(current);
    input.removeAttribute("aria-invalid");
    dec.disabled = current <= 1;
    inc.disabled = current >= MAX_QTY_PER_LINE;
  };
  const commit = (q) => {
    current = q;
    sync();
    onChange(q);
  };
  dec.addEventListener("click", () => current > 1 && commit(current - 1));
  inc.addEventListener("click", () => current < MAX_QTY_PER_LINE && commit(current + 1));
  input.addEventListener("input", () => {
    const q = parseQuantity(input.value);
    if (q === null) input.setAttribute("aria-invalid", "true");
    else {
      input.removeAttribute("aria-invalid");
      current = q;
      dec.disabled = q <= 1;
      inc.disabled = q >= MAX_QTY_PER_LINE;
      onChange(q);
    }
  });
  // Leaving the field with an invalid value restores the last valid quantity.
  input.addEventListener("blur", sync);
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowUp") { e.preventDefault(); inc.click(); }
    if (e.key === "ArrowDown") { e.preventDefault(); dec.click(); }
  });
  sync();
  return { node: el("span", { class: "stepper" }, inc, input, dec), get value() { return current; }, set(q) { current = q; sync(); } };
}

// ---------------------------------------------------------------- products

function renderProducts() {
  const grid = $("#product-grid");
  grid.replaceChildren(
    ...PRODUCTS.map((p) => {
      const qtyId = `qty-${p.id}`;
      const hint = el("span", { class: "qty-hint", id: `${qtyId}-hint`, "aria-live": "polite" });
      const updateHint = (q) => {
        hint.textContent = q > 1 ? `${describeQuantity(p, q)} · ${formatShekels(p.priceAgorot * q)}` : "";
      };
      const s = stepper({ id: qtyId, label: `כמות — ${p.name} (${p.unit.many})`, value: 1, onChange: updateHint });
      updateHint(1);
      const addBtn = el("button", {
        class: "btn btn-primary", type: "button",
        onclick: () => {
          const q = s.value;
          const total = cart.add(p.id, q);
          if (total === null) {
            showToast(`אפשר להזמין עד ${MAX_QTY_PER_LINE} ${p.unit.many} בהזמנה אחת.`, false);
            return;
          }
          showToast(`נוסף לסל: ${describeQuantity(p, q)} · ${p.name}`);
          s.set(1);
          updateHint(1);
        },
      }, "הוספה לסל");

      return el("li", { class: "product-card" },
        el("h3", { text: p.name }),
        p.details.length ? el("ul", { class: "product-details" }, p.details.map((d) => el("li", { text: d }))) : null,
        el("p", { class: "product-price" },
          el("span", { class: "price num", text: formatShekels(p.priceAgorot) }),
          el("span", { class: "price-suffix", text: `${p.priceSuffix} · כולל מע״מ` }),
        ),
        el("div", { class: "product-buy" },
          el("div", { class: "qty-field" },
            el("label", { for: qtyId, text: `כמות (${p.unitFieldLabel || p.unit.many})` }),
            s.node,
          ),
          addBtn,
        ),
        hint,
      );
    }),
  );
}

// ---------------------------------------------------------------- toast

let toastTimer;
function showToast(text, withCartAction = true) {
  const t = $("#toast");
  $("#toast-text").textContent = text;
  $("#toast-open-cart").hidden = !withCartAction;
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (t.hidden = true), 5000);
}

// ---------------------------------------------------------------- cart dialog

const dialog = $("#cart-dialog");

function openCart() {
  $("#toast").hidden = true;
  renderCart();
  if (!dialog.open) dialog.showModal();
}
function closeCart() {
  dialog.close();
}

function renderCartBadge() {
  const n = cart.count();
  const badge = $("#cart-count");
  badge.textContent = String(n);
  badge.classList.toggle("has-items", n > 0);
  $("#cart-count-label").textContent = n === 1 ? "פריט בסל" : "פריטים בסל";
}

function renderCart() {
  const priced = cart.priced();
  const empty = priced.lines.length === 0;
  $("#cart-empty").hidden = !empty;
  $("#cart-filled").hidden = empty;
  if (empty) return;

  const list = $("#cart-lines");
  // Keep focus on the stepper being edited by updating lines in place when possible.
  const existing = new Map([...list.children].map((li) => [li.dataset.id, li]));
  const nextNodes = priced.lines.map((line) => {
    const p = PRODUCTS_BY_ID[line.productId];
    let li = existing.get(line.productId);
    if (!li) {
      const s = stepper({
        id: `cart-qty-${p.id}`,
        label: `כמות — ${p.name} (${p.unit.many})`,
        value: line.quantity,
        onChange: (q) => cart.set(p.id, q),
      });
      li = el("li", { class: "cart-line", "data-id": p.id },
        el("div", {},
          el("div", { class: "cart-line-name", text: p.name }),
          el("div", { class: "cart-line-meta" },
            el("span", { class: "num", text: formatShekels(p.priceAgorot) }), ` ${p.priceSuffix}`),
          el("div", { class: "cart-line-meta", "data-role": "qty-label" }),
        ),
        el("div", { class: "cart-line-total num", "data-role": "line-total" }),
        el("div", { class: "cart-line-controls" },
          s.node,
          el("button", {
            class: "link-button", type: "button", "aria-label": `הסרת ${p.name} מהסל`,
            onclick: () => {
              cart.remove(p.id);
              showToast(`הוסר מהסל: ${p.name}`, false);
              $("#close-cart").focus();
            },
          }, "הסרה"),
        ),
      );
      li._stepper = s;
    } else if (li._stepper.value !== line.quantity) {
      li._stepper.set(line.quantity);
    }
    li.querySelector('[data-role="qty-label"]').textContent = describeQuantity(p, line.quantity);
    li.querySelector('[data-role="line-total"]').textContent = formatShekels(line.lineTotalAgorot);
    return li;
  });
  for (const [id, li] of existing) if (!priced.lines.some((l) => l.productId === id)) li.remove();
  nextNodes.forEach((n, i) => {
    if (list.children[i] !== n) list.insertBefore(n, list.children[i] || null);
  });
  $("#cart-total").textContent = formatShekels(priced.totalAgorot);
}

// ---------------------------------------------------------------- checkout

const form = $("#checkout-form");
const submitBtn = $("#checkout-button");
let inFlight = false;

const fields = {
  name: { input: $("#c-name"), error: $("#c-name-error"), valid: (v) => v.trim().length >= 2 && v.trim().length <= 80 },
  phone: {
    input: $("#c-phone"), error: $("#c-phone-error"),
    valid: (v) => /^[0-9+\-\s()]{9,20}$/.test(v.trim()) && v.replace(/\D/g, "").length >= 9 && v.replace(/\D/g, "").length <= 15,
  },
  email: { input: $("#c-email"), error: $("#c-email-error"), valid: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) && v.length <= 120 },
};

function readCustomer() {
  return Object.fromEntries(Object.entries(fields).map(([k, f]) => [k, f.input.value.trim()]));
}

function validateForm() {
  let firstInvalid = null;
  for (const f of Object.values(fields)) {
    const ok = f.valid(f.input.value);
    f.error.hidden = ok;
    if (ok) {
      f.input.removeAttribute("aria-invalid");
      f.input.removeAttribute("aria-describedby");
    } else {
      f.input.setAttribute("aria-invalid", "true");
      f.input.setAttribute("aria-describedby", f.error.id);
      firstInvalid ??= f.input;
    }
  }
  firstInvalid?.focus();
  return !firstInvalid;
}

function setBusy(busy, label) {
  inFlight = busy;
  submitBtn.disabled = busy;
  submitBtn.setAttribute("aria-busy", String(busy));
  submitBtn.textContent = label ?? checkoutLabel();
}
const checkoutLabel = () => (config.liveCharges ? "מעבר לתשלום" : "מעבר לתשלום (מצב בדיקה)");

function showFormError(text) {
  const e = $("#checkout-error");
  e.textContent = text;
  e.hidden = !text;
}

const ERRORS = {
  payment_unavailable: "לא הצלחנו לפתוח את דף התשלום. לא בוצע חיוב. אפשר לנסות שוב בעוד רגע.",
  invalid_customer: "יש לבדוק את הפרטים שהוזנו.",
  empty_cart: "הסל ריק.",
  invalid_quantity: "אחת הכמויות בסל אינה תקינה.",
  unknown_product: "אחד הפריטים בסל אינו זמין. הסרנו אותו — יש לבדוק את הסל ולנסות שוב.",
  round_closed: "הסבב נסגר.",
  round_not_open: "הסבב עוד לא נפתח.",
  live_payments_not_allowed: "התשלום עדיין לא פעיל.",
  network: "אין חיבור לשרת. לא בוצע חיוב. אפשר לנסות שוב.",
};

async function postCheckout(payload) {
  const res = await fetch("/api/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => ({}));
  return { status: res.status, data };
}

async function checkout(e) {
  e.preventDefault();
  if (inFlight) return; // double-click / double-submit guard
  showFormError("");
  if (!validateForm()) return;
  const items = cart.items();
  if (!items.length) return;

  const customer = readCustomer();
  customerStore.save(customer);
  const signature = JSON.stringify({ items, customer });
  setBusy(true, "פותח את דף התשלום…");
  let navigating = false;

  try {
    for (let attempt = 0; attempt < 6; attempt++) {
      const key = attemptStore.keyFor(signature);
      let r;
      try {
        r = await postCheckout({ idempotencyKey: key, items, customer });
      } catch {
        showFormError(ERRORS.network);
        return;
      }
      const { status, data } = r;

      if (status === 200 && data.state === "redirect" && data.paymentUrl) {
        navigating = true; // keep the button disabled while the browser navigates away
        window.location.assign(data.paymentUrl);
        return;
      }
      if (status === 202) {
        await new Promise((ok) => setTimeout(ok, 1000)); // same order is being prepared
        continue;
      }
      if (status === 200 && data.state === "paid") {
        navigating = true;
        window.location.assign(`/order?order=${encodeURIComponent(data.orderId)}&t=${encodeURIComponent(data.token)}`);
        return;
      }
      if (status === 200 || status === 409) {
        // The earlier attempt for this cart was cancelled or never started: start a fresh one.
        attemptStore.reset();
        continue;
      }
      if (data.error === "unknown_product") cart.clear();
      if (data.error === "payment_unavailable") attemptStore.reset();
      showFormError(ERRORS[data.error] || "משהו השתבש. לא בוצע חיוב. אפשר לנסות שוב.");
      return;
    }
    showFormError("משהו השתבש. לא בוצע חיוב. אפשר לנסות שוב.");
  } finally {
    if (!navigating) setBusy(false);
  }
}

// ---------------------------------------------------------------- round dates

function renderRound() {
  const note = $("#round-dates");
  if (!config.roundOpensAt) return; // no real date yet: no dates, no countdown
  const start = new Date(config.roundOpensAt);
  if (Number.isNaN(start.getTime())) return;
  const end = new Date(start.getTime() + config.roundDays * 86400000);
  const fmt = (d) => d.toLocaleDateString("he-IL", { day: "numeric", month: "numeric", timeZone: "Asia/Jerusalem" }).replace(/\//g, ".");
  const now = Date.now();
  let text = `${fmt(start)}–${fmt(new Date(end.getTime() - 1))}`;
  if (now < start.getTime()) text = `נפתח ב־${fmt(start)}`;
  else if (now < end.getTime()) {
    const days = Math.ceil((end.getTime() - now) / 86400000);
    text += ` · ${days === 1 ? "יום אחרון" : `נותרו ${days} ימים`}`;
  } else text = "הסבב הסתיים";
  note.textContent = text;
}

// ---------------------------------------------------------------- init

async function init() {
  renderProducts();
  renderCartBadge();
  cart.subscribe(() => {
    renderCartBadge();
    if (dialog.open) renderCart();
  });

  const saved = customerStore.load();
  for (const [k, f] of Object.entries(fields)) if (saved[k]) f.input.value = saved[k];
  for (const f of Object.values(fields)) {
    f.input.addEventListener("input", () => {
      if (f.input.getAttribute("aria-invalid") === "true" && f.valid(f.input.value)) {
        f.input.removeAttribute("aria-invalid");
        f.error.hidden = true;
      }
    });
  }

  $("#open-cart").addEventListener("click", openCart);
  $("#toast-open-cart").addEventListener("click", openCart);
  $("#close-cart").addEventListener("click", closeCart);
  $("#cart-browse").addEventListener("click", () => {
    closeCart();
    $("#options").focus();
    $("#options").scrollIntoView();
  });
  dialog.addEventListener("click", (e) => { if (e.target === dialog) closeCart(); }); // backdrop click
  dialog.addEventListener("close", () => $("#open-cart").focus());
  form.addEventListener("submit", checkout);

  // Returning with "back" from the payment page restores a bfcached page: re-enable the button.
  window.addEventListener("pageshow", (e) => { if (e.persisted) setBusy(false); });

  if (new URLSearchParams(location.search).get("cart") === "open") openCart();

  try {
    const res = await fetch("/api/config");
    if (res.ok) config = { ...config, ...(await res.json()) };
  } catch { /* keep the safe defaults: test mode banner on */ }
  $("#test-banner").hidden = config.liveCharges;
  if (!config.liveCharges) $("#checkout-note").textContent =
    "מצב בדיקה: דף התשלום הוא דף לדוגמה ולא יבוצע חיוב. בגרסה הפעילה התשלום יתבצע בעמוד מאובטח של ספק הסליקה, ופרטי האשראי לא יוזנו באתר הזה.";
  setBusy(false);
  renderRound();
}

init();
