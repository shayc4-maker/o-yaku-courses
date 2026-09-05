import type { CSSProperties, HTMLAttributes, ReactNode } from 'react';

export interface TabItem {
  value: string;
  label: ReactNode;
}

export type TabsVariant = 'underline' | 'pill';

export interface TabsProps extends HTMLAttributes<HTMLDivElement> {
  items?: (TabItem | string)[];
  value?: string;
  onChange?: (value: string) => void;
  variant?: TabsVariant;
}

export function Tabs({ items = [], value, onChange, variant = 'underline', style, ...rest }: TabsProps) {
  const first = items[0];
  const firstValue = first ? (typeof first === 'string' ? first : first.value) : undefined;
  const active = value ?? firstValue;
  return (
    <div
      role="tablist"
      style={{
        display: 'flex',
        gap: variant === 'underline' ? 'var(--space-8)' : 'var(--space-1)',
        borderBottom: variant === 'underline' ? '1px solid var(--line-hairline)' : 'none',
        ...style,
      }}
      {...rest}
    >
      {items.map((raw) => {
        const it: TabItem = typeof raw === 'string' ? { value: raw, label: raw } : raw;
        const on = it.value === active;
        const shared: CSSProperties = {
          fontFamily: 'var(--font-body)',
          fontSize: 'var(--text-sm)',
          letterSpacing: '0.02em',
          border: 0,
          background: 'none',
          cursor: 'pointer',
          transition: 'var(--transition-control)',
        };
        return (
          <button
            key={it.value}
            role="tab"
            aria-selected={on}
            onClick={() => onChange?.(it.value)}
            style={
              variant === 'underline'
                ? {
                    ...shared,
                    padding: '0 0 var(--space-4)',
                    marginBottom: -1,
                    color: on ? 'var(--text-heading)' : 'var(--text-muted)',
                    fontWeight: on ? 'var(--weight-semibold)' : 'var(--weight-regular)',
                    borderBottom: '1px solid ' + (on ? 'var(--clay-500)' : 'transparent'),
                  }
                : {
                    ...shared,
                    padding: 'var(--space-3) var(--space-5)',
                    borderRadius: 'var(--radius-control)',
                    background: on ? 'var(--surface-card)' : 'transparent',
                    boxShadow: on ? 'var(--shadow-hairline)' : 'none',
                    color: on ? 'var(--text-heading)' : 'var(--text-muted)',
                  }
            }
          >
            {it.label}
          </button>
        );
      })}
    </div>
  );
}
