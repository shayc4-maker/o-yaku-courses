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
};

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
};
