import { useState, type CSSProperties, type ElementType, type ReactNode, type ButtonHTMLAttributes } from 'react';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'quiet' | 'inverse';
export type ButtonSize = 'sm' | 'md' | 'lg';

const base: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 'var(--space-3)',
  fontFamily: 'var(--font-body)',
  fontWeight: 'var(--weight-semibold)',
  border: '1px solid transparent',
  borderRadius: 'var(--radius-control)',
  cursor: 'pointer',
  textDecoration: 'none',
  whiteSpace: 'nowrap',
  transition: 'var(--transition-control)',
  lineHeight: 1,
};

const sizes: Record<ButtonSize, CSSProperties> = {
  sm: { height: 32, padding: '0 var(--space-5)', fontSize: 'var(--text-xs)', letterSpacing: '0.04em' },
  md: { height: 40, padding: '0 var(--space-7)', fontSize: 'var(--text-sm)', letterSpacing: '0.03em' },
  lg: { height: 48, padding: '0 var(--space-8)', fontSize: 'var(--text-md)', letterSpacing: '0.02em' },
};

const variants: Record<ButtonVariant, CSSProperties> = {
  primary: { background: 'var(--clay-500)', color: '#fff' },
  secondary: { background: 'transparent', color: 'var(--text-heading)', borderColor: 'var(--line-strong)' },
  ghost: { background: 'transparent', color: 'var(--text-heading)' },
  quiet: { background: 'var(--surface-sunken)', color: 'var(--text-heading)' },
  inverse: { background: 'var(--stone-0)', color: 'var(--stone-900)' },
};

const hovers: Record<ButtonVariant, CSSProperties> = {
  primary: { background: 'var(--clay-600)' },
  secondary: { borderColor: 'var(--stone-900)' },
  ghost: { background: 'var(--surface-sunken)' },
  quiet: { background: 'var(--stone-200)' },
  inverse: { background: 'var(--stone-100)' },
};

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children?: ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: ReactNode;
  iconAfter?: ReactNode;
  fullWidth?: boolean;
  as?: ElementType;
  href?: string;
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  iconAfter,
  fullWidth = false,
  disabled = false,
  as = 'button',
  style,
  ...rest
}: ButtonProps) {
  const [hover, setHover] = useState(false);
  const Tag = as as ElementType;
  const s: CSSProperties = {
    ...base,
    ...(sizes[size] || sizes.md),
    ...(variants[variant] || variants.primary),
    ...(hover && !disabled ? hovers[variant] || {} : {}),
    ...(fullWidth ? { width: '100%' } : {}),
    ...(disabled ? { opacity: 0.4, cursor: 'not-allowed' } : {}),
    ...style,
  };
  return (
    <Tag
      style={s}
      disabled={Tag === 'button' ? disabled : undefined}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      {...rest}
    >
      {icon}
      {children}
      {iconAfter}
    </Tag>
  );
}
