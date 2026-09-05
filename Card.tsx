import { useState, type CSSProperties, type HTMLAttributes, type ReactNode } from 'react';

export type CardTone = 'default' | 'sunken' | 'brand' | 'inverse';

const tones: Record<CardTone, CSSProperties> = {
  default: { background: 'var(--surface-card)', border: '1px solid var(--line-hairline)' },
  sunken: { background: 'var(--surface-sunken)', border: '1px solid transparent' },
  brand: { background: 'var(--surface-brand-soft)', border: '1px solid var(--clay-100)' },
  inverse: { background: 'var(--surface-inverse)', border: '1px solid transparent', color: 'var(--text-inverse)' },
};

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children?: ReactNode;
  media?: ReactNode;
  mediaHeight?: number;
  tone?: CardTone;
  padding?: string | number;
  interactive?: boolean;
}

export function Card({
  children,
  media,
  mediaHeight = 200,
  tone = 'default',
  padding = 'var(--space-7)',
  interactive = false,
  style,
  ...rest
}: CardProps) {
  const [hover, setHover] = useState(false);
  return (
    <div
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        borderRadius: 'var(--radius-card)',
        overflow: 'hidden',
        transition:
          'border-color var(--duration-base) var(--ease-standard),box-shadow var(--duration-base) var(--ease-standard)',
        ...(tones[tone] || tones.default),
        ...(interactive ? { cursor: 'pointer' } : {}),
        ...(interactive && hover ? { borderColor: 'var(--line-strong)', boxShadow: 'var(--shadow-raised)' } : {}),
        ...style,
      }}
      {...rest}
    >
      {media ? (
        <div style={{ height: mediaHeight, background: 'var(--stone-100)', overflow: 'hidden' }}>{media}</div>
      ) : null}
      <div style={{ padding }}>{children}</div>
    </div>
  );
}
