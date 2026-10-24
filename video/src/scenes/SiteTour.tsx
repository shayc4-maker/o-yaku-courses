import { AbsoluteFill, Img, interpolate, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { BrowserFrame, Camera, CAM_HOME, Caption, track, VIEW } from '../components';
import { C } from '../theme';
import pages from '../../public/capture-pages/pages.json';

/**
 * Short tour of the rest of the REAL site (snapshots from capture/record-pages.mjs): articles,
 * one article, ceramics gallery + commission calculator, shop. Captions only, no voice.
 */
type Box = { x: number; y: number; w: number; h: number };
type Shot = { name: string; file: string; height: number; boxes: Record<string, Box | null> };
const byName = Object.fromEntries((pages.shots as unknown as Shot[]).map((s) => [s.name, s]));

type Beat = { url: string; frames: number; caption: string; shots: [number, string][]; scroll: [number, number][]; zoom?: [number, number, number, number][] };

const calc = byName['calc-1']?.boxes.calculator ?? { x: 200, y: 2445, w: 1200, h: 711 };
const CALC_SCROLL = calc.y - 90;

const BEATS: Beat[] = [
  {
    url: 'o-yaku.com/articles', frames: 120, caption: 'מאמרים ותיעוד של עבודה על עצים לאורך שנים',
    shots: [[0, 'articles']], scroll: [[0, 0], [25, 0], [110, 330]],
  },
  {
    url: 'o-yaku.com/articles/…', frames: 150, caption: 'תיעוד פיתוח של עץ, שלב אחרי שלב',
    shots: [[0, 'article']], scroll: [[0, 0], [20, 0], [140, 2600]],
  },
  {
    url: 'o-yaku.com/ceramics', frames: 140, caption: 'כלי בונסאי בהתאמה אישית, מהסטודיו',
    shots: [[0, 'ceramics']], scroll: [[0, 0], [20, 0], [130, 1250]],
  },
  {
    url: 'o-yaku.com/ceramics', frames: 165, caption: 'מחשבון כלי בהזמנה: מידות, צורה, הדמיה ומחיר משוער',
    shots: [[0, 'ceramics'], [45, 'calc-1'], [90, 'calc-2'], [130, 'calc-3']],
    scroll: [[0, 1250], [35, CALC_SCROLL]],
    zoom: [[0, CAM_HOME.x, CAM_HOME.y, 1], [35, CAM_HOME.x, CAM_HOME.y, 1], [55, 800, 430, 1.07], [165, 800, 430, 1.07]],
  },
  {
    url: 'o-yaku.com/shop', frames: 150, caption: 'חנות: עצים, כלי עבודה, מצע וכלי קרמיקה',
    shots: [[0, 'shop']], scroll: [[0, 0], [20, 0], [140, 1500]],
  },
];

const XF = 10;
export const TOUR_FRAMES = BEATS.reduce((n, b) => n + b.frames, 0) - XF * (BEATS.length - 1);

export function SiteTour() {
  let at = 0;
  return (
    <AbsoluteFill>
      {BEATS.map((b, i) => {
        const from = at;
        at += b.frames - XF;
        return (
          <Sequence key={i} from={from} durationInFrames={b.frames}>
            <BeatView beat={b} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
}

function BeatView({ beat }: { beat: Beat }) {
  const f = useCurrentFrame();
  let name = beat.shots[0][1];
  for (const [t, n] of beat.shots) if (f >= t) name = n;
  const shot = byName[name];
  const scroll = Math.min(track(f, beat.scroll), Math.max(0, shot.height - VIEW.h));
  const o = interpolate(f, [0, XF, beat.frames - XF, beat.frames], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ opacity: o }}>
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 40%, ${C.stone100}, ${C.stone200})` }} />
      <Camera keys={beat.zoom ?? [[0, CAM_HOME.x, CAM_HOME.y, 1], [beat.frames, CAM_HOME.x, CAM_HOME.y, 1.03]]}>
        <BrowserFrame url={beat.url} tab="O-YAKU">
          <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', background: C.stone50 }}>
            <Img src={staticFile(`capture-pages/${shot.file}`)} style={{ position: 'absolute', left: 0, top: -scroll, width: VIEW.w, height: shot.height }} />
          </div>
        </BrowserFrame>
      </Camera>
      <Caption from={8} to={beat.frames - 6} text={beat.caption} />
    </AbsoluteFill>
  );
}
