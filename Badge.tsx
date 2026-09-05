import type { CSSProperties, HTMLAttributes, ReactNode } from 'react';

export type BadgeTone = 'neutral' | 'brand' | 'success' | 'warning' | 'danger' | 'info';

const tones: Record<BadgeTone, CSSProperties> = {
  neutral: { color: 'var(--text-muted)', background: 'var(--surface-sunken)' },
  brand: { color: 'var(--clay-700)', background: 'var(--clay-50)' },
  success: { color: 'var(--status-success-fg)', background: 'var(--status-success-bg)' },
  warning: { color: 'var(--status-warning-fg)', background: 'var(--status-warning-bg)' },
  danger: { color: 'var(--status-danger-fg)', background: 'var(--status-danger-bg)' },
  info: { color: 'var(--status-info-fg)', background: 'var(--status-info-bg)' },
};

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  children?: ReactNode;
  tone?: BadgeTone;
  dot?: boolean;
}

export function Badge({ children, tone = 'neutral', dot = false, style, ...rest }: BadgeProps) {
  const t = tones[tone] || tones.neutral;
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 'var(--space-2)',
        fontFamily: 'var(--font-body)',
        fontSize: 'var(--text-3xs)',
        fontWeight: 'var(--weight-semibold)',
        letterSpacing: 'var(--tracking-wide)',
        textTransform: 'uppercase',
        padding: '4px var(--space-3)',
        borderRadius: 'var(--radius-xs)',
        lineHeight: 1.2,
        ...t,
        ...style,
      }}
      {...rest}
    >
      {dot ? (
        <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'currentColor' }} />
      ) : null}
      {children}
    </span>
  );
}
