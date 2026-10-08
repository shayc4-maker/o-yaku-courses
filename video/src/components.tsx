import type { CSSProperties, ReactNode } from 'react';
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { BODY, C, DISPLAY } from './theme';

/* ---------- animation helpers ---------- */

const EASE = Easing.inOut(Easing.cubic);

/** Piecewise interpolation over keyframes [frame, value] with ease-in-out between them. */
export function track(f: number, keys: [number, number][]): number {
  if (f <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    const [f1, v1] = keys[i];
    const [f0, v0] = keys[i - 1];
    if (f <= f1) return interpolate(f, [f0, f1], [v0, v1], { easing: EASE });
  }
  return keys[keys.length - 1][1];
}

export const fade = (f: number, start: number, end: number, len = 12) =>
  interpolate(f, [start, start + len, end - len, end], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

export const fadeIn = (f: number, start: number, len = 12) =>
  interpolate(f, [start, start + len], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

export function usePop(start: number) {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: f - start, fps, config: { damping: 18, stiffness: 140 } });
}

/** Scale dip around a click frame, for buttons. */
export const press = (f: number, at: number) =>
  interpolate(f, [at - 4, at, at + 6], [1, 0.95, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

/* ---------- brand ---------- */

export function Logo({ size = 40, inverse = false }: { size?: number; inverse?: boolean }) {
  return (
    <span
      style={{
        fontFamily: DISPLAY,
        fontWeight: 500,
        fontSize: size * 0.5,
        letterSpacing: '0.04em',
        lineHeight: 1,
        color: inverse ? C.stone50 : C.stone900,
        display: 'inline-flex',
        alignItems: 'center',
        gap: size * 0.2,
        direction: 'ltr',
      }}
    >
      <span
        style={{
          width: size * 0.36,
          height: size * 0.36,
          borderRadius: '50%',
          border: `${Math.max(2, size / 20)}px solid ${inverse ? C.stone300 : C.clay500}`,
          display: 'inline-block',
        }}
      />
      O-YAKU
    </span>
  );
}

/* ---------- icons (Lucide paths) ---------- */

const ICONS: Record<string, ReactNode> = {
  lock: (
    <>
      <rect x="3" y="11" width="18" height="11" rx="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </>
  ),
  check: <path d="M20 6 9 17l-5-5" />,
  play: <polygon points="6 3 20 12 6 21 6 3" fill="currentColor" />,
  search: (
    <>
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.3-4.3" />
    </>
  ),
  'arrow-left': <path d="M19 12H5m7 7-7-7 7-7" />,
  'file-text': (
    <>
      <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
      <path d="M14 2v4a2 2 0 0 0 2 2h4M16 13H8M16 17H8M10 9H8" />
    </>
  ),
  radio: (
    <>
      <circle cx="12" cy="12" r="2" />
      <path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14" />
    </>
  ),
  'external-link': <path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />,
};

export function Icon({ name, size = 18, color = 'currentColor', style }: { name: string; size?: number; color?: string; style?: CSSProperties }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" style={{ color, flexShrink: 0, ...style }}>
      {ICONS[name]}
    </svg>
  );
}

export function Spinner({ size = 20, color = C.clay500 }: { size?: number; color?: string }) {
  const f = useCurrentFrame();
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" style={{ transform: `rotate(${f * 14}deg)`, flexShrink: 0 }}>
      <circle cx="12" cy="12" r="9" fill="none" stroke={C.stone200} strokeWidth="3" />
      <path d="M12 3a9 9 0 0 1 9 9" fill="none" stroke={color} strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

/* ---------- browser chrome ---------- */

export const BROWSER = { x: 160, y: 70, w: 1600, h: 940, bar: 52 };
/** Canvas coords of the viewport's top-left corner. */
export const VIEW = { x: BROWSER.x, y: BROWSER.y + BROWSER.bar, w: BROWSER.w, h: BROWSER.h - BROWSER.bar };

export function BrowserFrame({ url, tab, children, page = C.stone50 }: { url: string; tab: string; children: ReactNode; page?: string }) {
  return (
    <div
      style={{
        position: 'absolute',
        left: BROWSER.x,
        top: BROWSER.y,
        width: BROWSER.w,
        height: BROWSER.h,
        borderRadius: 14,
        overflow: 'hidden',
        background: page,
        boxShadow: '0 30px 80px rgba(27,25,23,.18), 0 2px 8px rgba(27,25,23,.08)',
        border: `1px solid ${C.stone200}`,
      }}
    >
      <div style={{ height: BROWSER.bar, background: C.stone100, borderBottom: `1px solid ${C.stone200}`, display: 'flex', alignItems: 'center', gap: 18, padding: '0 20px', direction: 'ltr' }}>
        <div style={{ display: 'flex', gap: 8 }}>
          {['#E5817F', '#E8C27A', '#A9B98F'].map((c) => (
            <span key={c} style={{ width: 13, height: 13, borderRadius: '50%', background: c }} />
          ))}
        </div>
        <div style={{ fontFamily: BODY, fontSize: 14, color: C.stone700, background: C.stone0, padding: '6px 16px', borderRadius: 8, fontWeight: 600 }}>{tab}</div>
        <div style={{ flex: 1, fontFamily: BODY, fontSize: 15, color: C.stone500, background: C.stone0, padding: '7px 16px', borderRadius: 18, border: `1px solid ${C.stone200}` }}>{url}</div>
      </div>
      <div style={{ position: 'relative', width: VIEW.w, height: VIEW.h, direction: 'rtl', fontFamily: BODY, color: C.stone800 }}>{children}</div>
    </div>
  );
}

/* ---------- camera: zoom/pan the browser toward a focus point in viewport coords ---------- */

export type CamKey = [frame: number, x: number, y: number, scale: number];

export function Camera({ keys, children }: { keys: CamKey[]; children: ReactNode }) {
  const f = useCurrentFrame();
  const s = track(f, keys.map((k) => [k[0], k[3]]));
  const fx = VIEW.x + track(f, keys.map((k) => [k[0], k[1]]));
  const fy = VIEW.y + track(f, keys.map((k) => [k[0], k[2]]));
  return (
    <div style={{ position: 'absolute', inset: 0, transformOrigin: '0 0', transform: `translate(${960 - fx * s}px, ${540 - fy * s}px) scale(${s})` }}>
      {children}
    </div>
  );
}

/** Neutral camera focus: viewport point that sits at canvas center when scale = 1. */
export const CAM_HOME = { x: 960 - VIEW.x, y: 540 - VIEW.y };

/* ---------- cursor, in viewport coords; place inside the BrowserFrame's viewport ---------- */

export function Cursor({ path, clicks, appear = 0 }: { path: [number, number, number][]; clicks: number[]; appear?: number }) {
  const f = useCurrentFrame();
  const x = track(f, path.map((p) => [p[0], p[1]]));
  const y = track(f, path.map((p) => [p[0], p[2]]));
  const active = clicks.find((c) => f >= c && f < c + 16);
  const dip = clicks.reduce((m, c) => Math.min(m, press(f, c)), 1);
  return (
    <div style={{ position: 'absolute', left: 0, top: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 100, opacity: fadeIn(f, appear, 8) }}>
      {active !== undefined ? (
        <div
          style={{
            position: 'absolute',
            left: x - 30,
            top: y - 30,
            width: 60,
            height: 60,
            borderRadius: '50%',
            border: `3px solid ${C.clay500}`,
            opacity: interpolate(f - active, [0, 16], [0.9, 0]),
            transform: `scale(${interpolate(f - active, [0, 16], [0.3, 1.3])})`,
          }}
        />
      ) : null}
      <svg width="34" height="34" viewBox="0 0 24 24" style={{ position: 'absolute', left: x - 6, top: y - 3, transform: `scale(${dip})`, filter: 'drop-shadow(0 3px 4px rgba(0,0,0,.25))' }}>
        <path d="M5 3l14 8-6.5 1.5L9 19z" fill={C.stone900} stroke="#fff" strokeWidth="1.5" strokeLinejoin="round" />
      </svg>
    </div>
  );
}

/* ---------- caption bar, canvas-level ---------- */

export function Caption({ text, from, to }: { text: string; from: number; to: number }) {
  const f = useCurrentFrame();
  if (f < from || f > to) return null;
  const o = fade(f, from, to, 10);
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, bottom: 38, display: 'flex', justifyContent: 'center', opacity: o, transform: `translateY(${(1 - o) * 12}px)`, zIndex: 200 }}>
      <div
        style={{
          direction: 'rtl',
          fontFamily: BODY,
          fontWeight: 600,
          fontSize: 38,
          color: C.stone50,
          background: 'rgba(27,25,23,.86)',
          padding: '14px 34px',
          borderRadius: 999,
          boxShadow: '0 10px 30px rgba(0,0,0,.2)',
        }}
      >
        {text}
      </div>
    </div>
  );
}

export function Button({ children, style, scale = 1, variant = 'primary' }: { children: ReactNode; style?: CSSProperties; scale?: number; variant?: 'primary' | 'ghost' | 'dark' }) {
  const v = {
    primary: { background: C.clay500, color: '#fff', border: `1px solid ${C.clay500}` },
    ghost: { background: 'transparent', color: C.stone800, border: `1px solid ${C.stone300}` },
    dark: { background: C.stone900, color: '#fff', border: `1px solid ${C.stone900}` },
  }[variant];
  return (
    <div
      style={{
        position: 'absolute',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 10,
        fontWeight: 600,
        fontSize: 18,
        borderRadius: 4,
        transform: `scale(${scale})`,
        ...v,
        ...style,
      }}
    >
      {children}
    </div>
  );
}
