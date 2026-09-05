import type { CSSProperties, HTMLAttributes, ReactNode } from 'react';

export type DividerOrientation = 'horizontal' | 'vertical';
export type DividerTone = 'hairline' | 'strong' | 'inverse';

export interface DividerProps extends HTMLAttributes<HTMLElement> {
  orientation?: DividerOrientation;
  label?: ReactNode;
  tone?: DividerTone;
}

export function Divider({ orientation = 'horizontal', label, tone = 'hairline', style, ...rest }: DividerProps) {
  const color =
    tone === 'strong' ? 'var(--line-strong)' : tone === 'inverse' ? 'var(--line-inverse)' : 'var(--line-hairline)';

  if (orientation === 'vertical') {
    return <span style={{ width: 1, alignSelf: 'stretch', background: color, ...style } as CSSProperties} {...rest} />;
  }

  if (label) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-5)', ...style }} {...rest}>
        <span style={{ height: 1, flex: 1, background: color }} />
        <span
          style={{
            fontSize: 'var(--text-2xs)',
            letterSpacing: 'var(--tracking-widest)',
            textTransform: 'uppercase',
            color: 'var(--text-muted)',
            fontWeight: 'var(--weight-semibold)',
          }}
        >
          {label}
        </span>
        <span style={{ height: 1, flex: 1, background: color }} />
      </div>
    );
  }

  return <hr style={{ border: 0, height: 1, background: color, margin: 0, ...style }} {...rest} />;
}
