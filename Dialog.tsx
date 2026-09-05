import type { HTMLAttributes, MouseEventHandler, ReactNode } from 'react';

export interface DialogProps extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
  open?: boolean;
  title?: ReactNode;
  description?: ReactNode;
  children?: ReactNode;
  footer?: ReactNode;
  onClose?: MouseEventHandler<HTMLDivElement>;
  width?: number;
}

export function Dialog({ open = true, title, description, children, footer, onClose, width = 520, style, ...rest }: DialogProps) {
  if (!open) return null;
  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--overlay-scrim)',
        backdropFilter: 'var(--blur-scrim)',
        padding: 'var(--space-7)',
        zIndex: 50,
      }}
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
        style={{
          width,
          maxWidth: '100%',
          background: 'var(--surface-card)',
          borderRadius: 'var(--radius-card)',
          boxShadow: 'var(--shadow-overlay)',
          overflow: 'hidden',
          ...style,
        }}
        {...rest}
      >
        <div style={{ padding: 'var(--space-8) var(--space-8) var(--space-6)', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {title ? (
            <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-xl)', fontWeight: 'var(--weight-regular)', color: 'var(--text-heading)', margin: 0 }}>
              {title}
            </h3>
          ) : null}
          {description ? (
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', lineHeight: 'var(--leading-normal)', margin: 0 }}>{description}</p>
          ) : null}
          {children}
        </div>
        {footer ? (
          <div style={{ padding: 'var(--space-5) var(--space-8)', borderTop: '1px solid var(--line-hairline)', display: 'flex', gap: 'var(--space-4)', justifyContent: 'flex-end', background: 'var(--surface-page)' }}>
            {footer}
          </div>
        ) : null}
      </div>
    </div>
  );
}
