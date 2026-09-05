import { useEffect, useState } from 'react';
import { IconButton, Icon } from '../../ds';
import { useMobile } from '../../lib/useMobile';
import type { Navigate, PageId } from '../../types/route';
import { NAV, WRAP } from './constants';
import { Logo } from './Logo';

export function SiteHeader({ page, onNavigate }: { page: PageId; onNavigate: Navigate }) {
  const mobile = useMobile();
  const [open, setOpen] = useState(false);
  useEffect(() => {
    setOpen(false);
  }, [page]);
  const go = (id: PageId) => (e: React.MouseEvent) => {
    e.preventDefault();
    setOpen(false);
    onNavigate(id);
  };
  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 30,
        background: 'rgba(251,249,246,.88)',
        backdropFilter: 'saturate(120%) blur(10px)',
        borderBottom: '1px solid var(--line-hairline)',
      }}
    >
      <div className="oy-wrap" style={{ ...WRAP, height: mobile ? 64 : 78, display: 'flex', alignItems: 'center', gap: 'var(--space-9)' }}>
        <a href="#" onClick={go('home')} style={{ display: 'flex', alignItems: 'center', border: 0 }}>
          <Logo height={mobile ? 32 : 40} />
        </a>
        {mobile ? null : (
          <nav style={{ display: 'flex', gap: 'var(--space-7)' }}>
            {NAV.map((n) => (
              <a
                key={n.id}
                href="#"
                onClick={go(n.id)}
                style={{
                  fontSize: 'var(--text-sm)',
                  fontWeight: 600,
                  border: 0,
                  paddingBottom: 3,
                  color: page === n.id ? 'var(--text-heading)' : 'var(--text-muted)',
                  borderBottom: '1px solid ' + (page === n.id ? 'var(--clay-500)' : 'transparent'),
                }}
              >
                {n.label}
              </a>
            ))}
          </nav>
        )}
        <span style={{ flex: 1 }} />
        {mobile ? (
          <IconButton
            icon={<Icon name={open ? 'x' : 'menu'} size={18} />}
            label={open ? 'סגירת תפריט' : 'תפריט'}
            variant="ghost"
            onClick={() => setOpen(!open)}
          />
        ) : null}
      </div>
      {mobile && open ? (
        <nav style={{ borderTop: '1px solid var(--line-hairline)', background: 'var(--surface-page)', display: 'flex', flexDirection: 'column', padding: 'var(--space-3) var(--gutter-page)' }}>
          {NAV.map((n) => (
            <a
              key={n.id}
              href="#"
              onClick={go(n.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                minHeight: 48,
                padding: '0 var(--space-2)',
                fontSize: 'var(--text-md)',
                fontWeight: 600,
                border: 0,
                borderBottom: '1px solid var(--line-hairline)',
                color: page === n.id ? 'var(--text-brand)' : 'var(--text-heading)',
              }}
            >
              {n.label}
            </a>
          ))}
        </nav>
      ) : null}
    </header>
  );
}
