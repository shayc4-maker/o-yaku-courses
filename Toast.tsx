import type { HTMLAttributes, ReactNode } from 'react';

export type ToastTone = 'neutral' | 'success' | 'danger';

const tones: Record<ToastTone, string> = {
  neutral: 'var(--stone-900)',
  success: 'var(--moss-700)',
  danger: 'var(--clay-600)',
};

export interface ToastProps extends HTMLAttributes<HTMLDivElement> {
  children?: ReactNode;
  tone?: ToastTone;
  icon?: ReactNode;
  onDismiss?: () => void;
  title?: ReactNode;
  description?: ReactNode;
}

export function Toast({ children, tone = 'neutral', icon, onDismiss, title, description, style, ...rest }: ToastProps) {
  return (
    <div
      role="status"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 'var(--space-5)',
        background: tones[tone] || tones.neutral,
        color: 'var(--text-inverse)',
        borderRadius: 'var(--radius-control)',
        padding: 'var(--space-4) var(--space-6)',
        fontSize: 'var(--text-sm)',
        boxShadow: 'var(--shadow-overlay)',
        maxWidth: 420,
        ...style,
      }}
      {...rest}
    >
      {icon}
      <span style={{ flex: 1 }}>
        {title ? <div style={{ fontWeight: 600 }}>{title}</div> : null}
        {description ? <div style={{ opacity: 0.85, fontSize: 'var(--text-xs)' }}>{description}</div> : null}
        {children}
      </span>
      {onDismiss ? (
        <button
          onClick={onDismiss}
          aria-label="סגירה"
          style={{ border: 0, background: 'none', color: 'inherit', opacity: 0.65, cursor: 'pointer', display: 'flex', padding: 0 }}
        >
          <svg width="12" height="12" viewBox="0 0 12 12" stroke="currentColor" strokeWidth="1.3">
            <path d="M1 1l10 10M11 1L1 11" />
          </svg>
        </button>
      ) : null}
    </div>
  );
}
