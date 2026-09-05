/**
 * Seed articles/lessons/updates feed. Per the approved build scope, only Home, Knowledge Base
 * and Species are wired to the live database for now — this listing stays on curated seed data
 * (it mixes recorded-lesson teasers, paywall states, and update posts that don't map cleanly
 * onto the live `articles` table yet). The `species` field is a live species slug so links from
 * here into the Species page resolve against real data.
 */
export interface SeedArticle {
  id: string;
  kind: 'article' | 'lesson' | 'update';
  title: string;
  text: string;
  meta: string;
  species?: string;
  date: string;
  locked: boolean;
  body?: string[];
}

export const ARTICLE_KINDS: { id: string; label: string }[] = [
  { id: 'all', label: 'הכל' },
  { id: 'article', label: 'מאמרים' },
  { id: 'lesson', label: 'שיעורים מוקלטים' },
  { id: 'update', label: 'עדכונים' },
];

export const ARTICLES: SeedArticle[] = [
  {
    id: 'olive-2019',
    kind: 'article',
    title: 'זית: תיעוד פיתוח 2019–2024',
    text: 'חמש שנים על עץ אחד שנאסף מבוסתן נטוש. מהשתלה ראשונה ועד תצוגה.',
    meta: '14 דק׳ קריאה',
    species: 'olive',
    date: '12.08.2026',
    locked: false,
    body: [
      'העץ נאסף בחורף 2019 מבוסתן נטוש בהרי יהודה. גזע בקוטר 18 ס״מ, כמעט ללא שורשים דקים. השנה הראשונה הוקדשה להישרדות בלבד: מצע פומיס גס, הצללה, אפס גיזום.',
      'באביב 2021 נעשה הגיזום המבני הראשון. הורדנו שלושה ענפים ראשיים והשארנו שניים, שניהם עם עיניים רדומות גלויות. תוך שישה שבועות פרצו יותר מעשרים נצרים חדשים מהעץ הישן.',
      'עונת 2022–2023 עברה על חיווט ובניית הרמפה. חוט אלומיניום 2.5 מ״מ על הענפים הראשיים, 1.5 מ״מ על השלוחות. החוט הוסר לפני שהתחיל לחתוך, בכל פעם אחרי עונה אחת.',
      'בשתילה של מרץ 2024 העץ עבר לכלי התצוגה הראשון: מלבן 32 × 24, גלזורה חמצון ברזל, מהסטודיו. הכלי נבנה סביב המידות של העץ, לא ההפך.',
    ],
  },
  {
    id: 'juniper-year-one',
    kind: 'article',
    title: 'ערער: שנה ראשונה אחרי איסוף',
    text: 'מה עושים ומה לא עושים לעץ שהגיע מההר. בעיקר: לא לגעת.',
    meta: '9 דק׳ קריאה',
    species: 'juniper',
    date: '03.07.2026',
    locked: false,
    body: [
      'ערער שנאסף מההר מגיע עם מערכת שורשים חלקית ועלווה שהתרגלה לרוח ולשמש ישירה. כל שינוי חד בתנאים מוריד את סיכויי ההישרדות.',
      'בשנה הראשונה עושים דבר אחד: משקים נכון. המצע גס, הניקוז מלא, ובודקים לחות באצבע לפני כל השקיה. אין דישון בחודשיים הראשונים, אין גיזום, אין חיווט.',
      'סימן החיים הראשון הוא צמיחה חדשה בקצות הענפים, בדרך כלל באמצע הקיץ. רק אחרי חורף שני מתחילים לחשוב על עיצוב.',
    ],
  },
  {
    id: 'lesson-12',
    kind: 'lesson',
    title: 'שיעור 12 · גיזום מבני בזית — סתיו',
    text: 'מתי מקצרים ענפים ראשיים, כמה עיניים משאירים, ואיך בוחרים את קו הגזע.',
    meta: '48 דק׳ · מוקלט',
    species: 'olive',
    date: '20.09.2025',
    locked: true,
  },
  {
    id: 'lesson-4',
    kind: 'lesson',
    title: 'שיעור 4 · עיניים רדומות בעצים ים־תיכוניים',
    text: 'למה זית, מיש ואלון פורצים מהעץ הישן, ואיך מנצלים את זה בעיצוב.',
    meta: '35 דק׳ · מוקלט',
    date: '02.03.2025',
    locked: true,
  },
  {
    id: 'lesson-wire',
    kind: 'lesson',
    title: 'חיווט ענפים עבים',
    text: 'מתי מותר לכופף ענף בעובי אצבע, ואיך לא לשבור אותו.',
    meta: '52 דק׳ · מוקלט',
    date: '28.08.2026',
    locked: true,
  },
  {
    id: 'update-kiln',
    kind: 'update',
    title: 'פתיחת כבשן · 11.9',
    text: 'הכלים מהסדנה של אוגוסט מוכנים לאיסוף בסטודיו הפתוח.',
    meta: 'עדכון',
    date: '05.09.2026',
    locked: false,
    body: [
      'הכבשן נפתח ביום שישי 11.9 בשעה 10:00. הכלים מהסדנה של אוגוסט מוכנים לאיסוף בסטודיו הפתוח, עד 14:00.',
      'מי שלא מגיע: הכלים נשמרים בסטודיו עד המפגש הבא.',
    ],
  },
  {
    id: 'ficus-yellow',
    kind: 'article',
    title: 'עלים צהובים בפיקוס',
    text: 'שלוש סיבות, וסדר הבדיקה שחוסך זמן.',
    meta: '6 דק׳ קריאה',
    species: 'ficus',
    date: '15.06.2026',
    locked: false,
    body: [
      'עלים צהובים בפיקוס הם כמעט תמיד אחת משלוש סיבות: השקיית יתר, מעבר מקום, או חוסר אור. בודקים בסדר הזה.',
      'השקיית יתר: המצע רטוב יומיים אחרי ההשקיה, העלים רכים. מפסיקים להשקות עד שהמצע יבש בשני ס״מ העליונים.',
      'מעבר מקום: הפיקוס משיל עלים אחרי כל שינוי במיקום. זה נורמלי ועובר תוך שלושה שבועות.',
    ],
  },
];
