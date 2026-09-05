import type { CSSProperties } from 'react';
import { EYE } from '../chrome/constants';
import { FRONT_LINES, PATHS } from '../../data/ceramics';

function ShapeSvg({ d, w, h }: { d: string; w: number; h: number }) {
  return (
    <svg width={w} height={h} viewBox="0 0 100 100" preserveAspectRatio="none" style={{ display: 'block' }}>
      <path d={d} fill="var(--clay-50)" stroke="var(--clay-600)" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
      <path d={d} fill="none" stroke="var(--clay-300)" strokeWidth="1" vectorEffect="non-scaling-stroke" transform="translate(10 10) scale(.8)" />
    </svg>
  );
}

export function PotPreview({ shape, L, W, H }: { shape: string; L: number; W: number; H: number }) {
  const box = 150;
  const maxD = Math.max(L, W, 1);
  const sx = (L / maxD) * box;
  const sy = (W / maxD) * box;
  const r = shape === 'round' || shape === 'oval' ? '50%' : 4;
  const isRound = shape === 'round' || shape === 'hex' || shape === 'oct';
  const tw = isRound ? Math.min(sx, sy) : sx;
  const th = isRound ? Math.min(sx, sy) : sy;
  const sh = Math.min(Math.max((H / maxD) * box, 14), 120);
  const pane: CSSProperties = { minWidth: 0, background: 'var(--surface-card)', border: '1px solid var(--line-hairline)', borderRadius: 'var(--radius-card)', padding: 'var(--space-5)', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' };
  const stage: CSSProperties = { height: 190, display: 'flex', alignItems: 'center', justifyContent: 'center' };
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) minmax(0,1fr)', gap: 'var(--space-4)' }}>
      <div style={pane}>
        <span style={EYE}>מבט־על</span>
        <div style={stage}>
          {PATHS[shape] ? (
            <ShapeSvg d={PATHS[shape]} w={tw} h={th} />
          ) : (
            <div style={{ width: tw, height: th, border: '1.5px solid var(--clay-600)', borderRadius: r, background: 'var(--clay-50)', boxShadow: 'inset 0 0 0 10px var(--surface-card), inset 0 0 0 11px var(--clay-300)' }} />
          )}
        </div>
      </div>
      <div style={pane}>
        <span style={EYE}>מבט חזית</span>
        <div style={stage}>
          <svg width={tw} height={sh} viewBox="0 0 100 100" preserveAspectRatio="none" style={{ display: 'block', overflow: 'visible' }}>
            <path d="M0 0 L100 0 L92 100 L8 100 Z" fill="var(--clay-50)" stroke="var(--clay-600)" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
            {(FRONT_LINES[shape] || []).map((x) => (
              <line key={x} x1={x} y1="0" x2={50 + (x - 50) * 0.84} y2="100" stroke="var(--clay-300)" strokeWidth="1" vectorEffect="non-scaling-stroke" />
            ))}
          </svg>
        </div>
      </div>
    </div>
  );
}
