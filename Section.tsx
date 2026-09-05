import type { CSSProperties, ReactNode } from 'react';
import { useMobile } from '../../lib/useMobile';
import { EYE, WRAP } from './constants';

export interface SectionProps {
  eyebrow?: ReactNode;
  title?: ReactNode;
  lede?: ReactNode;
  action?: ReactNode;
  children?: ReactNode;
  style?: CSSProperties;
  narrow?: boolean;
}

export function Section({ eyebrow, title, lede, action, children, style, narrow }: SectionProps) {
  const mobile = useMobile();
  return (
    <section
      className="oy-wrap"
      style={{
        ...WRAP,
        maxWidth: narrow ? 'var(--container-narrow)' : 'var(--container-max)',
        marginTop: mobile ? 'var(--space-10)' : 'var(--space-12)',
        ...style,
      }}
    >
      {title || eyebrow ? (
        <div
          style={{
            display: 'flex',
            alignItems: mobile ? 'flex-start' : 'flex-end',
            flexDirection: mobile ? 'column' : 'row',
            gap: mobile ? 'var(--space-4)' : 'var(--space-7)',
            marginBottom: 'var(--space-8)',
          }}
        >
          <div>
            {eyebrow ? <div style={EYE}>{eyebrow}</div> : null}
            {title ? <h2 style={{ fontSize: 'var(--text-2xl)', fontWeight: 300, marginTop: 8 }}>{title}</h2> : null}
            {lede ? <p style={{ marginTop: 'var(--space-4)', color: 'var(--text-muted)', maxWidth: '58ch' }}>{lede}</p> : null}
          </div>
          {mobile ? null : <span style={{ flex: 1 }} />}
          {action}
        </div>
      ) : null}
      {children}
    </section>
  );
}
