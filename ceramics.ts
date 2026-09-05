export interface Award {
  year: string;
  where: string;
  title: string;
  text: string;
}

export const AWARDS: Award[] = [
  { year: '2025', where: 'יפן', title: 'פרס עידוד בתחרות Gafu-ten', text: 'כלי קרמיקה לבונסאי מאת שי כהן.' },
  { year: '2026', where: 'יפן', title: 'מקום שלישי בקטגוריית גלזורות', text: 'בתחרות Gafu-ten.' },
];

export interface GalleryItem {
  c: string;
  m: string;
  t: string;
}

export const GALLERY: GalleryItem[] = [
  { c: 'כלי גבוה מתוך סדרת הגלזורות', m: 'Gafu-ten · יפן · 2026', t: 'var(--stone-200)' },
  { c: 'כלי מלבני נמוך מתוך התצוגה', m: 'Gafu-ten · יפן · 2026', t: 'var(--moss-100)' },
  { c: 'כלי בגוון אדמדם מתוך התצוגה', m: 'Gafu-ten · יפן · 2026', t: 'var(--clay-50)' },
  { c: 'מבט רחב על אולם התחרות', m: 'Gafu-ten · יפן · 2026', t: 'var(--stone-100)' },
  { c: 'התצוגה הזוכה בקטגוריית הגלזורות', m: 'Gafu-ten · יפן · 2026', t: 'var(--stone-200)' },
  { c: 'כלי נמוך מתצוגת Gafu-ten 2025', m: 'Gafu-ten · יפן · 2025', t: 'var(--glaze-100)' },
  { c: 'שלושת הכלים ופרס העידוד', m: 'Gafu-ten · יפן · 2025', t: 'var(--ochre-100)' },
  { c: 'כלי גבוה מתצוגת Gafu-ten 2025', m: 'Gafu-ten · יפן · 2025', t: 'var(--stone-100)' },
  { c: 'תערוכת Trophy, בלגיה', m: 'Trophy · בלגיה · 2024', t: 'var(--stone-200)' },
];

export interface PotShape {
  value: string;
  label: string;
  k: number;
}

export const SHAPES: PotShape[] = [
  { value: 'rect', label: 'מלבן', k: 1 },
  { value: 'oval', label: 'אובאל', k: 1.05 },
  { value: 'round', label: 'עגול', k: 0.95 },
  { value: 'mokko', label: 'מוקו (Mokko)', k: 1.15 },
  { value: 'hex', label: 'משושה', k: 1.1 },
  { value: 'oct', label: 'מתומן', k: 1.1 },
];

export const PATHS: Record<string, string> = {
  mokko: 'M50 4 C66 4 74 12 76 22 C88 22 96 32 96 50 C96 68 88 78 76 78 C74 88 66 96 50 96 C34 96 26 88 24 78 C12 78 4 68 4 50 C4 32 12 22 24 22 C26 12 34 4 50 4 Z',
  hex: 'M25 2 L75 2 L98 50 L75 98 L25 98 L2 50 Z',
  oct: 'M29 2 L71 2 L98 29 L98 71 L71 98 L29 98 L2 71 L2 29 Z',
};

export const FRONT_LINES: Record<string, number[]> = { hex: [25, 75], oct: [29, 71], mokko: [24, 76] };
