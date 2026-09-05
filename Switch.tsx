import type { InputHTMLAttributes, ReactNode } from 'react';

export interface SwitchProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: ReactNode;
  checked?: boolean;
}

export function Switch({ label, checked, onChange, disabled = false, style, ...rest }: SwitchProps) {
  return (
    <label style={{ display: 'inline-flex', alignItems: 'center', gap: 'var(--space-4)', cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.45 : 1, ...style }}>
      <span
        style={{
          width: 38,
          height: 22,
          borderRadius: 'var(--radius-pill)',
          flex: 'none',
          position: 'relative',
          background: checked ? 'var(--clay-500)' : 'var(--stone-300)',
          transition: 'background-color var(--duration-base) var(--ease-standard)',
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
        <span
          style={{
            position: 'absolute',
            top: 3,
            left: checked ? 19 : 3,
            width: 16,
            height: 16,
            borderRadius: '50%',
            background: '#fff',
            transition: 'left var(--duration-base) var(--ease-out)',
          }}
        />
      </span>
      {label ? <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-body)' }}>{label}</span> : null}
    </label>
  );
}
