import { useState, type ButtonHTMLAttributes, type CSSProperties, type ReactNode } from 'react';

export type IconButtonVariant = 'ghost' | 'outline' | 'solid';
export type IconButtonSize = 'sm' | 'md' | 'lg';

const sizes: Record<IconButtonSize, number> = { sm: 30, md: 38, lg: 44 };

export interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: ReactNode;
  label: string;
  variant?: IconButtonVariant;
  size?: IconButtonSize;
}

export function IconButton({
  icon,
  label,
  variant = 'ghost',
  size = 'md',
  disabled = false,
  style,
  ...rest
}: IconButtonProps) {
  const [hover, setHover] = useState(false);
  const box = sizes[size] || sizes.md;
  const skins: Record<IconButtonVariant, CSSProperties> = {
    ghost: { background: hover ? 'var(--surface-sunken)' : 'transparent', color: 'var(--text-heading)', borderColor: 'transparent' },
    outline: { background: hover ? 'var(--surface-sunken)' : 'transparent', color: 'var(--text-heading)', borderColor: 'var(--line-strong)' },
    solid: { background: hover ? 'var(--clay-600)' : 'var(--clay-500)', color: '#fff', borderColor: 'transparent' },
  };
  return (
    <button
      aria-label={label}
      title={label}
      disabled={disabled}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        width: box,
        height: box,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        border: '1px solid',
        borderRadius: 'var(--radius-control)',
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'var(--transition-control)',
        opacity: disabled ? 0.4 : 1,
        ...(skins[variant] || skins.ghost),
        ...style,
      }}
      {...rest}
    >
      {icon}
    </button>
  );
}
