import type { ReactNode } from 'react';
import { Divider, Icon } from '../../ds';
import { useMobile } from '../../lib/useMobile';
import type { Navigate, PageId } from '../../types/route';
import { EYE, WRAP } from './constants';
import { Logo } from './Logo';

function FooterLink({ id, onNavigate, children }: { id: PageId; onNavigate: Navigate; children: ReactNode }) {
  return (
    <a
      href="#"
      onClick={(e) => {
        e.preventDefault();
        onNavigate(id);
      }}
      style={{ fontSize: 'var(--text-sm)', color: 'var(--stone-300)', border: 0 }}
    >
      {children}
    </a>
  );
}

export function SiteFooter({ onNavigate }: { onNavigate: Navigate }) {
  const mobile = useMobile();
  return (
    <footer style={{ background: 'var(--surface-inverse)', color: 'var(--text-inverse)', marginTop: 'var(--space-13)' }}>
      <div className="oy-wrap" style={{ ...WRAP, paddingTop: 'var(--space-11)', paddingBottom: 'var(--space-9)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: mobile ? '1fr 1fr' : '1.4fr 1fr 1fr 1fr', gap: 'var(--space-9)' }}>
          <div style={mobile ? { gridColumn: '1 / -1' } : undefined}>
            <Logo inverse height={48} />
            <p style={{ marginTop: 'var(--space-6)', fontSize: 'var(--text-sm)', lineHeight: 1.7, color: 'var(--stone-400)', maxWidth: '34ch' }}>
              בית ספר לבונסאי וסטודיו לקרמיקה. שי כהן, ירושלים.
            </p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <span style={{ ...EYE, color: 'var(--stone-500)' }}>לימוד</span>
            <FooterLink id="kb" onNavigate={onNavigate}>מאגר ידע</FooterLink>
            <FooterLink id="articles" onNavigate={onNavigate}>מאמרים</FooterLink>
            <FooterLink id="studio" onNavigate={onNavigate}>שיעורים בסטודיו</FooterLink>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <span style={{ ...EYE, color: 'var(--stone-500)' }}>הסטודיו</span>
            <FooterLink id="shop" onNavigate={onNavigate}>חנות</FooterLink>
            <FooterLink id="ceramics" onNavigate={onNavigate}>קרמיקה</FooterLink>
            <FooterLink id="about" onNavigate={onNavigate}>אודות</FooterLink>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <span style={{ ...EYE, color: 'var(--stone-500)' }}>קשר</span>
            <FooterLink id="contact" onNavigate={onNavigate}>צור קשר</FooterLink>
            <div style={{ display: 'flex', gap: 'var(--space-5)', marginTop: 'var(--space-2)', color: 'var(--stone-400)' }}>
              <Icon name="instagram" size={18} />
              <Icon name="youtube" size={18} />
              <Icon name="mail" size={18} />
            </div>
          </div>
        </div>
        <div style={{ marginTop: 'var(--space-9)' }}>
          <Divider tone="inverse" />
        </div>
        <div style={{ marginTop: 'var(--space-5)', fontSize: 'var(--text-2xs)', color: 'var(--stone-500)' }}>© 2026 O-Yaku · Shay Cohen</div>
      </div>
    </footer>
  );
}
