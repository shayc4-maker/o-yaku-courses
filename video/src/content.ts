/**
 * Everything editable about the video lives here: the question, the sources shown in the
 * answer, the live clip, and the on-screen captions.
 *
 * Source titles/texts are real published knowledge_segments about olives from the O-YAKU
 * database (lessons "שאלות ותשובות יולי" and "זיתים 101 יולי 2025").
 */

export interface Source {
  title: string;
  text: string;
  lesson: string;
  meta: string;
  /** Marks the source that links to the live clip on Patreon. */
  live?: { timestamp: string };
}

export type ExplainerProps = {
  question: string;
  sources: Source[];
  live: {
    postTitle: string;
    postUrl: string;
    /**
     * Put the clip in video/public/ and set e.g. 'live-clip.mp4'. null → animated placeholder.
     * The clip plays from its first frame; trim it to the exact segment beforehand.
     */
    clipFile: string | null;
    /** How long the clip runs in the video, in seconds. Match it to the trimmed clip. */
    clipSeconds: number;
    /** Subtitles burned over the clip — part of the spoken answer. [startSec, endSec, text]. */
    subtitles: [number, number, string][];
  };
  /**
   * Voice-over, one line per moment in the video. Each line starts at its cue (tied to the
   * animation, so it stays in sync when timings change). `caption` is the on-screen text,
   * `voice` is what's spoken, `audio` is the file in video/public/voice/. When `audio` is null,
   * voice/<cue>.mp3 is used if it exists (that's what `npm run voice` writes), else silence.
   * `maxSec` is how long the cue's window is — a longer recording runs into the next line.
   */
  narration: Record<Cue, { maxSec: number; caption: string | null; voice: string; audio: string | null }>;
  /** Optional background music in video/public/, ducked under the voice and the live clip. */
  music: string | null;
};

export type Cue = 'intro' | 'locked' | 'check' | 'ask' | 'answer' | 'toLive' | 'patreon' | 'outro';

export const defaultProps: ExplainerProps = {
  question: 'מתי גוזמים זית?',
  sources: [
    {
      title: 'דחיית עבודות עיצוב אחרונות בזיתים לסתיו',
      text: 'קיימת אפשרות לדחות את פעולות העיצוב, הגיזום והחיווט בזיתים לחודשים ספטמבר-אוקטובר, כהכנה לחורף וכחלק מסידור העבודה השנתי.',
      lesson: 'שאלות ותשובות יולי',
      meta: 'סתיו',
      live: { timestamp: '12:34' }, // TODO: real timestamp in the live
    },
    {
      title: 'חשיבות הגיזום המיידי בזיתים',
      text: 'יש לבצע גיזום בזיתים ללא דיחוי כדי למנוע נשירת עלים פנימיים ואובדן ענפים.',
      lesson: 'שאלות ותשובות יולי',
      meta: 'קיץ',
    },
    {
      title: 'תזמון בניית רמיפיקציה ועיבוי ענפים',
      text: 'בזית יש להתחיל את ההסתעפות מוקדם ולא להמתין להתעבות מלאה, כדי למנוע ניוון של ניצנים פנימיים.',
      lesson: 'זיתים 101 · יולי 2025',
      meta: 'כל השנה',
    },
  ],
  live: {
    postTitle: 'לייב שאלות ותשובות · יולי',
    postUrl: 'patreon.com/o-yaku',
    clipFile: null,
    clipSeconds: 12,
    // Placeholder subtitles paraphrasing the segment above — replace with the real transcript lines.
    subtitles: [
      [0.5, 4.5, 'את העבודות האחרונות על הזיתים אפשר לדחות לסתיו —'],
      [4.5, 8.5, 'ספטמבר, אוקטובר. גיזום, חיווט ועיצוב,'],
      [8.5, 12, 'כהכנה לחורף וכחלק מסדר העבודה השנתי.'],
    ],
  },
  narration: {
    intro: { maxSec: 4, caption: null, voice: 'כל מה שנאמר בשיעורים ובלייבים של O-YAKU, במקום אחד.', audio: null },
    locked: { maxSec: 3.5, caption: 'מנוע השאלות פתוח למנויי O-YAKU ב-Patreon', voice: 'מנוע השאלות פתוח למנויי הפטרון שלנו.', audio: null },
    check: { maxSec: 5, caption: 'התחברות בלחיצה, ובדיקה קצרה שהמנוי פעיל', voice: 'מתחברים עם חשבון הפטרון, ואחרי בדיקה קצרה של המנוי, אתם בפנים.', audio: null },
    ask: { maxSec: 4.5, caption: 'עכשיו אפשר לשאול כל שאלה', voice: 'עכשיו שואלים כל שאלה על העצים שלכם. למשל: מתי גוזמים זית?', audio: null },
    answer: { maxSec: 5, caption: 'התשובה מגיעה עם מקורות מהשיעורים והלייבים', voice: 'התשובה נבנית מתוך השיעורים והלייבים עצמם, עם מקור לכל קטע.', audio: null },
    toLive: { maxSec: 3.8, caption: 'וכל מקור מוביל לרגע המדויק בלייב', voice: 'רוצים לשמוע את ההסבר המלא? לחיצה אחת,', audio: null },
    // then the live clip's own audio plays
    patreon: { maxSec: 2.5, caption: 'הלייב נפתח בפטרון, בדיוק מהרגע הנכון', voice: 'ואתם ברגע המדויק בלייב.', audio: null },
    outro: { maxSec: 5.5, caption: null, voice: 'שואלים, מקבלים תשובה, וממשיכים ללמוד. הצטרפו אלינו בפטרון.', audio: null },
  },
  music: null,
};
