# אזור הניהול — הגדרה, הרשאות והעלאה

**מצב:** קוד ובדיקות מקומיות הושלמו. **לא הועלה**, לא הוגדר Access בחשבון, ולא הוחלו מיגרציות על מסד הייצור.
כל עוד חסרים `ACCESS_TEAM_DOMAIN`, `ACCESS_AUD` או `ADMIN_EMAILS`, כל נתיבי הניהול מחזירים 503 (חסום). אין ברירת מחדל פתוחה ואין מתג עוקף.

## מה נבנה

| | |
|---|---|
| ממשק | `/admin`: סיכום, הזמנות, קונים, מוצרים, יצוא. עברית, RTL, עובד בטלפון |
| API | `/api/admin/*` (פירוט למטה) |
| הרשאה | Cloudflare Access ובנוסף אימות JWT בצד השרת (`src/admin/access.js`) |
| קבצי ממשק | `admin-ui/*` נארזים לתוך ה־Worker כטקסט ואינם ב־`public/`, כך ששכבת הנכסים הסטטיים לא יכולה להגיש אותם בלי אימות |
| מסד | מיגרציה `0003_admin.sql` (פירוט למטה) |

### נתיבי API (כולם דורשים אימות)

| שיטה | נתיב | |
|---|---|---|
| GET | `/api/admin/me` | המשתמש המחובר |
| GET | `/api/admin/summary?scope=live\|test` | הכנסות, הזמנות ששולמו, קונים, מצבי שוברים |
| GET | `/api/admin/orders?q&product&payment&redemption&from&to&sort&dir&page&pageSize&scope` | סינון, מיון ודפדוף בצד השרת |
| GET | `/api/admin/orders/:id` | פירוט מלא: שורות מהצילום שנשמר בהזמנה, יתרות, מימושים, תיאומים, היסטוריה |
| GET | `/api/admin/buyers?q&page&scope` · `/api/admin/buyers/:id` | קונים וכרטיס קונה |
| GET | `/api/admin/products?scope` | תשעת המוצרים: נמכר, מומש, יתרה |
| GET | `/api/admin/export/{buyers,orders,balances}.csv?scope` | יצוא |
| POST | `/api/admin/orders/:id/redemptions` | מימוש (`idempotencyKey`, `productId`, `quantity`, `date`, `note`) |
| POST | `/api/admin/redemptions/:id/corrections` | תיקון מימוש (`idempotencyKey`, `quantity`, `reason`) |
| POST | `/api/admin/orders/:id/cancel-voucher` | ביטול שובר: חוסם מימוש בלבד (`reason`, `confirm: true`) |
| POST | `/api/admin/orders/:id/notes` | תיאום/הערה (`kind`, `productId?`, `value`) |

**אין** נתיב לסימון הזמנה כשולמה או להפקת שובר ידנית. הזמנה הופכת ל־`paid` רק דרך אימות התשלום הקיים (Morning או הדמיה במצב mock).

## אבטחה — מה נבדק

- **JWT:** חתימת RS256 מול המפתחות ב־`<team>/cdn-cgi/access/certs`, `iss` שווה לכתובת ה־Team, `aud` כולל את ה־AUD, תוקף `exp`/`nbf` (סטייה של 60 שניות), ו־`email` שמופיע ב־`ADMIN_EMAILS`. הטוקן נקרא מהכותרת `Cf-Access-Jwt-Assertion` או מהעוגייה `CF_Authorization`. כותרת אימייל לבדה, או טוקן לא חתום, נדחים.
- **סדר:** האימות רץ לפני כל קריאה או כתיבה למסד, בכל נתיב ניהול ובכל שיטה, כולל יצוא וקבצי הממשק.
- **CSRF:** כתיבה רק ב־POST עם `Content-Type: application/json`, ‏`Origin` זהה למקור האתר, ‏`Sec-Fetch-Site: same-origin` (כשקיים) וכותרת `X-OY-Admin: 1`.
- **no-store** בכל תגובות הניהול, ו־noindex כמו בשאר האתר.
- **לוגים:** רק קוד הסיבה לדחייה. לא נרשמים טוקן, אימייל או פרטי לקוח.
- **סביבת בדיקה:** כתובת Team מקומית (`http://127.0.0.1:<port>`) ו־`TEST_NOW` מתקבלות רק כשהבקשה עצמה מגיעה לכתובת loopback. מאחורי נתיב הייצור הן נדחות או מתעלמים מהן. המפתח לבדיקות נוצר בזיכרון בכל הרצה ואינו נשמר.
- **ניתוב:** `run_worker_first` כולל `/admin` ו־`/admin/*`. ‏`/api/*` כבר עובר דרך ה־Worker. גרסאות כמו `/Admin` או `/%61dmin` לא מגיעות לתוכן ניהול.

**לא נבדק:** התנהגות מול Cloudflare Access אמיתי בחשבון. נבדקו רק טוקנים שנחתמו מקומית במבנה של Access. בדיקה אחרי ההגדרה מופיעה בסוף המסמך.

## מסד נתונים — מיגרציה 0003

`migrations/0003_admin.sql` מוסיפה בלבד. לא מוחקת ולא משנה נתונים קיימים, מלבד מילוי השדות החדשים.

| שינוי | פירוט |
|---|---|
| טבלה `buyers` | קונה לכל אימייל מנורמל (trim + lowercase בלבד). שם וטלפון מההזמנה הראשונה. אין איחוד לפי שם או טלפון |
| `orders.buyer_id` | קישור יציב לקונה, ממולא לכל ההזמנות הקיימות. פרטי הלקוח המקוריים נשארים על ההזמנה |
| `order_items.redeem_units`, `redeem_unit_label` | צילום יחידות המימוש לכל שורה. אקדמה: חבילה = 10 שקים |
| `orders.voucher_cancelled_at/_by/_cancel_reason` | ביטול שובר. מצב התשלום אינו משתנה |
| טבלה `redemptions` | יומן מימושים שרק מתווספים אליו. תיקון הוא שורה חדשה עם כמות שלילית, מקושרת (`corrects_id`) ועם סיבה. `idempotency_key` ייחודי |
| טבלה `order_notes` | תיאומים והערות פנימיות (מועד, מידה, איסוף, משלוח, פרטי כלי, הכנסת עצים, סיום שנת שירות) |
| טבלה `admin_activity` | פעולות נוספות, כרגע ביטול שובר: מי, מתי, סיבה |

אי־התאמות מוצגות בכרטיס הקונה ב„לבדיקה ידנית”: שמות או טלפונים שונים תחת אותו אימייל, ואותו טלפון אצל קונים אחרים. דבר לא מאוחד אוטומטית.

## כללי מימוש

- מימוש רק בהזמנה ששולמה, בשובר שלא בוטל ושתוקפו לא פג, החל מ־1.1.2027 (שעון ישראל). תאריך המימוש אינו בעתיד ואינו אחרי תום התוקף.
- **אטומיות:** בדיקת היתרה והכתיבה הן משפט SQL אחד (`INSERT … SELECT … WHERE יתרה >= כמות`). D1 מריץ משפטים בזה אחר זה, כך ששתי בקשות מקבילות לא יכולות לעבור יחד את היתרה. נבדק: 2×15 על 20 שקים, ו־12×1 על 5.
- **Idempotency:** לכל טופס מפתח משלו. שליחה חוזרת עם אותו מפתח מחזירה את אותה רשומה. אותו מפתח עם תוכן אחר מחזיר 409.
- **יחידות:** אקדמה בשקים, ושאר המוצרים ביחידת המכירה. מספרים שלמים בלבד.
- **ביטול שובר** אינו החזר כספי. הממשק מבהיר זאת ודורש סיבה ואישור. החזר מתבצע מול ספק הסליקה ואינו נרשם כאן.
- **דף השובר הציבורי** (`/order`) מציג יתרה ומצב לכל שורה, בלי הערות, בלי זהות מנהל ובלי סיבות. אחרי ביטול או פקיעה היתרה המוצגת היא 0.

## מכירות אמיתיות לעומת בדיקה

ברירת המחדל בכל מסך ויצוא היא `scope=live`: רק `payment_mode = morning_live`. הכנסות, קונים וכמויות נספרים רק מהזמנות `paid`. בקשות שלא הושלמו מוצגות בנפרד כ„בקשות שאינן מכירות”.
המתג „מצב בדיקה” מציג רק הזמנות `mock` ו־`morning_sandbox`, עם פס אזהרה ותג בכל שורה. ביצוא יש עמודת „סביבה”, ושם הקובץ מסומן `TEST`.

## יצוא CSV

UTF‑8 עם BOM. תאים שמתחילים ב־`= + - @` מקבלים גרש בהתחלה, כדי שאקסל לא יפעיל אותם כנוסחה. אין בקבצים טוקני גישה, קישורי לקוח או הודעות סליקה גולמיות.

---

## הגדרה בחשבון Cloudflare (לביצוע אחרי אישור)

### מה חסר ממך

| פרט | איפה |
|---|---|
| **מייל הבעלים** (`ADMIN_EMAILS`) | המייל שאיתו תתחבר. אפשר כמה, מופרדים בפסיק |
| **Team Domain** (`ACCESS_TEAM_DOMAIN`) | Zero Trust ← Settings ← Custom Pages / Team domain, בצורה `https://<team>.cloudflareaccess.com` |
| **Application Audience (AUD) Tag** (`ACCESS_AUD`) | נוצר אחרי הקמת האפליקציה ב־Access ← Overview |

אלה אינם סודות. הם נכנסים כ־`vars` ב־`wrangler.jsonc`. אין להדביק אותם או שום מפתח בצ'אט.

### צעדים

1. **Zero Trust ← Access ← Applications ← Add ← Self-hosted.**
   - Application domain: `nursery.o-yaku.com`, נתיב `admin`.
   - Add domain נוסף באותה אפליקציה: `nursery.o-yaku.com`, נתיב `api/admin`.
   - Session duration: לבחירתך (מומלץ 24 שעות או פחות).
2. **Policy:** Action `Allow`, Include ← Emails ← מייל הבעלים בלבד. Login method: One-time PIN או ספק זהות קיים.
3. **לא** להוסיף לאפליקציה את `/`, ‏`/api/checkout`, ‏`/api/orders/*`, ‏`/pay/*` או `/api/morning/notify`. האתר הציבורי והודעות Morning צריכים להישאר נגישים.
4. להעתיק את ה־AUD Tag ולמלא ב־`wrangler.jsonc`:
   ```jsonc
   "ACCESS_TEAM_DOMAIN": "https://<team>.cloudflareaccess.com",
   "ACCESS_AUD": "<aud tag>",
   "ADMIN_EMAILS": "<owner email>"
   ```

### העלאה (רק בהוראה מפורשת)

הסדר חשוב: הקוד החדש של הקופה כותב ל־`buyers` ול־`redeem_units`, ולכן המיגרציה חייבת לרוץ לפני העלאת הקוד.

```bash
# 1. גיבוי
npx wrangler d1 export oyaku-founders-orders --remote --output backup-before-0003.sql
# 2. מיגרציה
npx wrangler d1 migrations apply oyaku-founders-orders --remote      # מחיל 0003 בלבד
# 3. העלאה
npx wrangler deploy
# 4. מילוי הזמנות שנוצרו בין שלב 2 ל־3 (אפשר להריץ שוב בלי נזק)
npx wrangler d1 execute oyaku-founders-orders --remote --file scripts/backfill-admin.sql
```

### בדיקה אחרי העלאה

- [ ] `/admin` בלי התחברות מפנה למסך ההתחברות של Access.
- [ ] `curl -i https://nursery.o-yaku.com/api/admin/me` (בלי עוגייה) מחזיר הפניה של Access או 401, לא נתונים.
- [ ] כניסה עם מייל הבעלים מציגה את הסיכום. מייל אחר נחסם ב־Access.
- [ ] האתר הציבורי, הקופה והשובר עובדים כרגיל. `/api/morning/notify` לא חסום ב־Access.
- [ ] יצוא CSV נפתח באקסל עם עברית תקינה.

## בדיקות מקומיות

```bash
npm test                     # יחידה: Access, CSRF, CSV, יחידות מימוש, קטלוג, תוקף
npm run test:admin           # API: הרשאות, חיפוש ודפדוף, מימוש ומקביליות, תיקון, ביטול, live/test, יצוא; חסימה בלי הגדרות; שעון אמיתי
npm run test:admin-browser   # דפדפן, מחשב וטלפון; צילומים ב־test-results/admin-*.png
# בדיקות קיימות (דורשות `npm run dev` עם PUBLIC_BASE_URL=http://127.0.0.1:8787 ב־.dev.vars):
npm run test:api && npm run test:browser && npm run test:morning-flow
```

בדיקות הניהול מריצות Worker פרטי משלהן, עם מסד D1 מקומי זמני ונתונים פיקטיביים, ומוחקות אותו בסיום.

## מחוץ להיקף הגרסה הזאת

- עקיפת כללי מימוש באישור בעלים (לא נדרש). אם תידרש, תהיה פעולה נפרדת עם סיבה והיסטוריה.
- החזרים כספיים, ושליחת הודעות ללקוחות.
- איחוד קונים ידני מתוך הממשק. כרגע מוצגות רק אי־התאמות.
- עורך קטלוג. תוכן ההזמנות נשמר כצילום, כך ששינוי עתידי בקטלוג לא ישנה הזמנות קודמות.
