import type { InputHTMLAttributes, ReactNode } from 'react';

export interface RadioProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: ReactNode;
  description?: ReactNode;
  checked?: boolean;
}

export function Radio({ label, description, checked, onChange, name, value, disabled = false, style, ...rest }: RadioProps) {
  return (
    <label style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'flex-start', cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.45 : 1, ...style }}>
      <span
        style={{
          width: 18,
          height: 18,
          flex: 'none',
          marginTop: 2,
          borderRadius: '50%',
          border: '1px solid ' + (checked ? 'var(--clay-500)' : 'var(--line-strong)'),
          background: 'var(--surface-card)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'var(--transition-control)',
          position: 'relative',
        }}
      >
        <input
          type="radio"
          name={name}
          value={value}
          checked={!!checked}
          onChange={onChange}
          disabled={disabled}
          style={{ position: 'absolute', opacity: 0, width: 0, height: 0 }}
          {...rest}
        />
        {checked ? <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--clay-500)' }} /> : null}
      </span>
      <span style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <span style={{ fontSize: 'var(--text-sm)', lineHeight: 1.4, color: 'var(--text-body)' }}>{label}</span>
        {description ? <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)' }}>{description}</span> : null}
      </span>
    </label>
  );
}
