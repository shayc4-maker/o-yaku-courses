import { useState, type CSSProperties, type HTMLAttributes, type ReactNode } from 'react';

export type TooltipPlacement = 'top' | 'bottom' | 'left' | 'right';

export interface TooltipProps extends HTMLAttributes<HTMLSpanElement> {
  label: ReactNode;
  children?: ReactNode;
  placement?: TooltipPlacement;
}

export function Tooltip({ label, children, placement = 'top', style, ...rest }: TooltipProps) {
  const [show, setShow] = useState(false);
  const pos: Record<TooltipPlacement, CSSProperties> = {
    top: { bottom: '100%', left: '50%', transform: 'translate(-50%,-8px)' },
    bottom: { top: '100%', left: '50%', transform: 'translate(-50%,8px)' },
    left: { right: '100%', top: '50%', transform: 'translate(-8px,-50%)' },
    right: { left: '100%', top: '50%', transform: 'translate(8px,-50%)' },
  };
  return (
    <span
      style={{ position: 'relative', display: 'inline-flex', ...style }}
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
      onFocus={() => setShow(true)}
      onBlur={() => setShow(false)}
      {...rest}
    >
      {children}
      <span
        role="tooltip"
        style={{
          position: 'absolute',
          whiteSpace: 'nowrap',
          pointerEvents: 'none',
          background: 'var(--stone-900)',
          color: 'var(--text-inverse)',
          fontSize: 'var(--text-2xs)',
          letterSpacing: '0.02em',
          padding: '5px var(--space-4)',
          borderRadius: 'var(--radius-xs)',
          opacity: show ? 1 : 0,
          transition: 'opacity var(--duration-fast) var(--ease-standard)',
          zIndex: 40,
          ...pos[placement],
        }}
      >
        {label}
      </span>
    </span>
  );
}
