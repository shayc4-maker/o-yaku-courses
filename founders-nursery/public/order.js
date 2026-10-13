import { formatShekels } from "./catalog.js";
import { createCartStore, attemptStore } from "./cart-store.js";

const $ = (s) => document.querySelector(s);
const params = new URLSearchParams(location.search);
const orderId = params.get("order");
const token = params.get("t");

function setStatus(kind, title, text) {
  const box = $("#status-box");
  box.classList.toggle("is-success", kind === "success");
  box.classList.toggle("is-danger", kind === "danger");
  $("#status-title").textContent = title;
  $("#status-text").textContent = text;
}

function setActions(...links) {
  $("#actions").replaceChildren(...links.map(([href, label, primary]) => {
    const a = document.createElement("a");
    a.href = href;
    a.className = `btn ${primary ? "btn-primary" : "btn-secondary"}`;
    a.textContent = label;
    return a;
  }));
}

function renderSummary(order) {
  $("#summary-body").replaceChildren(...order.items.map((i) => {
    const tr = document.createElement("tr");
    const name = document.createElement("td");
    name.append(i.name, document.createElement("br"));
    const meta = document.createElement("small");
    meta.textContent = `${i.quantityLabel} × ${formatShekels(i.unitPriceAgorot)}`;
    name.append(meta);
    const total = document.createElement("td");
    total.className = "num";
    total.textContent = formatShekels(i.lineTotalAgorot);
    tr.append(name, total);
    return tr;
  }));
  $("#summary-total").textContent = formatShekels(order.totalAgorot);
  $("#summary").hidden = false;
}

const LINE_STATE = { not_redeemed: "טרם מומש", partial: "מומש חלקית", full: "מומש במלואו", expired: "פג תוקף", cancelled: "בוטל" };
const VOUCHER_STATE = {
  partial: "השובר מומש חלקית. היתרות מעודכנות לפי רישום העסק.",
  full: "השובר מומש במלואו. אין יתרה למימוש.",
  expired: "תוקף השובר פג. אין יתרה למימוש.",
  cancelled: "השובר בוטל ואינו ניתן למימוש.",
};

function renderVoucher(order) {
  const voucher = order.voucher;
  if (!voucher) return;
  const date = (v) => new Date(v).toLocaleDateString("he-IL", { timeZone: "Asia/Jerusalem" });
  const pairs = [["מספר שובר", voucher.number], ["שם הרוכש", voucher.holder],
    ["תאריך רכישה", date(voucher.issuedAt)], ["בתוקף עד", date(voucher.expiresAt)]];
  $("#voucher-meta").replaceChildren(...pairs.flatMap(([label, value]) => {
    const dt = document.createElement("dt"); dt.textContent = label;
    const dd = document.createElement("dd"); dd.textContent = value;
    return [dt, dd];
  }));
  $("#voucher-items").replaceChildren(...order.items.map((item) => {
    const li = document.createElement("li");
    const title = document.createElement("strong"); title.textContent = `${item.name} · ${item.quantityLabel}`;
    const p = document.createElement("p"); p.textContent = item.redemption || "לתיאום המימוש יש לפנות לעסק.";
    li.append(title, p);
    if (item.redeemUnits != null) {
      // Current balance as recorded by the business. No internal notes are ever sent here.
      const bal = document.createElement("p");
      bal.className = "voucher-balance";
      bal.textContent = `יתרה למימוש: ${item.remainingUnits} מתוך ${item.redeemUnits} ${item.redeemUnitLabel} · ${LINE_STATE[item.state] || ""}`;
      li.append(bal);
    }
    return li;
  }));
  const stateNote = $("#voucher-state");
  const stateText = VOUCHER_STATE[voucher.state];
  stateNote.textContent = stateText || "";
  stateNote.hidden = !stateText;
  $("#voucher-example").hidden = !voucher.example;
  $("#print-voucher").onclick = () => window.print();
  $("#voucher").hidden = false;
  document.title = `${voucher.example ? "שובר לדוגמה" : "שובר"} ${voucher.number} · אויאקו`;
}

async function fetchOrder() {
  const res = await fetch(`/api/orders/${encodeURIComponent(orderId)}?t=${encodeURIComponent(token)}`, { cache: "no-store" });
  if (!res.ok) throw new Error(String(res.status));
  return res.json();
}

async function main() {
  try {
    const cfg = await (await fetch("/api/config")).json();
    $("#test-banner").hidden = cfg.liveCharges;
  } catch { $("#test-banner").hidden = false; }

  if (!orderId || !token) {
    setStatus("danger", "הזמנה לא נמצאה", "הקישור אינו שלם.");
    setActions(["/", "חזרה לדף הסבב", true]);
    return;
  }

  const startedAt = Date.now();
  for (;;) {
    let order;
    try {
      order = await fetchOrder();
    } catch {
      setStatus("danger", "הזמנה לא נמצאה", "לא הצלחנו לטעון את ההזמנה.");
      setActions(["/", "חזרה לדף הסבב", true]);
      return;
    }
    renderSummary(order);
    const test = order.paymentMode === "mock";

    if (order.status === "paid") {
      renderVoucher(order);
      createCartStore().clear();
      attemptStore.reset();
      setStatus("success",
        test ? "תשלום לדוגמה אושר" : "התשלום התקבל",
        test
          ? `מצב בדיקה — לא בוצע חיוב ולא הופק מסמך. מספר הזמנה ${order.id}.`
          : `תודה. מספר הזמנה ${order.id}. אצור איתך קשר לתיאום המימוש.`);
      setActions(["/", "חזרה לדף הסבב", false]);
      return;
    }
    if (order.status === "cancelled" || order.status === "failed_to_start") {
      attemptStore.reset();
      setStatus("danger", "התשלום לא הושלם",
        "ההזמנה הזו לא שולמה. הסל נשמר, ואפשר לנסות שוב.");
      setActions(["/?cart=open", "חזרה לסל", true]);
      return;
    }
    if (order.status === "needs_review") {
      setStatus("", "ההזמנה בבדיקה",
        `התקבל עדכון מספק הסליקה שדורש בדיקה ידנית. אין צורך לשלם שוב. מספר הזמנה ${order.id}.`);
      setActions(["/", "חזרה לדף הסבב", false]);
      return;
    }
    // awaiting_payment
    if (Date.now() - startedAt > 120000) {
      setStatus("", "עדיין לא התקבל אישור תשלום",
        `אם השלמת תשלום, אין לשלם שוב — האישור יכול להגיע באיחור. מספר הזמנה ${order.id}.`);
      setActions([location.href, "בדיקה חוזרת", false], ["/?cart=open", "חזרה לסל", false]);
      return;
    }
    setStatus("", "ממתינים לאישור התשלום", "האישור מגיע ישירות מספק הסליקה. הדף יתעדכן לבד.");
    await new Promise((ok) => setTimeout(ok, 3000));
  }
}

main();
