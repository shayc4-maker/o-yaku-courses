import { Img, interpolate, staticFile, useCurrentFrame } from 'remotion';
import { BrowserFrame, Camera, CAM_HOME, Cursor, Spinner, track, VIEW } from '../components';
import { C, DISPLAY } from '../theme';
import capture from '../../public/capture/timeline.json';

/**
 * The site part of the walkthrough, built from snapshots of the REAL current site
 * (shayc4-maker/o-yaku-website main, captured by capture/record.mjs with a fake transport).
 * Each beat shows one captured state; scrolling, cursor and camera are added here.
 *
 * Flow (current site behaviour): home as a guest → header "התחברות לפטרון" → Patreon sign-in
 * (stand-in card; the real OAuth page isn't shown) → back on the home page as a member
 * ("מנוי פעיל") → juniper question → five server stages → answer with sources grouped by
 * lesson → "צפייה בפטראון" on source [3].
 */
type Box = { x: number; y: number; w: number; h: number };
type Shot = { name: string; file: string; height: number; boxes: Record<string, Box | null> };
const shots = capture.shots as unknown as Shot[];
const byName = Object.fromEntries(shots.map((s) => [s.name, s]));
const center = (shot: string, box: string): [number, number] => {
  const b = byName[shot]?.boxes[box];
  if (!b) throw Error(`capture box missing: ${shot}.${box}`);
  return [b.x + b.w / 2, b.y + b.h / 2];
};

const TYPE_FRAMES = 3;
const QLEN = capture.question.length;

// Beat timings (frames, local to this scene).
export const R = {
  clickLogin: 95,
  patreonIn: 101,
  homeMember: 177,
  scrollToQuestion: 242,
  clickInput: 300,
  typeStart: 306,
  get typeEnd() { return this.typeStart + QLEN * TYPE_FRAMES; },
  get clickAsk2() { return this.typeEnd + 22; },
  get stage0() { return this.clickAsk2 + 4; },
  get answer() { return this.stage0 + 6 * 24; },
  get clickPatreon() { return this.answer + 190; },
};
export const REAL_SITE_FRAMES = R.clickPatreon + 26;

const Q_SCROLL = 440; // page scroll that puts the question area in view
const ANSWER_SCROLL = 760;
const SOURCES_SCROLL = 1360;

function currentShot(f: number): string {
  const seq: [number, string][] = [[0, 'home'], [R.homeMember, 'home-member']];
  for (let i = 1; i <= QLEN; i++) seq.push([R.typeStart + (i - 1) * TYPE_FRAMES, `type-${String(i).padStart(2, '0')}`]);
  const stages = ['stage-sent', 'stage-approved', 'stage-retrieval', 'stage-selection', 'stage-generation', 'stage-references'];
  stages.forEach((s, i) => seq.push([R.stage0 + i * 24, s]));
  seq.push([R.answer, 'answer']);
  let name = 'home';
  for (const [at, n] of seq) if (f >= at) name = n;
  return name;
}

function scrollAt(f: number): number {
  return track(f, [
    [0, 0], [R.scrollToQuestion, 0], [R.scrollToQuestion + 45, Q_SCROLL],
    [R.stage0 + 10, Q_SCROLL], [R.stage0 + 40, Q_SCROLL + 150], [R.answer, Q_SCROLL + 150], [R.answer + 45, ANSWER_SCROLL],
    [R.answer + 100, ANSWER_SCROLL], [R.answer + 150, SOURCES_SCROLL],
  ]);
}

export function RealSite() {
  const f = useCurrentFrame();
  const shot = byName[currentShot(f)];
  const scroll = scrollAt(f);
  const inPatreon = f >= R.patreonIn && f < R.homeMember;
  const url = inPatreon ? 'patreon.com/oauth2/authorize · O-YAKU' : 'o-yaku.com';

  // Cursor path in viewport coords (page coords minus the scroll at that moment).
  const vp = (shotName: string, box: string, s: number, dx = 0, dy = 6): [number, number] => {
    const [x, y] = center(shotName, box);
    return [x + dx, y - s + dy];
  };
  const login = vp('home', 'headerLogin', 0);
  const status = vp('home-member', 'connection', 0, 0, 0);
  const input = vp('home-member', 'input', Q_SCROLL, 120);
  const ask2 = vp('type-31', 'submit', Q_SCROLL);
  const link = vp('answer', 'source3Link', SOURCES_SCROLL, 10, 4);

  const pathKeys: [number, number, number][] = [
    [0, 1000, 600], [30, 1000, 600],
    [R.clickLogin - 8, login[0], login[1]], [R.patreonIn, login[0], login[1]],
    [R.homeMember + 50, login[0] + 120, login[1] + 160],
    [R.clickInput - 6, input[0], input[1]], [R.typeEnd, input[0], input[1]],
    [R.clickAsk2 - 6, ask2[0], ask2[1]], [R.stage0 + 30, ask2[0] + 260, ask2[1] + 220],
    [R.answer + 150, 820, 520], [R.clickPatreon - 8, link[0], link[1]],
  ];

  return (
    <Camera
      keys={[
        [0, CAM_HOME.x, CAM_HOME.y, 1],
        [40, CAM_HOME.x, CAM_HOME.y, 1],
        [R.clickLogin - 10, login[0] + 260, login[1] + 150, 1.6],
        [R.clickLogin + 4, login[0] + 260, login[1] + 150, 1.6],
        [R.patreonIn + 20, CAM_HOME.x, CAM_HOME.y, 1],
        [R.homeMember + 5, CAM_HOME.x, CAM_HOME.y, 1],
        [R.homeMember + 25, status[0] + 260, status[1] + 150, 1.6],
        [R.scrollToQuestion - 5, status[0] + 260, status[1] + 150, 1.6],
        [R.scrollToQuestion + 30, CAM_HOME.x, CAM_HOME.y, 1],
        [R.clickInput, 820, input[1] - 20, 1.35],
        [R.typeEnd + 10, 820, input[1] - 20, 1.35],
        [R.stage0 + 40, 800, 520, 1.12],
        [R.answer + 20, CAM_HOME.x, CAM_HOME.y, 1],
        [R.answer + 150, CAM_HOME.x, CAM_HOME.y, 1],
        [R.clickPatreon - 10, link[0] + 200, link[1] - 40, 1.4],
        [REAL_SITE_FRAMES, link[0], link[1], 2.2],
      ]}
    >
      <BrowserFrame url={url} tab="O-YAKU">
        <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', background: C.stone50 }}>
          <Img
            src={staticFile(`capture/${shot.file}`)}
            style={{ position: 'absolute', left: 0, top: -Math.min(scroll, Math.max(0, shot.height - VIEW.h)), width: VIEW.w, height: shot.height }}
          />
        </div>
        {inPatreon ? <PatreonSignIn f={f - R.patreonIn} /> : null}
        <Cursor appear={20} clicks={[R.clickLogin, R.clickInput, R.clickAsk2, R.clickPatreon]} path={pathKeys} />
      </BrowserFrame>
    </Camera>
  );
}

/** Stand-in for the Patreon OAuth page: the real one isn't captured or imitated. */
function PatreonSignIn({ f }: { f: number }) {
  const o = interpolate(f, [0, 8, 68, 76], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const back = f > 40;
  return (
    <div style={{ position: 'absolute', inset: 0, background: `rgba(244,241,236,${0.96 * o})`, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: o, zIndex: 50 }}>
      <div style={{ background: C.stone0, border: `1px solid ${C.stone200}`, borderRadius: 10, padding: '40px 56px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18, boxShadow: '0 20px 60px rgba(0,0,0,.12)' }}>
        <Spinner size={34} />
        <div style={{ fontFamily: DISPLAY, fontSize: 30, color: C.stone900 }}>{back ? 'המנוי אומת · חוזרים לאתר' : 'מתחברים דרך Patreon'}</div>
        <div style={{ fontSize: 18, color: C.stone500 }}>{back ? 'כל השיעורים והשאלות פתוחים' : 'אישור החיבור בחשבון הפטרון שלכם'}</div>
      </div>
    </div>
  );
}
