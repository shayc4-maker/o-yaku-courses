import { useId, useState, type CSSProperties, type ReactNode, type SelectHTMLAttributes } from 'react';

export interface SelectOption {
  value: string;
  label: ReactNode;
}

export interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'children'> {
  label?: ReactNode;
  hint?: ReactNode;
  error?: ReactNode;
  options?: (SelectOption | string)[];
  wrapperStyle?: CSSProperties;
}

export function Select({ label, hint, error, options = [], id, style, wrapperStyle, ...rest }: SelectProps) {
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
      <div style={{ position: 'relative' }}>
        <select
          id={inputId}
          onFocus={() => setFocus(true)}
          onBlur={() => setFocus(false)}
          style={{
            width: '100%',
            height: 42,
            appearance: 'none',
            WebkitAppearance: 'none',
            border: '1px solid ' + border,
            borderRadius: 'var(--radius-control)',
            background: 'var(--surface-card)',
            padding: '0 var(--space-9) 0 var(--space-5)',
            outline: 'none',
            fontFamily: 'var(--font-body)',
            fontSize: 'var(--text-sm)',
            color: 'var(--text-body)',
            boxShadow: focus ? 'var(--focus-ring)' : 'none',
            transition: 'var(--transition-control)',
            ...style,
          }}
          {...rest}
        >
          {options.map((o) => {
            const opt: SelectOption = typeof o === 'string' ? { value: o, label: o } : o;
            return (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            );
          })}
        </select>
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="var(--text-muted)"
          strokeWidth="1.5"
          strokeLinecap="round"
          style={{ position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }}
        >
          <path d="M6 9l6 6 6-6" />
        </svg>
      </div>
      {error || hint ? (
        <span style={{ fontSize: 'var(--text-2xs)', color: error ? 'var(--status-danger-fg)' : 'var(--text-muted)' }}>{error || hint}</span>
      ) : null}
    </div>
  );
}
