/**
 * Everything editable about the video lives here: the question, the sources shown in the
 * answer, the live clip edit, and the on-screen captions.
 *
 * Source titles/texts are real published knowledge_segments from the O-YAKU database, lesson
 * "הרכבות סתיו ערערים 2024" (the same lesson the live clip comes from).
 */

export interface Source {
  title: string;
  text: string;
  lesson: string;
  meta: string;
  /** Marks the source that links to the live clip on Patreon. */
  live?: { timestamp: string };
}

/**
 * One piece of the live clip edit. `from`/`to` are seconds in the clip file; `speed` > 1 speeds
 * it up; `volume` is the live sound level (0 = muted). With `voice`, that line is narrated over
 * the piece (file voice/clip-<id>.mp3, made by `npm run voice`) and shown as its subtitle.
 */
export type Segment = { id: string; from: number; to: number; speed?: number; volume?: number; voice?: string };

export type ExplainerProps = {
  question: string;
  sources: Source[];
  live: {
    postTitle: string;
    postUrl: string;
    /** Clip file in video/public/ (kept out of git). null → animated placeholder. */
    clipFile: string | null;
    /** Where the clip file starts inside the full live, for the player's clock. */
    fileStart: string;
    /** The edit: pieces of the clip, played in order with short dissolves. */
    segments: Segment[];
    /** Subtitles for the live sound, in clip-file seconds: [from, to, text]. */
    subtitles: [number, number, string][];
  };
  /**
   * Voice-over, one line per moment in the video. Each line starts at its cue (tied to the
   * animation, so it stays in sync when timings change). `caption` is the on-screen text,
   * `voice` is what's spoken, `audio` is the file in video/public/voice/. When `audio` is null,
   * voice/<cue>.mp3 is used if it exists (that's what `npm run voice` writes), else silence.
   * `maxSec` is how long the cue's window is — a longer recording runs into the next line.
   * The rec-*.mp3 files are the owner's own recordings (cut and loudness-matched to the live clip).
   */
  narration: Record<Cue, { maxSec: number; caption: string | null; voice: string; audio: string | null }>;
  /** Optional background music in video/public/, ducked under the voice and the live clip. */
  music: string | null;
  /**
   * Audio export for editing elsewhere (e.g. DaVinci): 'voice' = narration only, 'live' = live
   * clip sound only, 'mix' = everything. With rawVoice, narration comes from voice-raw/<cue>.wav
   * (unprocessed cuts of the recording) instead of the cleaned files.
   */
  stem?: 'mix' | 'voice' | 'live';
  rawVoice?: boolean;
  /** ElevenLabs voice used by `npm run voice` ("shayka", the owner's cloned voice). */
  voiceId: string;
};

export type Cue = 'intro' | 'locked' | 'check' | 'ask' | 'answer' | 'toLive' | 'patreon' | 'outro';

export const defaultProps: ExplainerProps = {
  question: 'איך מרכיבים עלווה חדשה על ערער?',
  sources: [
    {
      title: 'קשירה ואטימה של אזור ההרכבה',
      text: 'קיבוע הייחור המוחדר בעזרת חוט ללא תזוזה ואטימת האזור במשחת החלמה לא-נוזלית להגנה על הקמביום.',
      lesson: 'הרכבות סתיו ערערים 2024',
      meta: 'סתיו',
      live: { timestamp: '21:03' }, // fileStart + first segment
    },
    {
      title: 'החלפת עלוות ערער מקומית באיטויגאווה',
      text: 'היתרונות בהחלפת עלוות ערער מקומית קוצנית וגסה בעלוות איטויגאווה עדינה וצפופה באמצעות הרכבה.',
      lesson: 'הרכבות סתיו ערערים 2024',
      meta: 'סתיו',
    },
    {
      title: 'הסתיו כעונה אידיאלית להרכבות',
      text: 'הפיזיולוגיה של העצים בסתיו, המאופיינת באגירת אנרגיה וצמיחה וסקולרית, הופכת עונה זו לאופטימלית להרכבות.',
      lesson: 'הרכבות סתיו ערערים 2024',
      meta: 'סתיו',
    },
  ],
  // Version A: the live's own sound, four spoken pieces.
  live: {
    postTitle: 'שיעור הרכבות סתיו בערערים',
    postUrl: 'patreon.com/u36592485/posts/shy-vr-hrkbvt-b-112241338',
    clipFile: 'live-norm.mp4', // live-source.mp4 with loudness-normalized audio (-16 LUFS)
    fileStart: '20:34',
    segments: [
      { id: 'angle', from: 29.2, to: 36.6 },
      { id: 'thread', from: 55.1, to: 60.6 },
      { id: 'oneStroke', from: 93.8, to: 99.1 },
      { id: 'tie', from: 100.0, to: 106.5 },
    ],
    subtitles: [
      [29.3, 33.7, 'נכנסים עם הסכין בזווית בין 30 ל-45 מעלות,'],
      [33.8, 36.6, 'יותר בכיוון 30 מעלות, בלי לפחד.'],
      [55.2, 60.5, 'ומשחיל את הייחור, שפתוח משני הצדדים שלו, לתוך החתך.'],
      [93.8, 96.5, 'עדיף להשחיל במכה אחת ולא להזיז יותר.'],
      [96.5, 99.1, 'ככל שמזיזים יותר, זה מוריד את סיכויי ההצלחה.'],
      [100.0, 106.5, 'אז אני פה מחבר ומהדק עם חוט את הייחור לחתך.'],
    ],
  },
  narration: {
    intro: { maxSec: 4.3, caption: null, voice: 'כל מה שנאמר בשיעורים ובלייבים של O-YAKU, במקום אחד.', audio: 'rec-intro.mp3' },
    locked: { maxSec: 3.7, caption: 'מנוע השאלות החדש, פתוח למנויי O-YAKU ב-Patreon', voice: 'מנוע השאלות החדש פתוח למנויי הפטרון שלנו.', audio: 'rec-locked.mp3' },
    check: { maxSec: 4.7, caption: 'התחברות בלחיצה, ובדיקה קצרה שהמנוי פעיל', voice: 'מתחברים עם חשבון הפטרון, ואחרי בדיקה קצרה של המנוי, אתם בפנים.', audio: 'rec-check.mp3' },
    ask: { maxSec: 6.8, caption: 'שואלים כל שאלה בתחום הבונסאי', voice: 'שואלים כל שאלה בתחום הבונסאי. למשל: איך מרכיבים עלווה על ערער?', audio: 'rec-ask.mp3' },
    answer: { maxSec: 5.1, caption: 'התשובה מגיעה עם מקורות מהשיעורים והלייבים', voice: 'התשובה נבנית מתוך השיעורים והלייבים עצמם, עם מקור לכל קטע.', audio: 'rec-answer.mp3' },
    toLive: { maxSec: 3.9, caption: 'וכל מקור מוביל לרגע המדויק בלייב', voice: 'רוצים לשמוע את ההסבר המלא? לחיצה אחת,', audio: 'rec-toLive.mp3' },
    // the live clip starts right after this line
    patreon: { maxSec: 3.1, caption: 'הלייב נפתח בפטרון, בדיוק מהרגע הנכון', voice: 'ואתם ברגע המדויק בלייב.', audio: 'rec-patreon.mp3' },
    outro: { maxSec: 5.6, caption: null, voice: 'שואלים, מקבלים תשובה, וממשיכים ללמוד. הצטרפו עכשיו.', audio: 'rec-outro.mp3' },
  },
  music: null,
  voiceId: 'kfiqnWKpE9m8HkyjWdgl',
};

/** Version B: the clearest work shots, partly sped up, narrated over a low live sound. */
export const narratedProps: ExplainerProps = {
  ...defaultProps,
  live: {
    ...defaultProps.live,
    segments: [
      { id: 'n-cut', from: 30.0, to: 40.0, speed: 1.5, volume: 0.15, voice: 'חותכים בעורק בזווית של כשלושים מעלות, בלי לפחד.' },
      { id: 'n-thread', from: 54.0, to: 68.0, speed: 2, volume: 0.15, voice: 'משחילים את הייחור לתוך החתך, במכה אחת, בלי להזיז.' },
      { id: 'n-tie', from: 103.0, to: 117.0, speed: 2, volume: 0.15, voice: 'ומהדקים היטב עם חוט, שנשאר עד שהאיחוי חזק.' },
      { id: 'n-done', from: 128.0, to: 134.0, volume: 0.15, voice: 'וכך מרכיבים עלווה חדשה על ערער ותיק.' },
    ],
    subtitles: [],
  },
};

export const segmentSeconds = (s: Segment) => (s.to - s.from) / (s.speed ?? 1);
export const clipSeconds = (live: ExplainerProps['live']) => live.segments.reduce((t, s) => t + segmentSeconds(s), 0);
