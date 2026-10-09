import { interpolate, useCurrentFrame } from 'remotion';
import { BrowserFrame, Button, Camera, CAM_HOME, Cursor, fadeIn, Icon, Logo, press, Spinner, track, usePop } from '../components';
import type { ExplainerProps } from '../content';
import { C, DISPLAY } from '../theme';

/**
 * The site part of the walkthrough, one continuous browser take (local frames):
 *   0–115   logged-out knowledge base, engine locked → click "התחברות עם Patreon"
 *   120–250 short subscription check modal → connected
 *   300–430 type the question → click "חפש"
 *   432–600 searching → answer with sources, live source highlighted
 *   600–720 click "צפייה בקטע בפטרון" → push-in transition to Patreon
 */
/**
 * Short pauses inserted into the walkthrough so each voice-over line fits its moment:
 * before the connect click, after connecting, and before the search click. Every frame
 * number in this scene goes through d(), so the pauses are idle time, not frozen frames.
 */
const PAUSES: [at: number, frames: number][] = [
  [60, 20],
  [250, 10],
  [430, 8],
];
export const d = (n: number) => n + PAUSES.reduce((sum, [at, len]) => (n >= at ? sum + len : sum), 0);

export const SITE_FLOW_FRAMES = d(720);

export const T = {
  clickConnect: d(115),
  modalIn: d(120),
  step1Done: d(165),
  step2Done: d(205),
  connected: d(245),
  clickInput: d(300),
  typeStart: d(306),
  charFrames: 5,
  clickSearch: d(438),
  resultsAt: d(478),
  clickLive: d(668),
};

// Layout, in viewport coords (1600 × 888).
const BOX = { left: 250, right: 1350, top: 300, h: 64 };
const SEARCH_BTN = { left: 250, w: 136 };
const CONNECT_BTN = { cx: 800, cy: 622, w: 330, h: 58 };
const ROW_TOP = 446;
const ROW_H = 138;
const LIVE_BTN = { left: 250, w: 290, cy: ROW_TOP + 66, h: 50 };

export function SiteFlow({ question, sources }: Pick<ExplainerProps, 'question' | 'sources'>) {
  const f = useCurrentFrame();
  const connected = f >= T.connected;
  // Type faster for long questions so typing always ends before the search click.
  const cf = Math.max(2, Math.min(T.charFrames, Math.floor((T.clickSearch - 40 - T.typeStart) / question.length)));
  const typeEnd = T.typeStart + question.length * cf;
  const typed = question.slice(0, Math.max(0, Math.floor((f - T.typeStart) / cf) + 1));
  const searching = f >= T.clickSearch && f < T.resultsAt;
  const lockOpacity = interpolate(f, [T.connected - 5, T.connected + 12], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const searchBtnCenter: [number, number] = [SEARCH_BTN.left + SEARCH_BTN.w / 2, BOX.top + BOX.h / 2];
  const liveRow = Math.max(0, sources.findIndex((s) => s.live)) * ROW_H;
  const liveBtnCenter: [number, number] = [LIVE_BTN.left + 18 + LIVE_BTN.w / 2, LIVE_BTN.cy + liveRow];

  return (
    <Camera
      keys={[
        [0, CAM_HOME.x, CAM_HOME.y, 1],
        [d(60), CAM_HOME.x, CAM_HOME.y, 1],
        [d(105), 800, 500, 1.18],
        [d(210), 800, 470, 1.18],
        [d(255), CAM_HOME.x, CAM_HOME.y, 1],
        [d(285), CAM_HOME.x, CAM_HOME.y, 1],
        [d(315), 800, BOX.top + 40, 1.42],
        [typeEnd + 30, 760, BOX.top + 40, 1.42],
        [T.resultsAt, CAM_HOME.x, CAM_HOME.y + 40, 1],
        [d(575), CAM_HOME.x, CAM_HOME.y + 40, 1],
        [d(615), 640, ROW_TOP + 70 + liveRow, 1.38],
        [T.clickLive + 4, 600, ROW_TOP + 70 + liveRow, 1.42],
        [d(720), liveBtnCenter[0], liveBtnCenter[1], 2.6],
      ]}
    >
      <BrowserFrame url="o-yaku.com/kb" tab="O-YAKU · מאגר ידע">
        <Header connected={connected} />

        {/* page heading */}
        <div style={{ position: 'absolute', right: 250, top: 128, fontSize: 13, letterSpacing: '.18em', fontWeight: 600, color: C.clay600 }}>KNOWLEDGE · מאגר ידע</div>
        <div style={{ position: 'absolute', right: 250, top: 158, fontFamily: DISPLAY, fontWeight: 300, fontSize: 52, color: C.stone900 }}>שאלו את המאגר</div>
        <div style={{ position: 'absolute', right: 250, top: 236, fontSize: 21, color: C.stone500 }}>תשובות מתוך כל השיעורים והלייבים של O-YAKU, עם מקור לכל קטע.</div>

        {/* ask box */}
        <div
          style={{
            position: 'absolute',
            right: 1600 - BOX.right,
            left: SEARCH_BTN.left + SEARCH_BTN.w + 14,
            top: BOX.top,
            height: BOX.h,
            background: connected ? C.stone0 : C.stone100,
            border: `1px solid ${f >= T.clickInput && f < T.clickSearch ? C.clay500 : C.stone300}`,
            boxShadow: f >= T.clickInput && f < T.clickSearch ? `0 0 0 4px ${C.clay100}` : 'none',
            borderRadius: 4,
            display: 'flex',
            alignItems: 'center',
            gap: 14,
            padding: '0 22px',
            fontSize: 24,
          }}
        >
          {connected ? <Icon name="search" size={22} color={C.stone400} /> : <Icon name="lock" size={22} color={C.stone400} />}
          {f >= T.typeStart ? (
            <span style={{ color: C.stone900 }}>
              {typed}
              {f < T.clickSearch && Math.floor(f / 15) % 2 === 0 ? <span style={{ color: C.clay500 }}>|</span> : null}
            </span>
          ) : (
            <span style={{ color: C.stone400 }}>{connected ? 'למשל: מתי לגזום זית? איך עובדים על שורשים?' : 'זמין למנויים בלבד'}</span>
          )}
        </div>
        <Button
          scale={press(f, T.clickSearch)}
          style={{ left: SEARCH_BTN.left, top: BOX.top, width: SEARCH_BTN.w, height: BOX.h, fontSize: 21, opacity: connected ? 1 : 0.4 }}
        >
          חפש
        </Button>

        {/* locked state card */}
        {lockOpacity > 0 ? <LockedCard opacity={lockOpacity} f={f} /> : null}

        {/* subscription check modal */}
        {f >= T.modalIn && f < T.connected + 12 ? <CheckModal f={f} /> : null}

        {/* searching */}
        {searching ? (
          <div style={{ position: 'absolute', right: 250, top: 410, display: 'flex', alignItems: 'center', gap: 14, fontSize: 20, color: C.stone500 }}>
            <Spinner size={22} />
            מחפשים בשיעורים ובלייבים…
          </div>
        ) : null}

        {/* answer: sources */}
        {f >= T.resultsAt ? <Results f={f} sources={sources} /> : null}

        <Cursor
          appear={30}
          clicks={[T.clickConnect, T.clickInput, T.clickSearch, T.clickLive]}
          path={[
            [0, 1250, 760],
            [d(65), 1250, 760],
            [T.clickConnect - 6, CONNECT_BTN.cx + 40, CONNECT_BTN.cy + 6],
            [T.connected + 10, CONNECT_BTN.cx + 40, CONNECT_BTN.cy + 6],
            [T.clickInput - 4, 980, BOX.top + 34],
            [typeEnd + 6, 980, BOX.top + 34],
            [T.clickSearch - 6, searchBtnCenter[0], searchBtnCenter[1] + 4],
            [d(600), searchBtnCenter[0], searchBtnCenter[1] + 4],
            [T.clickLive - 6, liveBtnCenter[0] + 30, liveBtnCenter[1] + 4],
          ]}
        />
      </BrowserFrame>
    </Camera>
  );
}

function Header({ connected }: { connected: boolean }) {
  const f = useCurrentFrame();
  const pop = usePop(T.connected);
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, top: 0, height: 78, borderBottom: `1px solid ${C.stone200}`, display: 'flex', alignItems: 'center', gap: 44, padding: '0 64px', background: 'rgba(251,249,246,.92)' }}>
      <Logo size={40} />
      {['בית', 'מאגר ידע', 'מאמרים', 'סטודיו', 'חנות', 'אודות'].map((l) => (
        <span key={l} style={{ fontSize: 16, fontWeight: 600, color: l === 'מאגר ידע' ? C.stone900 : C.stone500, borderBottom: `1px solid ${l === 'מאגר ידע' ? C.clay500 : 'transparent'}`, paddingBottom: 3 }}>
          {l}
        </span>
      ))}
      <span style={{ flex: 1 }} />
      {connected ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, background: C.moss100, color: C.moss700, borderRadius: 999, padding: '8px 16px 8px 10px', fontSize: 15, fontWeight: 700, transform: `scale(${pop})` }}>
          <span style={{ width: 30, height: 30, borderRadius: '50%', background: C.moss500, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Icon name="check" size={16} color="#fff" />
          </span>
          מחובר · מנוי פעיל
        </div>
      ) : (
        <div style={{ fontSize: 15, fontWeight: 600, color: C.stone700, border: `1px solid ${C.stone300}`, borderRadius: 4, padding: '8px 16px', opacity: f > 0 ? 1 : 0 }}>התחברות</div>
      )}
    </div>
  );
}

function LockedCard({ opacity, f }: { opacity: number; f: number }) {
  return (
    <div style={{ opacity }}>
      <div
        style={{
          position: 'absolute',
          left: 400,
          width: 800,
          top: 400,
          height: 290,
          background: C.stone0,
          border: `1px solid ${C.stone200}`,
          borderRadius: 6,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          paddingTop: 30,
          boxShadow: '0 8px 30px rgba(27,25,23,.06)',
        }}
      >
        <div style={{ width: 52, height: 52, borderRadius: '50%', background: C.clay50, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="lock" size={24} color={C.clay600} />
        </div>
        <div style={{ fontFamily: DISPLAY, fontSize: 28, color: C.stone900, marginTop: 14 }}>המנוע זמין למנויי O-YAKU ב-Patreon</div>
        <div style={{ fontSize: 18, color: C.stone500, marginTop: 6 }}>חברו את חשבון הפטרון כדי לשאול שאלות ולצפות בשיעורים</div>
      </div>
      <Button
        scale={press(f, T.clickConnect)}
        variant="dark"
        style={{ left: CONNECT_BTN.cx - CONNECT_BTN.w / 2, top: CONNECT_BTN.cy - CONNECT_BTN.h / 2, width: CONNECT_BTN.w, height: CONNECT_BTN.h, fontSize: 20, borderRadius: 999 }}
      >
        התחברות עם Patreon
      </Button>
    </div>
  );
}

function CheckModal({ f }: { f: number }) {
  const pop = usePop(T.modalIn);
  const out = interpolate(f, [T.connected - 4, T.connected + 10], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const steps: [string, number, number][] = [
    ['מתחברים לחשבון Patreon', T.modalIn + 8, T.step1Done],
    ['בודקים שהמנוי פעיל', T.step1Done + 4, T.step2Done],
  ];
  const success = f >= T.step2Done + 6;
  return (
    <div style={{ position: 'absolute', inset: 0, background: `rgba(27,25,23,${0.32 * Math.min(pop, 1) * out})`, zIndex: 50 }}>
      <div
        style={{
          position: 'absolute',
          left: 800 - 280,
          top: 444 - 150,
          width: 560,
          height: 300,
          background: C.stone0,
          borderRadius: 10,
          boxShadow: '0 30px 80px rgba(0,0,0,.25)',
          padding: '34px 40px',
          transform: `scale(${0.92 + 0.08 * pop})`,
          opacity: Math.min(pop, 1) * out,
        }}
      >
        <div style={{ fontFamily: DISPLAY, fontSize: 28, color: C.stone900 }}>בדיקת מנוי</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18, marginTop: 26 }}>
          {steps.map(([label, start, done]) =>
            f >= start ? (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 14, fontSize: 21, color: f >= done ? C.stone800 : C.stone500, opacity: fadeIn(f, start, 6) }}>
                {f >= done ? <Icon name="check" size={22} color={C.moss700} /> : <Spinner size={22} />}
                {label}
              </div>
            ) : null,
          )}
          {success ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 22, fontWeight: 700, color: C.moss700, background: C.moss100, borderRadius: 6, padding: '12px 16px', opacity: fadeIn(f, T.step2Done + 6, 6) }}>
              מחובר · ברוכים הבאים!
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function Results({ f, sources }: { f: number; sources: ExplainerProps['sources'] }) {
  return (
    <>
      <div style={{ position: 'absolute', right: 250, top: 404, fontSize: 18, color: C.stone500, opacity: fadeIn(f, T.resultsAt, 8) }}>
        <b style={{ color: C.stone800 }}>{sources.length} קטעי ידע</b> · מתוך שיעורים ולייבים
      </div>
      {sources.map((s, i) => {
        const start = T.resultsAt + 6 + i * 12;
        const o = fadeIn(f, start, 10);
        const top = ROW_TOP + i * ROW_H;
        const highlight = s.live ? track(f, [[d(575), 0], [d(600), 1]]) : 0;
        return (
          <div
            key={s.title}
            style={{
              position: 'absolute',
              left: 250,
              right: 250,
              top,
              height: ROW_H - 10,
              opacity: o * (s.live ? 1 : 1 - 0.45 * highlight),
              transform: `translateY(${(1 - o) * 16}px)`,
              borderTop: `1px solid ${C.stone200}`,
              background: `rgba(253,243,243,${highlight})`,
              boxShadow: highlight ? `inset -4px 0 0 ${C.clay500}` : 'none',
              display: 'flex',
              alignItems: 'flex-start',
              gap: 16,
              padding: '20px 18px 0',
            }}
          >
            <Icon name={s.live ? 'radio' : 'file-text'} size={20} color={C.clay600} style={{ marginTop: 4 }} />
            <div style={{ flex: 1, minWidth: 0, paddingLeft: s.live ? 310 : 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <span style={{ fontSize: 21, fontWeight: 700, color: C.stone900 }}>{s.title}</span>
                {s.live ? (
                  <span style={{ fontSize: 14, fontWeight: 700, color: C.clay700, background: C.clay100, borderRadius: 999, padding: '3px 12px', direction: 'rtl' }}>
                    לייב · {s.live.timestamp}
                  </span>
                ) : null}
              </div>
              <div style={{ fontSize: 18, color: C.stone500, marginTop: 6, lineHeight: 1.5 }}>{s.text}</div>
              <div style={{ fontSize: 14, color: C.stone400, marginTop: 6, fontWeight: 600, letterSpacing: '.04em' }}>
                {s.lesson} · {s.meta}
              </div>
            </div>
          </div>
        );
      })}
      {sources.some((s) => s.live) ? (
        <Button
          scale={press(f, T.clickLive) * (0.9 + 0.1 * fadeIn(f, T.resultsAt + 6, 10))}
          style={{
            left: LIVE_BTN.left + 18,
            top: LIVE_BTN.cy - LIVE_BTN.h / 2 + sources.findIndex((s) => s.live) * ROW_H,
            width: LIVE_BTN.w,
            height: LIVE_BTN.h,
            opacity: fadeIn(f, T.resultsAt + 6, 10),
            borderRadius: 999,
          }}
        >
          <Icon name="play" size={16} color="#fff" />
          צפייה בקטע בפטרון
        </Button>
      ) : null}
    </>
  );
}
