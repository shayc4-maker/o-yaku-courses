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
