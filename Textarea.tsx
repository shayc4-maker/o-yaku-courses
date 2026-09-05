import { useId, useState, type CSSProperties, type ReactNode, type TextareaHTMLAttributes } from 'react';

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: ReactNode;
  hint?: ReactNode;
  error?: ReactNode;
  wrapperStyle?: CSSProperties;
}

export function Textarea({ label, hint, error, rows = 4, id, style, wrapperStyle, ...rest }: TextareaProps) {
  const [focus, setFocus] = useState(false);
  const generatedId = useId();
  const inputId = id || generatedId;
  const border = error ? 'var(--clay-500)' : focus ? 'var(--stone-900)' : 'var(--line-strong)';
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', ...wrapperStyle }}>
      {label ? (
        <label htmlFor={inputId} style={{ fontSize: 'var(--text-xs)', fontWeight: 'var(--weight-semibold)', letterSpacing: '0.04em', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
          {label}
        </label>
      ) : null}
      <textarea
        id={inputId}
        rows={rows}
        onFocus={() => setFocus(true)}
        onBlur={() => setFocus(false)}
        style={{
          border: '1px solid ' + border,
          borderRadius: 'var(--radius-control)',
          background: 'var(--surface-card)',
          padding: 'var(--space-4) var(--space-5)',
          outline: 'none',
          resize: 'vertical',
          fontFamily: 'var(--font-body)',
          fontSize: 'var(--text-sm)',
          lineHeight: 'var(--leading-normal)',
          color: 'var(--text-body)',
          boxShadow: focus ? 'var(--focus-ring)' : 'none',
          transition: 'var(--transition-control)',
          ...style,
        }}
        {...rest}
      />
      {error || hint ? (
        <span style={{ fontSize: 'var(--text-2xs)', color: error ? 'var(--status-danger-fg)' : 'var(--text-muted)' }}>{error || hint}</span>
      ) : null}
    </div>
  );
}
