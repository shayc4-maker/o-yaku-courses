export const TERMS_VERSION = "2026-10-07-v1";

export const REDEMPTION = {
  "tshirt": "מימוש החל מינואר 2027 ועד תום תוקף השובר. מידות ואופן המסירה יתואמו בטלפון.",
  "ceramics-group": "מימוש החל מינואר 2027 ועד תום תוקף השובר, בתיאום מראש. המחיר הוא למשתתף בקבוצה של ארבעה.",
  "ceramics-private": "מימוש החל מינואר 2027 ועד תום תוקף השובר, בתיאום מראש.",
  "bonsai-private-lesson": "מימוש החל מינואר 2027 ועד תום תוקף השובר, בתיאום מראש. שיעור פרטי במשתלה, 3 שעות.",
  "bonsai-wiring-workshop": "מימוש החל מינואר 2027 ועד תום תוקף השובר, בתיאום מראש. 4 שעות, עד ארבעה בקבוצה. המחיר למשתתף.",
  "pine-grafting-workshop": "מימוש החל מינואר 2027 ועד תום תוקף השובר, בתיאום מראש. עד ארבעה בקבוצה. המחיר למשתתף וכולל זריע שעליו מורכב אורן סנג׳ומארו.",
  "akadama-10": "מימוש החל מינואר 2027 ועד תום תוקף השובר, באיסוף בתיאום מראש. משלוח יתואם בטלפון; עלותו ומועדו יימסרו לפני אישורו.",
  "custom-pot": "מימוש החל מינואר 2027 ועד תום תוקף השובר. מידות, עיצוב ומועד אספקה יתואמו מראש.",
  "live-test": "מוצר בדיקה לסליקה בלבד. אין בו מימוש.",
  "nursery-sqm-year": "מימוש החל מינואר 2027 ועד תום תוקף השובר, בתיאום מראש. שנת השירות מתחילה עם הכנסת העצים.",
};

// Calendar years, with February 29 clamped to February 28 in a non-leap year.
export function voucherExpiry(issuedAt) {
  const date = new Date(issuedAt);
  const month = date.getUTCMonth();
  date.setUTCFullYear(date.getUTCFullYear() + 2);
  if (date.getUTCMonth() !== month) date.setUTCDate(0);
  return date.toISOString();
}
