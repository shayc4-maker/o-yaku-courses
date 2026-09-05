import type { InputHTMLAttributes, ReactNode } from 'react';

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: ReactNode;
  description?: ReactNode;
  checked?: boolean;
}

export function Checkbox({ label, description, checked, onChange, disabled = false, style, ...rest }: CheckboxProps) {
  return (
    <label style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'flex-start', cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.45 : 1, ...style }}>
      <span
        style={{
          width: 18,
          height: 18,
          flex: 'none',
          marginTop: 2,
          borderRadius: 'var(--radius-xs)',
          border: '1px solid ' + (checked ? 'var(--clay-500)' : 'var(--line-strong)'),
          background: checked ? 'var(--clay-500)' : 'var(--surface-card)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'var(--transition-control)',
          position: 'relative',
        }}
      >
        <input
          type="checkbox"
          checked={!!checked}
          onChange={onChange}
          disabled={disabled}
          style={{ position: 'absolute', opacity: 0, width: 0, height: 0 }}
          {...rest}
        />
        {checked ? (
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 6L9 17l-5-5" />
          </svg>
        ) : null}
      </span>
      <span style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <span style={{ fontSize: 'var(--text-sm)', lineHeight: 1.4, color: 'var(--text-body)' }}>{label}</span>
        {description ? <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)' }}>{description}</span> : null}
      </span>
    </label>
  );
}
