import { useId, useState, type CSSProperties, type InputHTMLAttributes, type ReactNode } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: ReactNode;
  hint?: ReactNode;
  error?: ReactNode;
  prefix?: ReactNode;
  suffix?: ReactNode;
  wrapperStyle?: CSSProperties;
}

export function Input({ label, hint, error, prefix, suffix, id, style, wrapperStyle, ...rest }: InputProps) {
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
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-4)',
          border: '1px solid ' + border,
          borderRadius: 'var(--radius-control)',
          background: 'var(--surface-card)',
          padding: '0 var(--space-5)',
          height: 42,
          boxShadow: focus ? 'var(--focus-ring)' : 'none',
          transition: 'var(--transition-control),box-shadow var(--duration-fast) var(--ease-standard)',
        }}
      >
        {prefix ? <span style={{ color: 'var(--text-subtle)', display: 'flex' }}>{prefix}</span> : null}
        <input
          id={inputId}
          onFocus={() => setFocus(true)}
          onBlur={() => setFocus(false)}
          style={{
            flex: 1,
            minWidth: 0,
            border: 0,
            outline: 'none',
            background: 'transparent',
            fontFamily: 'var(--font-body)',
            fontSize: 'var(--text-sm)',
            color: 'var(--text-body)',
            height: '100%',
            ...style,
          }}
          {...rest}
        />
        {suffix ? <span style={{ color: 'var(--text-subtle)', display: 'flex' }}>{suffix}</span> : null}
      </div>
      {error || hint ? (
        <span style={{ fontSize: 'var(--text-2xs)', color: error ? 'var(--status-danger-fg)' : 'var(--text-muted)' }}>{error || hint}</span>
      ) : null}
    </div>
  );
}
