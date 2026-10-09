import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { fadeIn, Icon, Logo, usePop } from '../components';
import { BODY, C, DISPLAY } from '../theme';

export const INTRO_FRAMES = 120;
export const OUTRO_FRAMES = 180;

export function Intro() {
  const f = useCurrentFrame();
  const logo = usePop(4);
  const rise = (start: number) => ({ opacity: fadeIn(f, start, 16), transform: `translateY(${(1 - fadeIn(f, start, 16)) * 20}px)` });
  return (
    <AbsoluteFill style={{ background: C.stone50, alignItems: 'center', justifyContent: 'center', direction: 'rtl', fontFamily: BODY }}>
      <div style={{ transform: `scale(${logo})` }}>
        <Logo size={110} />
      </div>
      <div style={{ fontFamily: DISPLAY, fontWeight: 300, fontSize: 76, color: C.stone900, marginTop: 50, ...rise(22) }}>כל הידע מהשיעורים והלייבים</div>
      <div style={{ fontSize: 34, color: C.stone500, marginTop: 18, ...rise(40) }}>שואלים — ומקבלים תשובה עם מקור</div>
    </AbsoluteFill>
  );
}

export function Outro() {
  const f = useCurrentFrame();
  const pop = usePop(30);
  const lines = ['מתחברים עם Patreon', 'שואלים כל שאלה', 'צופים בקטע המדויק מהלייב'];
  return (
    <AbsoluteFill style={{ background: C.stone900, alignItems: 'center', justifyContent: 'center', direction: 'rtl', fontFamily: BODY, opacity: interpolate(f, [0, 12], [0, 1], { extrapolateRight: 'clamp' }) }}>
      <Logo size={96} inverse />
      <div style={{ display: 'flex', gap: 46, marginTop: 56 }}>
        {lines.map((l, i) => (
          <div key={l} style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 32, color: C.stone200, opacity: fadeIn(f, 10 + i * 10, 12) }}>
            <Icon name="check" size={28} color={C.clay400} />
            {l}
          </div>
        ))}
      </div>
      <div
        style={{
          marginTop: 70,
          fontSize: 38,
          fontWeight: 700,
          color: '#fff',
          background: C.clay500,
          borderRadius: 999,
          padding: '20px 56px',
          transform: `scale(${pop})`,
        }}
      >
        הצטרפו כמנויים ב-Patreon
      </div>
      <div style={{ marginTop: 26, fontSize: 26, color: C.stone400, direction: 'ltr', opacity: fadeIn(f, 50, 14) }}>o-yaku.com</div>
      <div style={{ position: 'absolute', bottom: 0, height: 6, left: 0, width: `${interpolate(f, [0, 180], [0, 100])}%`, background: C.clay500 }} />
    </AbsoluteFill>
  );
}
