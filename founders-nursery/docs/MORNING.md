# Morning (חשבונית ירוקה) — בדיקת החיבור

נבדק ב־7.10.2026. **החיבור לא נבדק מול חשבון אמיתי או חשבון Sandbox.** התיעוד הרשמי
(`greeninvoice.docs.apiary.io`, `greeninvoice.co.il/help-center`) היה חסום מסביבת העבודה.
המידע נאסף מתקצירי חיפוש של העמודים הרשמיים ומאינטגרציות של צד שלישי. לכן הטבלה מפרידה
בין מה שאומת לבין מה שעדיין הנחה.

## מה ידוע ומאיזה מקור

| נושא | מה נמצא | רמת ודאות | מקור |
|---|---|---|---|
| מסלול נדרש ל־API | ממשק API זמין למנויי **Best** ומעלה | גבוהה — עמוד עזרה רשמי (תקציר) | [ממשק ה־API שלנו](https://www.greeninvoice.co.il/help-center/api/) |
| יצירת מפתח API | אזור אישי ← כלים למפתחים ← מפתחות API. הסוד מוצג פעם אחת בלבד | גבוהה — עמוד עזרה רשמי (תקציר) | [יצירת מפתח API](https://www.greeninvoice.co.il/help-center/generating-api-key/) |
| סביבת בדיקה | נרשמים ל־Sandbox, מקימים עסק פיקטיבי, „רוכשים” Best לבדיקה ויוצרים מפתח. עסקאות מעל 5,000 ₪ נכשלות בכוונה (סימולציה) | בינונית־גבוהה — תקציר חיפוש | [יצירת מפתח API](https://www.greeninvoice.co.il/support/api/%D7%99%D7%A6%D7%99%D7%A8%D7%AA-%D7%9E%D7%A4%D7%AA%D7%97%D7%95%D7%AA-api) |
| כתובות בסיס | Production: `https://api.greeninvoice.co.il/api/v1` · Sandbox: `https://sandbox.d.greeninvoice.co.il/api/v1` | בינונית — מתועד באינטגרציות צד שלישי | [GreenInvoice‑MCP](https://github.com/danielrosehill/GreenInvoice-MCP) |
| עמוד תשלום דינמי | `POST /payments/form` מחזיר כתובת לעמוד תשלום מאובטח. אחרי תשלום מופק מסמך אוטומטית | בינונית — תקציר של Apiary ואינטגרציות | [Apiary](https://jsapi.apiary.io/apis/greeninvoice.html), [PR של צד שלישי](https://github.com/tomerytz-del/ShukNadlan/pull/290) |
| שדות הבקשה | `description, type, lang, currency, vatType, amount, maxPayments, client, income[], remarks, successUrl, failureUrl, notifyUrl, custom, pluginId, group` | **נמוכה — הנחה**. לא נבדק מול התיעוד המלא | כנ״ל |
| סל עם כמה פריטים | `income[]` עם `description, quantity, price, vatType` לכל שורה | **נמוכה**. דיווח של צד שלישי טוען ש־`price` ב־`income` הוא לפני מע״מ, ושמשמעות `vatType` שונה ממה שנהוג לחשוב | [PR של צד שלישי](https://github.com/tomerytz-del/ShukNadlan/pull/290) |
| חזרה מהתשלום | `successUrl` / `failureUrl`. נוסף להם `&response=success` | בינונית | תקציר Apiary |
| התראה לשרת | `notifyUrl` לכל עמוד תשלום. בנוסף יש Webhooks שמוגדרים בממשק (`payment/received`, `document/created`) עם „מפתח סודי” | בינונית־גבוהה (Webhooks — עמוד רשמי). מבנה הגוף ושיטת החתימה **לא ידועים** | [הגדרת Webhooks](https://www.greeninvoice.co.il/help-center/creating-webhook/), [document/created](https://www.greeninvoice.co.il/help-center/webhook-document-created/) |
| אימות | `POST /account/token` עם `id` + `secret` ← JWT. דיווח של צד שלישי מיוני 2026 טוען למעבר ל־OAuth 2.0 (`/idp/v1/oauth/token` ב־`api.morning.co`) | **לא ודאי** — שני המקורות סותרים | [PR של צד שלישי](https://github.com/tomerytz-del/ShukNadlan/pull/290) |
| הפעלת סליקה | ייתכן ש־plugin הסליקה דורש אישור „מסחר אלקטרוני” נפרד מול חברת הסליקה | נמוכה | [PR של צד שלישי](https://github.com/tomerytz-del/ShukNadlan/pull/290), [חיבור לתשלומים דיגיטליים](https://www.greeninvoice.co.il/help-center/digital-payments-connect/) |

## איך הקוד נזהר מההנחות

- `PAYMENT_MODE=mock` הוא ברירת המחדל. במצב הזה אין פנייה ל־Morning, ודף התשלום הוא דף לדוגמה שמסומן ככזה.
- `morning_live` לא פועל בלי `ALLOW_LIVE_PAYMENTS=yes`.
- כתובות הבסיס, זרימת האימות (`MORNING_AUTH_FLOW`), שליחת שורות (`MORNING_SEND_INCOME_LINES`) ו־`vatType` לשורה הם הגדרות. אם משהו מתברר כשגוי ב־Sandbox, מתקנים בלי לשנות קוד.
- הזמנה מסומנת `paid` רק אחרי שהשרת קורא את המסמך בחזרה מ־Morning (`GET /documents/{id}`) עם המפתח שלנו, ובודק שהמסמך מפנה למספר ההזמנה ושהסכום זהה. גוף ההתראה לבדו אינו הוכחה.
- כל התראה נשמרת פעם אחת (`payment_events.event_key` ייחודי). התראה חוזרת לא משנה דבר.
- כל דבר שלא מצליח להתאמת אוטומטית מסומן `needs_review` להתאמה ידנית. הוא אף פעם לא מסומן `paid` בלי אימות.
- כתובת ה־`notifyUrl` נושאת HMAC של מספר ההזמנה (`NOTIFY_SIGNING_SECRET`), כך שרק השרת יכול לייצר אותה.

## בדיקה ב־Sandbox — לפני כל גבייה

1. פתיחת חשבון Sandbox (`app.sandbox.d.greeninvoice.co.il`), עסק פיקטיבי, מסלול Best לבדיקה, מפתח API.
2. ב־`.dev.vars`: `PAYMENT_MODE=morning_sandbox`, `MORNING_API_BASE=https://sandbox.d.greeninvoice.co.il/api/v1`, המפתח והסוד.
3. חשיפת השרת המקומי בכתובת ציבורית (למשל `cloudflared tunnel --url http://localhost:8787`) והגדרתה ב־`PUBLIC_BASE_URL`, כדי ש־Morning יוכל לשלוח את ה־notify.
4. לבדוק ולתעד:
   - [ ] איזו זרימת אימות עובדת: `legacy` או `oauth`.
   - [ ] `POST /payments/form` מחזיר `url`, ונפתח עמוד תשלום של Morning.
   - [ ] **הסכום שמוצג בעמוד התשלום שווה בדיוק לסכום הסל.** אם לא, לשנות את `MORNING_INCOME_VAT_TYPE`, או לכבות את `MORNING_SEND_INCOME_LINES`.
   - [ ] המסמך שמופק: סוג (`type`), שורות, כמויות, מע״מ, שם לקוח ואימייל.
   - [ ] ה־notify מגיע: לתעד את גוף הבקשה (נשמר ב־`payment_events.payload`) ולוודא ש־`extractDocumentId` מוצא את מזהה המסמך.
   - [ ] `GET /documents/{id}` מחזיר `amount`, ‏`currency`, ‏`remarks` כמצופה. ההזמנה עוברת ל־`paid`.
   - [ ] ביטול בעמוד התשלום מחזיר ל־`failureUrl`, וההזמנה עוברת ל־`cancelled`.
   - [ ] כרטיס שנדחה (סכום מעל 5,000 ₪ ב־Sandbox): אין מסמך, וההזמנה לא מסומנת `paid`.
   - [ ] notify כפול: המסמך לא מופק פעמיים וההזמנה לא משתנה.
5. רק אחרי שכל הסעיפים עברו: מפתח Production, `PAYMENT_MODE=morning_live`, ‏`ALLOW_LIVE_PAYMENTS=yes`, ועסקה אמיתית אחת בסכום נמוך — באישורך.

## מה דרוש ממך

- אישור שמסלול ה־Best פעיל וכולל API. אם יש ספק, לשאול את Morning.
- אישור שהסליקה (plugin תשלומים / Morning Pay) פעילה בחשבון, כולל אישור „מסחר אלקטרוני” אם נדרש, ו־`pluginId`/‏`group` אם Morning מבקשים.
- סוג העסק (מורשה / פטור) וסוג המסמך הרצוי (חשבונית מס קבלה / קבלה).
- מפתח API ל־Sandbox. אחר כך מפתח ל־Production. **לא בצ'אט** — רק דרך `wrangler secret put`.
- אישור מ־Morning (או מהתיעוד המלא) על: שדות `income`, משמעות `vatType`, גוף ה־notify ושיטת החתימה של Webhooks.

## חלופות נתמכות אם אין גישת API

- **קישור תשלום קבוע לכל מוצר** מתוך ממשק Morning: בלי סל, תשלום נפרד לכל מוצר. תשלום חופשי על קישור קבוע אינו חיבור סל תקין.
- **הזמנה בלי תשלום מקוון**: הסל שולח בקשת הזמנה, ואתה שולח בקשת תשלום מ־Morning ידנית. דורש שינוי קטן בקוד (סטטוס `requested` במקום הפניה לתשלום).
- **WooCommerce / Shopify עם תוסף Morning הרשמי**: נתמך רשמית, אבל כבד בהרבה מהפרויקט הזה.
