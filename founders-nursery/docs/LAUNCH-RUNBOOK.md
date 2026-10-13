# מסלול השקה — מהמצב הנוכחי לגבייה

מסמך אחד, לפי הסדר. מחליף את הרשימה הכללית ב־[LAUNCH-CHECKLIST.md](LAUNCH-CHECKLIST.md) (שם נשארים פרטי התוכן).
**אין לעבור לשלב הבא לפני שהקודם הושלם.** השלבים המסומנים 🔒 משנים משהו בחשבון האמיתי ודורשים אישור מפורש שלך ברגע הביצוע.

| מצב נוכחי | |
|---|---|
| קוד, בדיקות מקומיות, אזור ניהול | הושלם. כל הבדיקות עוברות |
| בדיקת תשלום מול Sandbox של Morning | **לא בוצעה** |
| Cloudflare Access ואזור הניהול | **לא הוגדר** (חסום) |
| מיגרציה 0003 על המסד האמיתי | **לא הוחלה** |
| סליקה חיה | **כבויה** (`mock`, `ALLOW_LIVE_PAYMENTS=no`) |

## שלב 1 — בדיקת Sandbox (לא נוגע בכסף אמיתי)

מבצעים לפי [SANDBOX-TEST.md](SANDBOX-TEST.md). מסיימים כשסעיפים 1–11 בטבלה עברו.

- [ ] חשבון Sandbox, מפתח API, תוסף סליקה
- [ ] `node scripts/sandbox-verify.mjs form` ו־`confirm` — הכול PASS
- [ ] מקרה כשל (מעל ₪5,000), ביטול, חזרה בלי תשלום
- [ ] מסלול מלא מהאתר, כולל התראה אמיתית ובדיקת כפילות
- [ ] המסמך שהופק נראה נכון (שם, שורות, מע״מ, סכום)
- [ ] הבדלים מהתיעוד נרשמו בטבלה ותוקנו בהגדרות

## שלב 2 — תוכן שחייב להיות סופי

מתוך [LAUNCH-CHECKLIST.md](LAUNCH-CHECKLIST.md), ורק אתה יכול להשלים:
- [ ] מועד פתיחת הסבב (`ROUND_OPENS_AT`). בלעדיו אין ספירה והשרת לא חוסם רכישה לפני הפתיחה או אחרי 14 יום
- [ ] פרטי עסק ותנאי ביטול מאושרים (בדוק מול ייעוץ משפטי, בעיקר זכות ביטול עסקה מרחוק)
- [ ] מחירים ומגבלות מידות סופיים
- [ ] אישור נוסח ההודעות בדף ההזמנה והשובר

## שלב 3 — Cloudflare Access (אזור הניהול) 🔒

לפי [ADMIN.md](ADMIN.md), סעיף „הגדרה בחשבון Cloudflare”.

- [ ] אפליקציית Access ל־`nursery.o-yaku.com/admin` ול־`nursery.o-yaku.com/api/admin`, מדיניות Allow למייל הבעלים בלבד
- [ ] ערכי `ACCESS_TEAM_DOMAIN`, `ACCESS_AUD`, `ADMIN_EMAILS` ב־`wrangler.jsonc`
- [ ] האפליקציה **לא** מכסה את `/`, `/api/checkout`, `/api/orders/*`, `/pay/*`, `/api/morning/notify`

## שלב 4 — העלאה במצב בדיקה 🔒

עדיין `PAYMENT_MODE=mock`. הסדר חשוב.

```bash
npx wrangler d1 export oyaku-founders-orders --remote --output backup-before-0003.sql
npx wrangler d1 migrations apply oyaku-founders-orders --remote      # מחיל 0003 בלבד
npx wrangler deploy
npx wrangler d1 execute oyaku-founders-orders --remote --file scripts/backfill-admin.sql
```

- [ ] האתר הציבורי, הסל והשובר עובדים כרגיל
- [ ] `/admin` בלי התחברות מפנה ל־Access. עם המייל שלך נפתח
- [ ] `/api/admin/me` בלי עוגייה לא מחזיר נתונים
- [ ] `/api/morning/notify` אינו חסום ב־Access
- [ ] יצוא CSV נפתח באקסל עם עברית תקינה

## שלב 5 — סליקה חיה 🔒

רק אחרי שלבים 1–4.

```bash
npx wrangler secret put MORNING_API_KEY_ID          # מפתחות Production; לא בצ'אט
npx wrangler secret put MORNING_API_KEY_SECRET
npx wrangler secret put NOTIFY_SIGNING_SECRET       # אם עדיין לא הוגדר בפריסה
```

ב־`wrangler.jsonc`: `PAYMENT_MODE=morning_live`, `ALLOW_LIVE_PAYMENTS=yes`, `MORNING_API_BASE=https://api.greeninvoice.co.il/api/v1`, `MORNING_AUTH_BASE=https://api.morning.co`, `PUBLIC_BASE_URL=https://nursery.o-yaku.com`. אחר כך `npx wrangler deploy`.

- [ ] **עסקה אמיתית אחת בסכום נמוך, שאתה מבצע בעצמך** (למשל חולצה אחת)
- [ ] ההזמנה עברה ל־`paid` ושובר מוצג, **בלי** סימון „לדוגמה”
- [ ] המסמך ב־Morning תקין, והסכום זהה
- [ ] באזור הניהול ההזמנה נספרת ב„מכירות אמיתיות”
- [ ] החזר של העסקה הזו מתבצע מול Morning (ביטול שובר באתר חוסם מימוש בלבד ואינו מחזיר כסף)

## שלב 6 — הפצה

- [ ] להחליט אם נדרשת הגנת גישה על הקישור (`noindex` אינו הגנה)
- [ ] בדיקה אחרונה בטלפון ובמחשב
- [ ] פרסום הקישור לקבוצה

## חזרה אחורה

- **להפסיק גבייה מיד:** `ALLOW_LIVE_PAYMENTS=no` ו־`npx wrangler deploy`. עם `morning_live` הקופה מחזירה שגיאה ולא פותחת עמוד תשלום; הזמנות קיימות ושוברים נשארים. (מעבר ל־`mock` פותח דף תשלום לדוגמה לכל מבקר, ולכן לא מומלץ באתר שהקישור שלו כבר הופץ.)
- **המיגרציה:** תוספתית בלבד; חזרה אחורה אינה נדרשת. הגיבוי בשלב 4 קיים למקרה חירום.
