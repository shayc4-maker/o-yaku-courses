// O‑Yaku admin UI. Plain DOM, no innerHTML for data. All data comes from /api/admin/*,
// which the server only answers for an authenticated owner.
import { PRODUCTS, formatShekels } from "/catalog.js";

const view = document.getElementById("view");
const scopeBox = document.getElementById("scope-test");

const PAYMENT = { awaiting_payment: "ממתין לתשלום", paid: "שולם", needs_review: "דורש בדיקה", cancelled: "לא הושלם", failed_to_start: "לא נפתח תשלום" };
const STATE = { na: "אין שובר", not_redeemed: "טרם מומש", partial: "מומש חלקית", full: "מומש במלואו", expired: "פג תוקף", cancelled: "בוטל" };
const MODE = { morning_live: "אמיתי", morning_sandbox: "Sandbox", mock: "הדמיה" };
const NOTE_KINDS = {
  note: "הערה פנימית", session: "מועד סדנה / שיעור", shirt_size: "מידת חולצה", pickup: "תיאום איסוף",
  shipping: "תיאום משלוח", pot_details: "פרטי כלי בהזמנה אישית", trees_in: "הכנסת עצים", service_end: "סיום שנת השירות",
};
const DATE_KINDS = new Set(["trees_in", "service_end"]);
const ERRORS = {
  insufficient_balance: "הכמות גדולה מהיתרה.",
  redemption_not_started: "המימוש מתחיל בינואר 2027.",
  date_before_redemption_start: "תאריך המימוש לפני ינואר 2027.",
  date_in_future: "תאריך המימוש בעתיד.",
  date_after_expiry: "תאריך המימוש אחרי תום תוקף השובר.",
  voucher_expired: "תוקף השובר פג.",
  voucher_cancelled: "השובר בוטל.",
  order_not_paid: "ההזמנה לא שולמה.",
  invalid_quantity: "כמות לא תקינה — מספר שלם בלבד.",
  invalid_date: "תאריך לא תקין.",
  reason_required: "יש לכתוב סיבה.",
  confirm_required: "יש לאשר את הביטול.",
  correction_exceeds_redemption: "התיקון גדול מהכמות שנותרה במימוש המקורי.",
  idempotency_conflict: "הפעולה כבר נשלחה עם פרטים אחרים. רעננו את הדף.",
  csrf_origin: "בקשה נחסמה (מקור).",
  token_missing: "פג תוקף ההתחברות. רעננו את הדף.",
  token_expired: "פג תוקף ההתחברות. רעננו את הדף.",
  not_an_admin: "אין הרשאת ניהול.",
  admin_not_configured: "אזור הניהול לא הוגדר.",
  value_required: "יש למלא ערך.",
  network: "אין חיבור לשרת.",
};

// ------------------------------------------------------------------ helpers

function h(tag, attrs = {}, ...children) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === false || v == null) continue;
    if (k === "class") n.className = v;
    else if (k === "text") n.textContent = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat(Infinity)) if (c != null && c !== false) n.append(c);
  return n;
}
const fmtDate = (iso) => (iso ? new Date(iso).toLocaleDateString("he-IL", { timeZone: "Asia/Jerusalem" }) : "—");
const fmtDateTime = (iso) => (iso ? new Date(iso).toLocaleString("he-IL", { timeZone: "Asia/Jerusalem", dateStyle: "short", timeStyle: "short" }) : "—");
const money = (a) => h("span", { class: "num", text: formatShekels(a) });
const badge = (cls, text) => h("span", { class: `badge badge-${cls}`, text });
const modeBadge = (m) => (m === "morning_live" ? null : badge("test", MODE[m] || m));
const newKey = () => crypto.randomUUID().replace(/-/g, "") + Date.now().toString(36);
const errText = (e) => ERRORS[e?.code] || (e?.code ? `שגיאה (${e.code})` : "שגיאה");
const scope = () => (scopeBox.checked ? "test" : "live");

class ApiErr extends Error {
  constructor(code, status, data) { super(code); this.code = code; this.status = status; this.data = data; }
}
async function api(path, { method = "GET", body } = {}) {
  let res;
  try {
    res = await fetch(`/api/admin${path}`, {
      method,
      credentials: "same-origin",
      cache: "no-store",
      headers: method === "POST" ? { "Content-Type": "application/json", "X-OY-Admin": "1" } : {},
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiErr("network", 0);
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiErr(data.error || "server_error", res.status, data);
  return data;
}
function withScope(path) {
  return path + (path.includes("?") ? "&" : "?") + "scope=" + scope();
}

// replaceChildren() would print "null" for empty slots; drop them first.
function render(...nodes) {
  view.replaceChildren(...nodes.flat(Infinity).filter((n) => n != null && n !== false));
}

function loading() {
  render(h("p", { class: "muted", role: "status", text: "טוען…" }));
}
function showError(e, retry) {
  render(h("div", { class: "notice-box notice-error", role: "alert" },
    h("p", { text: errText(e) }), retry && h("button", { class: "btn btn-secondary btn-sm", type: "button", onclick: retry }, "ניסיון חוזר")));
}
function emptyState(text) {
  return h("p", { class: "muted", text });
}
function td(label, ...content) {
  return h("td", { "data-label": label }, h("span", {}, ...content));
}

// Submit helper: disables the button, keeps one idempotency key per form until success.
function bindSubmit(form, button, statusEl, run) {
  let key = newKey();
  let busy = false;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (busy) return;
    busy = true;
    button.disabled = true;
    statusEl.className = "notice-box";
    statusEl.textContent = "שומר…";
    statusEl.hidden = false;
    try {
      await run(key);
      key = newKey();
      statusEl.className = "notice-box notice-ok";
      statusEl.textContent = "נשמר.";
      setTimeout(route, 400);
    } catch (err) {
      statusEl.className = "notice-box notice-error";
      statusEl.setAttribute("role", "alert");
      const extra = err.data?.remaining != null ? ` יתרה: ${err.data.remaining}.` : "";
      statusEl.textContent = errText(err) + extra;
      if (err.code === "idempotency_conflict") key = newKey();
    } finally {
      busy = false;
      button.disabled = false;
    }
  });
}

// ------------------------------------------------------------------ views

async function viewSummary() {
  const s = await api(withScope("/summary"));
  const pending = Object.entries(s.notSales || {});
  render(
    h("h1", { text: s.scope === "live" ? "סיכום מכירות" : "סיכום — מצב בדיקה" }),
    h("dl", { class: "stats" },
      h("div", { class: "stat" }, h("dt", { text: "הכנסות מאושרות (כולל מע״מ)" }), h("dd", {}, money(s.revenueAgorot))),
      h("div", { class: "stat" }, h("dt", { text: "הזמנות ששולמו" }), h("dd", { text: String(s.paidOrders) })),
      h("div", { class: "stat" }, h("dt", { text: "קונים עם רכישה מאושרת" }), h("dd", { text: String(s.buyers) })),
    ),
    h("section", { class: "panel" },
      h("h2", { text: "מצב שוברים" }),
      Object.keys(s.redemptionStates).length
        ? h("div", { class: "badges" }, Object.entries(s.redemptionStates).map(([k, n]) => badge(k, `${STATE[k]}: ${n}`)))
        : emptyState("אין שוברים עדיין.")),
    h("section", { class: "panel" },
      h("h2", { text: "בקשות שאינן מכירות" }),
      h("p", { class: "small muted", text: "בקשות תשלום שלא הושלמו אינן נספרות בהכנסות." }),
      pending.length ? h("div", { class: "badges" }, pending.map(([k, n]) => badge(k, `${PAYMENT[k] || k}: ${n}`))) : emptyState("אין.")),
  );
}

function selectField(id, label, options, value) {
  return h("div", { class: "field" }, h("label", { for: id, text: label }),
    h("select", { id, name: id }, options.map(([v, t]) => h("option", { value: v, selected: v === value, text: t }))));
}
function inputField(id, label, attrs = {}) {
  return h("div", { class: `field ${attrs.wide ? "field-wide" : ""}` }, h("label", { for: id, text: label }),
    h(attrs.textarea ? "textarea" : "input", { id, name: id, ...attrs, wide: null, textarea: null }));
}

async function viewOrders(params) {
  const p = new URLSearchParams(params);
  const data = await api(withScope(`/orders?${p}`));
  const form = h("form", { class: "filters", role: "search" },
    inputField("q", "חיפוש (מספר, שם, טלפון, אימייל)", { type: "search", value: p.get("q") || "", wide: true }),
    selectField("product", "מוצר", [["", "הכול"], ...PRODUCTS.map((x) => [x.id, x.name])], p.get("product") || ""),
    selectField("payment", "תשלום", [["", "הכול"], ...Object.entries(PAYMENT)], p.get("payment") || ""),
    selectField("redemption", "מימוש", [["", "הכול"], ...Object.entries(STATE).filter(([k]) => k !== "na")], p.get("redemption") || ""),
    inputField("from", "מתאריך", { type: "date", value: p.get("from") || "" }),
    inputField("to", "עד תאריך", { type: "date", value: p.get("to") || "" }),
    selectField("sort", "מיון", [["created", "תאריך הזמנה"], ["paid", "תאריך תשלום"], ["total", "סכום"], ["name", "שם"], ["id", "מספר"]], p.get("sort") || "created"),
    selectField("dir", "כיוון", [["desc", "יורד"], ["asc", "עולה"]], p.get("dir") || "desc"),
    h("div", { class: "row-actions" }, h("button", { class: "btn btn-primary btn-sm", type: "submit" }, "סינון"),
      h("a", { class: "btn btn-ghost btn-sm", href: "#/orders" }, "ניקוי")),
  );
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = new URLSearchParams();
    for (const [k, v] of new FormData(form)) if (v) q.set(k, v);
    location.hash = `#/orders?${q}`;
  });

  const rows = data.orders.map((o) => h("tr", {},
    td("הזמנה", h("a", { href: `#/orders/${o.id}`, text: o.id })),
    td("תאריך", fmtDate(o.createdAt)),
    td("קונה", o.buyerId ? h("a", { href: `#/buyers/${o.buyerId}`, text: o.customer.name }) : o.customer.name),
    td("פריטים", o.itemsText || ""),
    td("סה״כ", money(o.totalAgorot)),
    td("תשלום", h("span", { class: "badges" }, badge(o.status, PAYMENT[o.status] || o.status), modeBadge(o.paymentMode))),
    td("מימוש", o.redemptionState === "na" ? "—" : badge(o.redemptionState, STATE[o.redemptionState])),
    td("תוקף", fmtDate(o.expiresAt)),
  ));
  const active = ["product", "payment", "redemption", "from", "to"].filter((k) => p.get(k)).length;
  const filters = h("details", { class: "panel filters-panel", open: active > 0 || window.matchMedia("(min-width: 761px)").matches },
    h("summary", { text: active ? `סינון ומיון · ${active} פעילים` : "סינון ומיון" }), form);
  render(
    h("h1", { text: "הזמנות" }),
    filters,
    h("p", { class: "small muted", text: `${data.total} הזמנות` }),
    data.orders.length
      ? h("table", { class: "data-table" },
          h("thead", {}, h("tr", {}, ["הזמנה", "תאריך", "קונה", "פריטים", "סה״כ", "תשלום", "מימוש", "תוקף"].map((t) => h("th", { scope: "col", text: t })))),
          h("tbody", {}, rows))
      : emptyState("אין הזמנות שמתאימות לסינון."),
    pager(data, (page) => { p.set("page", page); location.hash = `#/orders?${p}`; }),
  );
}

function pager(data, go) {
  const pages = Math.max(1, Math.ceil(data.total / data.pageSize));
  if (pages <= 1) return null;
  return h("nav", { class: "pager", "aria-label": "דפדוף" },
    h("button", { class: "btn btn-secondary btn-sm", type: "button", disabled: data.page <= 1, onclick: () => go(data.page - 1) }, "הקודם"),
    h("span", { class: "small", text: `עמוד ${data.page} מתוך ${pages}` }),
    h("button", { class: "btn btn-secondary btn-sm", type: "button", disabled: data.page >= pages, onclick: () => go(data.page + 1) }, "הבא"));
}

function contactBlock(c) {
  const tel = c.phone.replace(/[^\d+]/g, "");
  return h("div", { class: "contact" },
    h("strong", { text: c.name }),
    h("a", { href: `tel:${tel}`, dir: "ltr", text: c.phone }),
    h("a", { href: `mailto:${encodeURIComponent(c.email).replace(/%40/g, "@")}`, dir: "ltr", text: c.email }));
}

async function viewOrder(id) {
  const o = await api(`/orders/${encodeURIComponent(id)}`);
  const me = await api("/me");
  const test = o.paymentMode !== "morning_live";
  const redeemable = o.voucher && !["cancelled", "expired", "full"].includes(o.voucher.state);

  const lines = o.lines.map((l) => {
    const box = h("div", { class: "line" },
      h("div", { class: "line-head" },
        h("h3", { text: l.name }),
        l.state !== "na" ? badge(l.state, STATE[l.state]) : null),
      h("p", { class: "small muted" }, `${l.quantityLabel} · `, money(l.unitPriceAgorot), " ליחידה · ", money(l.lineTotalAgorot)),
      o.voucher ? h("p", { class: "balance" },
        `למימוש: ${l.units} ${l.unitLabel} · מומשו ${l.redeemed} · `, h("strong", { text: `יתרה ${o.voucher.state === "cancelled" || o.voucher.state === "expired" ? 0 : l.remaining}` })) : null,
    );
    if (redeemable && l.remaining > 0) {
      const formId = `r-${l.productId}`;
      const btn = h("button", { class: "btn btn-primary btn-sm", type: "submit" }, "רישום מימוש");
      const status = h("p", { class: "notice-box", hidden: true });
      const form = h("form", { class: "inline-form", "aria-label": `מימוש ${l.name}` },
        inputField(`${formId}-qty`, `כמות (${l.unitLabel})`, { type: "number", min: "1", max: String(l.remaining), step: "1", required: true, inputmode: "numeric" }),
        inputField(`${formId}-date`, "תאריך", { type: "date", value: me.today, required: true, min: me.redemptionStartsOn, max: me.today }),
        inputField(`${formId}-note`, "הערה (פנימית)", { wide: true, maxlength: "500" }),
        h("div", { class: "row-actions" }, btn), status);
      bindSubmit(form, btn, status, (key) => {
        const qty = Number(form.querySelector(`#${formId}-qty`).value);
        return api(`/orders/${o.id}/redemptions`, { method: "POST", body: {
          idempotencyKey: key, productId: l.productId, quantity: qty,
          date: form.querySelector(`#${formId}-date`).value, note: form.querySelector(`#${formId}-note`).value,
        } });
      });
      const toggle = h("button", { class: "btn btn-secondary btn-sm", type: "button", "aria-expanded": "false" }, "מימוש");
      form.hidden = true;
      toggle.addEventListener("click", () => { form.hidden = !form.hidden; toggle.setAttribute("aria-expanded", String(!form.hidden)); if (!form.hidden) form.querySelector("input").focus(); });
      box.append(h("div", { class: "row-actions" }, toggle), form);
    }
    return box;
  });

  const redemptionRows = o.redemptions.map((r) => {
    const line = o.lines.find((l) => l.productId === r.productId);
    const cells = [
      td("#", String(r.id)),
      td("סוג", r.kind === "redeem" ? "מימוש" : `תיקון ל־#${r.correctsId}`),
      td("מוצר", line?.name || r.productId),
      td("כמות", r.kind === "redeem" ? `${r.quantity} ${line?.unitLabel || ""}` : `הפחתה של ${Math.abs(r.quantity)} ${line?.unitLabel || ""}`),
      td("תאריך", r.redeemedOn),
      td("הערה / סיבה", r.note || r.reason || ""),
      td("ע״י", r.by),
    ];
    const tr = h("tr", {}, cells);
    if (r.kind === "redeem" && r.correctable > 0) {
      const btn = h("button", { class: "btn btn-secondary btn-sm", type: "submit" }, "שמירת תיקון");
      const status = h("p", { class: "notice-box", hidden: true });
      const fid = `c-${r.id}`;
      const form = h("form", { class: "inline-form", "aria-label": `תיקון מימוש ${r.id}` },
        inputField(`${fid}-qty`, `כמות לביטול (עד ${r.correctable})`, { type: "number", min: "1", max: String(r.correctable), step: "1", required: true }),
        inputField(`${fid}-reason`, "סיבת התיקון", { required: true, minlength: "3", maxlength: "500", wide: true }),
        h("div", { class: "row-actions" }, btn), status);
      bindSubmit(form, btn, status, (key) => api(`/redemptions/${r.id}/corrections`, { method: "POST", body: {
        idempotencyKey: key, quantity: Number(form.querySelector(`#${fid}-qty`).value), reason: form.querySelector(`#${fid}-reason`).value,
      } }));
      const toggle = h("button", { class: "btn btn-ghost btn-sm", type: "button", "aria-expanded": "false" }, "תיקון");
      const formRow = h("tr", { class: "form-row", hidden: true }, h("td", { colspan: "8" }, form));
      toggle.addEventListener("click", () => {
        formRow.hidden = !formRow.hidden;
        toggle.setAttribute("aria-expanded", String(!formRow.hidden));
        if (!formRow.hidden) form.querySelector("input").focus();
      });
      tr.append(td("", toggle));
      return [tr, formRow];
    }
    tr.append(td("", ""));
    return tr;
  });

  // Coordination form
  const coordBtn = h("button", { class: "btn btn-secondary btn-sm", type: "submit" }, "שמירה");
  const coordStatus = h("p", { class: "notice-box", hidden: true });
  const kindSel = selectField("n-kind", "סוג", Object.entries(NOTE_KINDS), "note");
  const valueWrap = h("div", { class: "field field-wide" });
  const renderValue = () => {
    const k = kindSel.querySelector("select").value;
    valueWrap.replaceChildren(h("label", { for: "n-value", text: DATE_KINDS.has(k) ? "תאריך" : "תוכן" }),
      DATE_KINDS.has(k) ? h("input", { id: "n-value", type: "date", required: true })
        : h("textarea", { id: "n-value", required: true, maxlength: "1000" }));
  };
  kindSel.querySelector("select").addEventListener("change", renderValue);
  renderValue();
  const coordForm = h("form", { class: "inline-form", "aria-label": "תיאום והערות" },
    kindSel, selectField("n-product", "מוצר", [["", "כל ההזמנה"], ...o.lines.map((l) => [l.productId, l.name])], ""),
    valueWrap, h("div", { class: "row-actions" }, coordBtn), coordStatus);
  bindSubmit(coordForm, coordBtn, coordStatus, () => api(`/orders/${o.id}/notes`, { method: "POST", body: {
    kind: coordForm.querySelector("#n-kind").value, productId: coordForm.querySelector("#n-product").value || null,
    value: coordForm.querySelector("#n-value").value,
  } }));

  // Voucher cancellation (blocks redemption only)
  let cancelPanel = null;
  if (o.voucher && !o.voucher.cancelledAt) {
    const btn = h("button", { class: "btn btn-danger btn-sm", type: "submit" }, "ביטול השובר");
    const status = h("p", { class: "notice-box", hidden: true });
    const form = h("form", { class: "inline-form" },
      inputField("cancel-reason", "סיבת הביטול", { required: true, minlength: "3", maxlength: "500", wide: true }),
      h("label", { class: "field-wide small" }, h("input", { type: "checkbox", id: "cancel-confirm", required: true }),
        " הבנתי: ביטול השובר חוסם מימוש בלבד. הוא אינו החזר כספי ואינו משנה את מצב התשלום."),
      h("div", { class: "row-actions" }, btn), status);
    bindSubmit(form, btn, status, () => api(`/orders/${o.id}/cancel-voucher`, { method: "POST", body: {
      reason: form.querySelector("#cancel-reason").value, confirm: form.querySelector("#cancel-confirm").checked,
    } }));
    cancelPanel = h("section", { class: "panel panel-danger" }, h("h2", { text: "ביטול שובר" }),
      h("p", { class: "small", text: "חוסם מימוש עתידי. החזר כספי, אם יידרש, מתבצע מול ספק הסליקה ואינו נרשם כאן." }), form);
  }

  render(
    h("p", {}, h("a", { href: "#/orders", text: "← הזמנות" })),
    test ? h("p", { class: "notice-box notice-warn", role: "note", text: `הזמנת ${MODE[o.paymentMode]} — אינה מכירה אמיתית. שובר לדוגמה בלבד.` }) : null,
    h("div", { class: "line-head" }, h("h1", { text: `הזמנה ${o.id}` }),
      h("div", { class: "badges" }, badge(o.status, PAYMENT[o.status] || o.status), modeBadge(o.paymentMode),
        o.voucher ? badge(o.voucher.state, `שובר: ${STATE[o.voucher.state]}`) : null)),
    h("div", { class: "two-col" },
      h("div", { class: "admin-col" },
        h("section", { class: "panel" }, h("h2", { text: "פריטים ויתרות" }), lines,
          h("p", { class: "cart-total" }, h("span", { text: "סה״כ (כולל מע״מ)" }), money(o.totalAgorot)),
          o.voucher?.state === "cancelled" ? h("p", { class: "notice-box notice-error", text: `השובר בוטל ${fmtDateTime(o.voucher.cancelledAt)} ע״י ${o.voucher.cancelledBy}: ${o.voucher.cancelReason}` }) : null,
          !o.voucher && o.status !== "paid" ? h("p", { class: "small muted", text: "אין שובר: ההזמנה לא שולמה. אי אפשר לסמן תשלום ידנית — רק אימות מול Morning." }) : null),
        h("section", { class: "panel" }, h("h2", { text: "מימושים" }),
          o.redemptions.length
            ? h("table", { class: "data-table" }, h("thead", {}, h("tr", {}, ["#", "סוג", "מוצר", "כמות", "תאריך", "הערה / סיבה", "ע״י", ""].map((t) => h("th", { scope: "col", text: t })))),
                h("tbody", {}, redemptionRows))
            : emptyState("עדיין לא נרשמו מימושים.")),
        h("section", { class: "panel" }, h("h2", { text: "תיאום והערות" }),
          o.coordination.length ? h("dl", { class: "kv" }, o.coordination.flatMap((c) => [
            h("dt", { text: `${NOTE_KINDS[c.kind] || c.kind}${c.productId ? ` · ${o.lines.find((l) => l.productId === c.productId)?.name || ""}` : ""}` }),
            h("dd", { text: c.value })])) : null,
          o.notes.length ? h("ul", { class: "history" }, o.notes.map((n) => h("li", {}, h("time", { text: `${fmtDateTime(n.at)} · ${n.by}` }), h("span", { text: n.value })))) : null,
          h("p", { class: "small muted", text: "נתוני תיאום אינם משנים את הכמות שמומשה." }),
          coordForm),
        cancelPanel),
      h("div", { class: "admin-col" },
        h("section", { class: "panel" }, h("h2", { text: "קונה" }), contactBlock(o.customer),
          o.buyerId ? h("p", { class: "small" }, h("a", { href: `#/buyers/${o.buyerId}`, text: "כרטיס קונה" })) : null),
        h("section", { class: "panel" }, h("h2", { text: "פרטים" }),
          h("dl", { class: "kv" },
            h("dt", { text: "נוצרה" }), h("dd", { text: fmtDateTime(o.createdAt) }),
            h("dt", { text: "שולמה" }), h("dd", { text: fmtDateTime(o.paidAt) }),
            h("dt", { text: "תוקף שובר" }), h("dd", { text: fmtDate(o.voucher?.expiresAt) }),
            h("dt", { text: "סביבת תשלום" }), h("dd", { text: MODE[o.paymentMode] || o.paymentMode }),
            h("dt", { text: "תנאים" }), h("dd", { text: o.termsVersion || "—" }),
            h("dt", { text: "מסמך Morning" }), h("dd", { text: o.providerDocumentId || "—" }),
            o.statusReason ? [h("dt", { text: "הערת מערכת" }), h("dd", { text: o.statusReason })] : null)),
        h("section", { class: "panel" }, h("h2", { text: "היסטוריה" }),
          h("ol", { class: "history" }, o.history.map((e) => h("li", {},
            h("time", { text: `${fmtDateTime(e.at)}${e.by ? ` · ${e.by}` : ""}` }),
            h("span", { text: e.text }),
            e.note ? h("span", { class: "muted", text: `הערה: ${e.note}` }) : null,
            e.reason ? h("span", { class: "muted", text: `סיבה: ${e.reason}` }) : null))))),
    ),
  );
}

async function viewBuyers(params) {
  const p = new URLSearchParams(params);
  const data = await api(withScope(`/buyers?${p}`));
  const form = h("form", { class: "panel filters", role: "search" },
    inputField("bq", "חיפוש לפי שם, טלפון או אימייל", { type: "search", value: p.get("q") || "", wide: true }),
    h("div", { class: "row-actions" }, h("button", { class: "btn btn-primary btn-sm", type: "submit" }, "חיפוש")));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = form.querySelector("#bq").value.trim();
    location.hash = q ? `#/buyers?q=${encodeURIComponent(q)}` : "#/buyers";
  });
  render(
    h("h1", { text: "קונים" }), form,
    h("p", { class: "small muted", text: `${data.total} קונים` }),
    data.buyers.length
      ? h("table", { class: "data-table" },
          h("thead", {}, h("tr", {}, ["שם", "טלפון", "אימייל", "הזמנות", "שולמו", "סכום ששולם", "הזמנה אחרונה"].map((t) => h("th", { scope: "col", text: t })))),
          h("tbody", {}, data.buyers.map((b) => h("tr", {},
            td("שם", h("a", { href: `#/buyers/${b.id}`, text: b.name })),
            td("טלפון", h("span", { dir: "ltr", text: b.phone })),
            td("אימייל", h("span", { dir: "ltr", text: b.email })),
            td("הזמנות", String(b.orders)), td("שולמו", String(b.paidOrders)),
            td("סכום ששולם", money(b.paidAgorot)), td("הזמנה אחרונה", fmtDate(b.lastOrderAt))))))
      : emptyState("לא נמצאו קונים."),
    pager(data, (page) => { p.set("page", page); location.hash = `#/buyers?${p}`; }),
  );
}

async function viewBuyer(id) {
  const b = await api(`/buyers/${encodeURIComponent(id)}`);
  render(
    h("p", {}, h("a", { href: "#/buyers", text: "← קונים" })),
    h("h1", { text: b.name }),
    h("div", { class: "two-col" },
      h("div", { class: "admin-col" },
        h("section", { class: "panel" }, h("h2", { text: "הזמנות" }),
          h("table", { class: "data-table" },
            h("thead", {}, h("tr", {}, ["הזמנה", "תאריך", "סה״כ", "תשלום", "מימוש"].map((t) => h("th", { scope: "col", text: t })))),
            h("tbody", {}, b.orders.map((o) => h("tr", {},
              td("הזמנה", h("a", { href: `#/orders/${o.id}`, text: o.id })), td("תאריך", fmtDate(o.createdAt)), td("סה״כ", money(o.totalAgorot)),
              td("תשלום", h("span", { class: "badges" }, badge(o.status, PAYMENT[o.status] || o.status), modeBadge(o.paymentMode))),
              td("מימוש", o.redemptionState === "na" ? "—" : badge(o.redemptionState, STATE[o.redemptionState]))))))),
        h("section", { class: "panel" }, h("h2", { text: "שוברים ויתרות" }),
          b.balances.length ? h("table", { class: "data-table" },
            h("thead", {}, h("tr", {}, ["הזמנה", "מוצר", "נרכש", "מומש", "יתרה", "מצב"].map((t) => h("th", { scope: "col", text: t })))),
            h("tbody", {}, b.balances.map((l) => h("tr", {},
              td("הזמנה", h("a", { href: `#/orders/${l.orderId}`, text: l.orderId }), " ", modeBadge(l.paymentMode)),
              td("מוצר", l.name), td("נרכש", `${l.quantityLabel} (${l.units} ${l.unitLabel})`), td("מומש", String(l.redeemed)),
              td("יתרה", `${l.remaining} ${l.unitLabel}`), td("מצב", badge(l.state, STATE[l.state]))))))
            : emptyState("אין שוברים ששולמו."))),
      h("div", { class: "admin-col" },
        h("section", { class: "panel" }, h("h2", { text: "פרטי קשר" }), contactBlock(b),
          h("p", { class: "small muted", text: "חיוג ומייל נפתחים במכשיר שלך. לא נשלחות הודעות אוטומטיות." })),
        h("section", { class: "panel" }, h("h2", { text: "רכישות אמיתיות שאושרו" }),
          h("p", {}, money(b.paidLiveAgorot), ` · ${b.paidLiveOrders} הזמנות`)),
        b.detailVariants.length || b.samePhoneOtherBuyers.length ? h("section", { class: "panel" }, h("h2", { text: "לבדיקה ידנית" }),
          b.detailVariants.length ? [h("p", { class: "small", text: "פרטים שונים בהזמנות של אותו אימייל (לא אוחדו):" }),
            h("ul", { class: "small" }, b.detailVariants.map((v) => h("li", { text: v })))] : null,
          b.samePhoneOtherBuyers.length ? [h("p", { class: "small", text: "אותו טלפון אצל קונים אחרים (לא אוחדו אוטומטית):" }),
            h("ul", { class: "small" }, b.samePhoneOtherBuyers.map((x) => h("li", {}, h("a", { href: `#/buyers/${x.id}`, text: `${x.name} · ${x.email}` }))))] : null) : null)),
  );
}

async function viewProducts() {
  const data = await api(withScope("/products"));
  render(
    h("h1", { text: "מוצרים" }),
    h("p", { class: "small muted", text: "יחידות מהזמנות ששולמו. סכומים בשקלים, כולל מע״מ. „לא למימוש” = יתרה בשוברים שבוטלו או שפג תוקפם." }),
    h("table", { class: "data-table" },
      h("thead", {}, h("tr", {}, ["מוצר", "נמכרו", "הכנסה", "מומשו", "יתרה למסירה", "לא למימוש"].map((t) => h("th", { scope: "col", text: t })))),
      h("tbody", {}, data.products.map((p) => {
        const packs = p.perSaleUnit > 1;
        const u = (n) => `${n} ${p.redeemUnit}`;
        return h("tr", {},
          td("מוצר", p.name),
          td("נמכרו", packs ? `${p.soldQty} ${p.saleUnit} · ${u(p.soldUnits)}` : `${p.soldQty} ${p.saleUnit}`),
          td("הכנסה", money(p.revenueAgorot)),
          td("מומשו", u(p.redeemedUnits)),
          td("יתרה למסירה", packs ? `${u(p.remainingUnits)} (${(p.remainingUnits / p.perSaleUnit).toLocaleString("he-IL", { maximumFractionDigits: 1 })} ${p.saleUnit})` : u(p.remainingUnits)),
          td("לא למימוש", u(p.lapsedUnits)));
      }))),
  );
}

function viewExport() {
  const link = (kind, text) => h("a", { class: "btn btn-secondary", href: `/api/admin/export/${kind}.csv?scope=${scope()}`, download: "" }, text);
  render(
    h("h1", { text: "יצוא CSV" }),
    h("section", { class: "panel export-list" },
      h("p", { class: "small", text: scope() === "live" ? "מכירות אמיתיות בלבד (morning_live)." : "מצב בדיקה: הדמיה ו־Sandbox בלבד. כל שורה מסומנת בעמודת סביבה." }),
      link("buyers", "קונים"), link("orders", "הזמנות"), link("balances", "יתרות למימוש"),
      h("p", { class: "small muted", text: "הקבצים בקידוד UTF‑8 עם BOM לעברית תקינה באקסל. אינם כוללים קישורי לקוח, טוקנים או הודעות סליקה גולמיות." })),
  );
}

// ------------------------------------------------------------------ routing

async function route() {
  const hash = location.hash.slice(1) || "/";
  const [path, query = ""] = hash.split("?");
  const parts = path.split("/").filter(Boolean);
  const section = parts[0] || "summary";
  for (const a of document.querySelectorAll("[data-nav]")) {
    if (a.dataset.nav === section) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  }
  const run = async () => {
    loading();
    try {
      if (section === "summary") await viewSummary();
      else if (section === "orders" && parts[1]) await viewOrder(decodeURIComponent(parts[1]));
      else if (section === "orders") await viewOrders(query);
      else if (section === "buyers" && parts[1]) await viewBuyer(parts[1]);
      else if (section === "buyers") await viewBuyers(query);
      else if (section === "products") await viewProducts();
      else if (section === "export") viewExport();
      else render(emptyState("הדף לא נמצא."));
    } catch (e) {
      showError(e, run);
    }
  };
  await run();
}

function applyScopeUi() {
  document.getElementById("scope-banner").hidden = !scopeBox.checked;
}

try { scopeBox.checked = sessionStorage.getItem("oy-admin-scope") === "test"; } catch {}
applyScopeUi();
scopeBox.addEventListener("change", () => {
  try { sessionStorage.setItem("oy-admin-scope", scope()); } catch {}
  applyScopeUi();
  route();
});
window.addEventListener("hashchange", route);
api("/me").then((m) => { document.getElementById("who").textContent = `מחובר: ${m.email} · סליקה: ${m.paymentMode}`; }).catch(() => {});
route();
