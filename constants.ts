import type { CSSProperties } from 'react';
import type { PageId } from '../../types/route';

export const NAV: { id: PageId; label: string }[] = [
  { id: 'home', label: 'בית' },
  { id: 'kb', label: 'מאגר ידע' },
  { id: 'articles', label: 'מאמרים' },
  { id: 'studio', label: 'סטודיו' },
  { id: 'shop', label: 'חנות' },
  { id: 'ceramics', label: 'קרמיקה' },
  { id: 'about', label: 'אודות' },
  { id: 'contact', label: 'צור קשר' },
];

export const EYE: CSSProperties = {
  fontSize: 'var(--text-2xs)',
  letterSpacing: 'var(--tracking-widest)',
  textTransform: 'uppercase',
  fontWeight: 600,
  color: 'var(--text-muted)',
};

export const WRAP: CSSProperties = {
  maxWidth: 'var(--container-max)',
  margin: '0 auto',
  padding: '0 var(--gutter-page-lg)',
};
