import { useState, type HTMLAttributes, type MouseEventHandler, type ReactNode } from 'react';

export interface TagProps extends HTMLAttributes<HTMLSpanElement> {
  children?: ReactNode;
  selected?: boolean;
  onRemove?: MouseEventHandler<HTMLButtonElement>;
  onClick?: MouseEventHandler<HTMLSpanElement>;
}

export function Tag({ children, selected = false, onRemove, onClick, style, ...rest }: TagProps) {
  const [hover, setHover] = useState(false);
  const interactive = !!onClick;
  return (
    <span
      onClick={onClick}
      role={interactive ? 'button' : undefined}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 'var(--space-3)',
        fontFamily: 'var(--font-body)',
        fontSize: 'var(--text-xs)',
        letterSpacing: '0.02em',
        padding: '5px var(--space-4)',
        borderRadius: 'var(--radius-pill)',
        border: '1px solid ' + (selected ? 'var(--clay-500)' : 'var(--line-strong)'),
        background: selected ? 'var(--clay-50)' : hover && interactive ? 'var(--surface-sunken)' : 'transparent',
        color: selected ? 'var(--clay-700)' : 'var(--text-body)',
        cursor: interactive ? 'pointer' : 'default',
        transition: 'var(--transition-control)',
        ...style,
      }}
      {...rest}
    >
      {children}
      {onRemove ? (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove(e);
          }}
          aria-label="הסרה"
          style={{ border: 0, background: 'none', padding: 0, cursor: 'pointer', color: 'inherit', opacity: 0.6, display: 'flex' }}
        >
          <svg width="10" height="10" viewBox="0 0 10 10" stroke="currentColor" strokeWidth="1.2">
            <path d="M1 1l8 8M9 1l-8 8" />
          </svg>
        </button>
      ) : null}
    </span>
  );
}
