// Morning (Green Invoice) adapter.
//
// STATUS: NOT VERIFIED AGAINST A LIVE OR SANDBOX ACCOUNT.
// Official docs (greeninvoice.docs.apiary.io, greeninvoice.co.il/help-center) could not be
// opened from the environment this was written in. Endpoint paths and field names below come
// from search excerpts of those official pages and from third-party integrations, and are
// listed as "to verify" in founders-nursery/docs/MORNING.md. Run the sandbox checklist in that
// file before switching PAYMENT_MODE away from "mock".
//
// Base URLs are not hard-coded here — they come from configuration (MORNING_API_BASE,
// MORNING_AUTH_BASE) so they can be corrected without a code change.

let cachedToken = null; // { value, expiresAtMs, cacheKey }

async function getAccessToken(env) {
  const cacheKey = `${env.MORNING_AUTH_FLOW}:${env.MORNING_API_KEY_ID}`;
  if (cachedToken && cachedToken.cacheKey === cacheKey && cachedToken.expiresAtMs - Date.now() > 60_000) {
    return cachedToken.value;
  }

  let res;
  if (env.MORNING_AUTH_FLOW === "oauth") {
    // Reported (third-party, 2026) OAuth 2.0 client-credentials flow. To verify.
    res = await fetch(`${env.MORNING_AUTH_BASE}/idp/v1/oauth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        grant_type: "client_credentials",
        client_id: env.MORNING_API_KEY_ID,
        client_secret: env.MORNING_API_KEY_SECRET,
      }),
    });
  } else {
    // Long-documented flow: POST /account/token with the API key id + secret. To verify.
    res = await fetch(`${env.MORNING_API_BASE}/account/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: env.MORNING_API_KEY_ID, secret: env.MORNING_API_KEY_SECRET }),
    });
  }
  const body = await res.json().catch(() => ({}));
  const value = body.accessToken || body.access_token || body.token;
  if (!res.ok || !value) {
    throw new Error(`morning_auth_failed: HTTP ${res.status}`);
  }
  const expiresAtMs = body.expiresAt
    ? Number(body.expiresAt) * 1000
    : body.expires_in
      ? Date.now() + Number(body.expires_in) * 1000
      : Date.now() + 20 * 60_000;
  cachedToken = { value, expiresAtMs, cacheKey };
  return value;
}

async function morningFetch(env, path, init = {}) {
  const token = await getAccessToken(env);
  return fetch(`${env.MORNING_API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}`, ...(init.headers || {}) },
  });
}

const agorotToShekels = (a) => Math.round(a) / 100;

// Requests a one-off hosted payment page for this exact order.
// The amount and every line come from the server-side priced order, never from the browser.
export async function createPaymentPage(env, order, urls) {
  const body = {
    description: `משתלת אויאקו — הזמנה ${order.id}`,
    type: 320, // receipt-invoice (חשבונית מס קבלה). To verify against the business's document settings.
    lang: "he",
    currency: order.currency,
    vatType: 0,
    amount: agorotToShekels(order.totalAgorot),
    maxPayments: 1,
    client: {
      name: order.customer.name,
      emails: [order.customer.email],
      phone: order.customer.phone,
    },
    remarks: `הזמנה ${order.id}`,
    successUrl: urls.successUrl,
    failureUrl: urls.failureUrl,
    notifyUrl: urls.notifyUrl,
    custom: order.id,
  };
  if (env.MORNING_SEND_INCOME_LINES !== "false") {
    // Per-line vatType for VAT-inclusive prices. The meaning of the values must be confirmed in
    // the sandbox: the charged total has to equal order.totalAgorot exactly.
    body.income = order.lines.map((l) => ({
      description: l.name,
      quantity: l.quantity,
      price: agorotToShekels(l.unitPriceAgorot),
      currency: order.currency,
      vatType: Number(env.MORNING_INCOME_VAT_TYPE ?? 1),
    }));
  }
  if (env.MORNING_PLUGIN_ID) body.pluginId = env.MORNING_PLUGIN_ID;
  if (env.MORNING_GROUP) body.group = Number(env.MORNING_GROUP);

  const res = await morningFetch(env, "/payments/form", { method: "POST", body: JSON.stringify(body) });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || !data.url) {
    throw new Error(`morning_form_failed: HTTP ${res.status} ${data.errorCode ?? ""} ${data.errorMessage ?? ""}`.trim());
  }
  return { paymentUrl: data.url };
}

// Pulls a candidate document id out of a notification payload. The payload shape is not verified,
// so this only looks in a few plausible places and returns null otherwise.
export function extractDocumentId(payload) {
  if (!payload || typeof payload !== "object") return null;
  const candidates = [payload.documentId, payload.document?.id, payload.data?.documentId, payload.data?.document?.id, payload.id];
  const found = candidates.find((v) => typeof v === "string" && /^[A-Za-z0-9-]{8,64}$/.test(v));
  return found ?? null;
}

// Confirms a payment by reading the document back from Morning's API with our own credentials.
// The notification body itself is never treated as proof. Returns { confirmed: true, ... } only
// when the document exists, references this order, and its amount/currency can be read.
export async function confirmPayment(env, orderId, payload) {
  const documentId = extractDocumentId(payload);
  if (!documentId) return { confirmed: false, reason: "no_document_id_in_notification" };

  const res = await morningFetch(env, `/documents/${encodeURIComponent(documentId)}`, { method: "GET" });
  if (!res.ok) return { confirmed: false, reason: `document_lookup_http_${res.status}` };
  const doc = await res.json().catch(() => null);
  if (!doc) return { confirmed: false, reason: "document_lookup_unreadable" };

  const references = [doc.remarks, doc.description, doc.custom].filter(Boolean).join(" ");
  if (!references.includes(orderId)) return { confirmed: false, reason: "document_does_not_reference_order" };
  if (typeof doc.amount !== "number") return { confirmed: false, reason: "document_amount_missing" };

  return {
    confirmed: true,
    amountAgorot: Math.round(doc.amount * 100),
    currency: doc.currency || null,
    documentId,
    transactionId: doc.payment?.[0]?.transactionId ?? null,
  };
}
