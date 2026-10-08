import { interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { BrowserFrame, Camera, CAM_HOME, fadeIn, Icon } from '../components';
import type { ExplainerProps } from '../content';
import { C, DISPLAY } from '../theme';

/** Frames before the clip starts playing inside the Patreon page (page settles in). */
export const CLIP_LEAD = 30;
/** Frames after the clip before the scene hands over to the outro. */
export const CLIP_TAIL = 30;

const PLAYER = { left: 200, top: 36, w: 1200, h: 675 };

/** Patreon post page with the live clip — or a placeholder until the clip file is set. */
export function PatreonClip({ live, timestamp }: { live: ExplainerProps['live']; timestamp: string }) {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clipFrames = Math.round(live.clipSeconds * fps);
  const t = Math.max(0, f - CLIP_LEAD) / fps; // seconds into the clip
  const playing = f >= CLIP_LEAD && f < CLIP_LEAD + clipFrames;
  const sub = live.subtitles.find(([a, b]) => playing && t >= a && t < b);
  const enter = interpolate(f, [0, 20], [1.08, 1], { extrapolateRight: 'clamp' });
  const playerCenterY = PLAYER.top + PLAYER.h / 2;

  return (
    <div style={{ position: 'absolute', inset: 0, transform: `scale(${enter})` }}>
      <Camera
        keys={[
          [0, CAM_HOME.x, CAM_HOME.y, 1],
          [CLIP_LEAD, CAM_HOME.x, playerCenterY + 40, 1.08],
          [CLIP_LEAD + clipFrames, CAM_HOME.x, playerCenterY, 1.2],
        ]}
      >
        <BrowserFrame url={live.postUrl} tab="Patreon" page="#FFFFFF">
          {/* player */}
          <div style={{ position: 'absolute', left: PLAYER.left, top: PLAYER.top, width: PLAYER.w, height: PLAYER.h, background: C.stone900, borderRadius: 8, overflow: 'hidden' }}>
            {live.clipFile ? (
              <Sequence from={CLIP_LEAD} durationInFrames={clipFrames}>
                <OffthreadVideo src={staticFile(live.clipFile)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </Sequence>
            ) : (
              <Placeholder f={f} timestamp={timestamp} />
            )}

            {/* play state overlay before start */}
            {f < CLIP_LEAD ? (
              <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,.35)' }}>
                <div style={{ width: 96, height: 96, borderRadius: '50%', background: 'rgba(255,255,255,.92)', display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${interpolate(f, [CLIP_LEAD - 8, CLIP_LEAD], [1, 0.85], { extrapolateLeft: 'clamp' })})` }}>
                  <Icon name="play" size={40} color={C.stone900} style={{ marginLeft: 6 }} />
                </div>
              </div>
            ) : null}

            {/* subtitles: part of the spoken answer */}
            {sub ? (
              <div style={{ position: 'absolute', left: 0, right: 0, bottom: 74, display: 'flex', justifyContent: 'center' }}>
                <span style={{ direction: 'rtl', fontSize: 34, fontWeight: 600, color: '#fff', background: 'rgba(0,0,0,.62)', padding: '8px 22px', borderRadius: 6 }}>{sub[2]}</span>
              </div>
            ) : null}

            {/* controls */}
            <Controls f={f} clipFrames={clipFrames} timestamp={timestamp} fps={fps} />
          </div>

          {/* post meta under the player */}
          <div style={{ position: 'absolute', right: PLAYER.left, top: PLAYER.top + PLAYER.h + 28, display: 'flex', alignItems: 'center', gap: 18, opacity: fadeIn(f, 6, 12) }}>
            <div style={{ width: 54, height: 54, borderRadius: '50%', background: C.stone100, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <span style={{ width: 22, height: 22, borderRadius: '50%', border: `3px solid ${C.clay500}` }} />
            </div>
            <div>
              <div style={{ fontFamily: DISPLAY, fontSize: 30, color: C.stone900 }}>{live.postTitle}</div>
              <div style={{ fontSize: 17, color: C.stone500, marginTop: 2 }}>O-YAKU · פוסט למנויים · מתחיל מ-{timestamp}</div>
            </div>
          </div>
        </BrowserFrame>
      </Camera>
    </div>
  );
}

function Placeholder({ f, timestamp }: { f: number; timestamp: string }) {
  const drift = f * 0.4;
  return (
    <div style={{ position: 'absolute', inset: 0, background: `linear-gradient(${120 + drift * 0.2}deg, #3a3631, #1f1d1a 55%, #4a3a33)`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 14 }}>
      <div style={{ fontSize: 15, letterSpacing: '.22em', color: 'rgba(255,255,255,.45)', fontWeight: 700 }}>PLACEHOLDER</div>
      <div style={{ fontFamily: DISPLAY, fontSize: 44, color: 'rgba(255,255,255,.88)' }}>כאן ייכנס קטע הלייב</div>
      <div style={{ fontSize: 20, color: 'rgba(255,255,255,.55)' }}>החל מ-{timestamp} · מגדירים את הקובץ ב-content.ts</div>
    </div>
  );
}

function toSeconds(ts: string) {
  return ts.split(':').reduce((acc, p) => acc * 60 + Number(p), 0);
}
function fmt(sec: number) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${String(s).padStart(2, '0')}`;
}

function Controls({ f, clipFrames, timestamp, fps }: { f: number; clipFrames: number; timestamp: string; fps: number }) {
  const total = 58 * 60 + 12; // nominal live length, only for the progress bar
  const start = toSeconds(timestamp);
  const now = start + Math.min(Math.max(0, f - CLIP_LEAD), clipFrames) / fps;
  const pct = (now / total) * 100;
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: 56, background: 'linear-gradient(transparent, rgba(0,0,0,.6))', direction: 'ltr', display: 'flex', alignItems: 'center', gap: 16, padding: '0 22px' }}>
      <Icon name="play" size={18} color="#fff" />
      <span style={{ color: '#fff', fontSize: 15, fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
        {fmt(now)} / {fmt(total)}
      </span>
      <div style={{ flex: 1, height: 5, background: 'rgba(255,255,255,.25)', borderRadius: 3, position: 'relative' }}>
        <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${pct}%`, background: C.clay500, borderRadius: 3 }} />
        <div style={{ position: 'absolute', left: `${(start / total) * 100}%`, top: -5, width: 3, height: 15, background: '#fff', borderRadius: 2 }} />
      </div>
    </div>
  );
}
