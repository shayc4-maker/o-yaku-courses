# משתלת אויאקו — דף סבב ההקמה וסל רכישה

דף נחיתה בעברית, סל רכישה ותשתית תשלום, כ־Cloudflare Worker נפרד (`oyaku-founders-nursery`).
הוא אינו קשור לפרויקטים הקיימים בחשבון ואינו משנה אותם.

**מצב נוכחי:** הדף והסל עובדים ונבדקו מקומית. התשלום במצב בדיקה (`PAYMENT_MODE=mock`): דף תשלום
לדוגמה, ללא חיוב. החיבור ל־Morning כתוב אבל **לא אומת** — ראו [docs/MORNING.md](docs/MORNING.md).
אין להשתמש באתר לגבייה לפני שהבדיקה שם הושלמה.

## מבנה

```
public/            הדף (HTML/CSS/JS בלי build), נכסי המותג, פונטים מקומיים
  catalog.js       קטלוג ומחירים — מקור אחד לדפדפן ולשרת
  cart-store.js    סל ב־localStorage, מפתח idempotency לכל ניסיון תשלום
  app.js           מוצרים, סל, טופס, מעבר לתשלום
  order.html/.js   מצב הזמנה אחרי החזרה מהתשלום
src/
  worker.js        API: /api/checkout, /api/orders/:id, /api/morning/notify, /pay/return, /pay/mock
  orders.js        D1 — הזמנות, שורות, אירועי תשלום
  payments/morning.js  מתאם Morning (לא מאומת)
migrations/        סכמת D1
test/              בדיקות יחידה, API, דפדפן, וזרימת Morning מול שרת מדומה
docs/              MORNING.md, LAUNCH-CHECKLIST.md
```

## הרצה מקומית

```bash
cd founders-nursery
npm install
cp .dev.vars.example .dev.vars        # ולשים מחרוזת אקראית ב־NOTIFY_SIGNING_SECRET
npm run dev                           # http://localhost:8787
```

בדיקות (השרת המקומי צריך לרוץ עבור api/browser):

```bash
npm test                    # קטלוג, מחירים, ולידציה
npm run test:api            # API מול השרת המקומי
npm run test:browser        # דפדפן: מובייל/דסקטופ, סל, רענון, תשלום מדומה. צילומים ב־test-results/
npm run test:morning-flow   # הלוגיקה של נתיב Morning מול שרת Morning מדומה (מריץ Worker משלו)
```

## משתני סביבה

| שם | סוג | תיאור |
|---|---|---|
| `PAYMENT_MODE` | var | `mock` (ברירת מחדל) · `morning_sandbox` · `morning_live` |
| `ALLOW_LIVE_PAYMENTS` | var | חייב להיות `yes` כדי ש־`morning_live` יפעל |
| `PUBLIC_BASE_URL` | var | הכתובת הציבורית של האתר, לכתובות החזרה וה־notify |
| `ROUND_OPENS_AT` | var | מועד פתיחה ב־ISO, למשל `2026-11-01T08:00:00+02:00`. ריק = אין תאריכים, אין ספירה ואין חסימה. כשמוגדר: תאריכים וימים שנותרו מוצגים, והשרת חוסם רכישה לפני הפתיחה ואחרי 14 יום |
| `MORNING_API_BASE` / `MORNING_AUTH_BASE` | var | כתובות Morning — ראו docs/MORNING.md |
| `MORNING_AUTH_FLOW` | var | `legacy` או `oauth` — לקבוע אחרי בדיקת Sandbox |
| `MORNING_SEND_INCOME_LINES`, `MORNING_INCOME_VAT_TYPE` | var | אופן שליחת שורות הסל ל־Morning |
| `MORNING_PLUGIN_ID`, `MORNING_GROUP` | var | אם Morning דורשים |
| `NOTIFY_SIGNING_SECRET` | **secret** | חותם את כתובת ה־notify לכל הזמנה |
| `MORNING_API_KEY_ID`, `MORNING_API_KEY_SECRET` | **secret** | מפתח ה־API של Morning |

## פריסה ב־Cloudflare (רק אחרי אישור)

הפרויקט מוגדר עם `workers_dev: false`: גם אם יפורסם, אין לו כתובת ציבורית עד שמשנים את ההגדרה.

```bash
npx wrangler login
npx wrangler d1 create oyaku-founders-orders          # להעתיק את database_id ל־wrangler.jsonc
npx wrangler d1 migrations apply oyaku-founders-orders --remote
npx wrangler secret put NOTIFY_SIGNING_SECRET
npx wrangler secret put MORNING_API_KEY_ID             # כשיהיה
npx wrangler secret put MORNING_API_KEY_SECRET         # כשיהיה
npx wrangler deploy                                    # יוצר Worker חדש בשם oyaku-founders-nursery
```

בהשקה: `workers_dev: true` (כתובת `*.workers.dev`) או Custom Domain, ועדכון `PUBLIC_BASE_URL`.
הגדרות התשלום עוברות ל־live רק אחרי בדיקת ה־Sandbox.

מעקב הזמנות: `npx wrangler d1 execute oyaku-founders-orders --remote --command "SELECT id,status,total_agorot,customer_name,created_at FROM orders ORDER BY created_at DESC"`.

## פרטיות וגישה

- `noindex` בתגית meta ובכותרת `X-Robots-Tag` בכל תגובה. אין כלי מעקב, אנליטיקה או פיקסלים. הפונטים מוגשים מהאתר עצמו.
- **noindex אינו הגנת גישה.** כל מי שיש לו את הקישור יכול להיכנס. אם צריך הגנה, האפשרות הפשוטה היא Cloudflare Access (קוד חד־פעמי למייל לרשימה מוגדרת), אבל היא מחייבת לאסוף מראש מיילים של חברי הקבוצה. לא הופעלה.
- פרטי אשראי לא נאספים באתר. התשלום מתבצע בעמוד של הספק.

## הערות

- ההדמיה המקורית (תיקייה מקומית ו־`chatgpt.site`) לא הייתה נגישה מסביבת העבודה. הדף נבנה לפי הפרומפט וחבילת העיצוב.
- תמונת הפתיחה (`assets/atmosphere-juniper.jpg`) לקוחה מחבילת העיצוב ומסומנת באתר „תמונת אווירה”. יש לוודא זכויות שימוש או להחליף בתמונה מההדמיה.
- סטיות מכוונות מחבילת העיצוב, לשם ניגודיות AA: כפתור ראשי ב־clay‑600, וטקסט משני ב־stone‑600. בתוויות עבריות ריווח האותיות מצומצם.
