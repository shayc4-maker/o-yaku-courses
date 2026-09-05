export const HE_DAYS = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ש'];

export interface LessonType {
  value: string;
  label: string;
}

export const LESSON_TYPES: LessonType[] = [
  { value: 'workshop', label: 'סדנה חד־פעמית' },
  { value: 'course', label: 'מפגש קורס' },
  { value: 'open', label: 'סטודיו פתוח' },
  { value: 'ceramics', label: 'קרמיקה' },
];

export interface Lesson {
  id: number;
  date: string;
  time: string;
  type: string;
  title: string;
  min: number;
  max: number;
  enrolled: number;
  notes: string;
}

// Client-side only — the studio calendar isn't wired to a backend yet (out of the approved
// live-data scope for this build; only home/kb/species read from Supabase). State resets on
// reload, same as the prototype.
export const SEED_LESSONS: Lesson[] = [
  { id: 1, date: '2026-09-08', time: '18:30', type: 'course', title: 'קורס יסודות · מפגש 3', min: 4, max: 8, enrolled: 7, notes: 'חיווט ראשון. להביא מזמרה וחוט 2.5.' },
  { id: 2, date: '2026-09-11', time: '10:00', type: 'open', title: 'סטודיו פתוח', min: 2, max: 10, enrolled: 3, notes: 'עבודה על העצים של התלמידים. פתיחת כבשן.' },
  { id: 3, date: '2026-09-15', time: '18:30', type: 'course', title: 'קורס יסודות · מפגש 4', min: 4, max: 8, enrolled: 8, notes: '' },
  { id: 4, date: '2026-09-18', time: '09:30', type: 'workshop', title: 'סדנת שתילה מחדש', min: 5, max: 8, enrolled: 2, notes: 'כולל מצע ורשת ניקוז. 4 שעות.' },
  { id: 5, date: '2026-09-25', time: '10:00', type: 'ceramics', title: 'בניית כלי ראשון', min: 4, max: 6, enrolled: 4, notes: 'חומר וגלזורה כלולים.' },
  { id: 6, date: '2026-10-02', time: '18:30', type: 'course', title: 'קורס יסודות · מפגש 5', min: 4, max: 8, enrolled: 8, notes: '' },
];

export const EMPTY_LESSON: Omit<Lesson, 'id'> = { date: '', time: '18:30', type: 'workshop', title: '', min: 4, max: 8, enrolled: 0, notes: '' };

export const pad2 = (n: number) => String(n).padStart(2, '0');
export const iso = (y: number, m: number, d: number) => `${y}-${pad2(m + 1)}-${pad2(d)}`;

export function lessonState(l: Lesson): { label: string; tone: 'neutral' | 'warning' | 'success' } {
  if (l.enrolled >= l.max) return { label: 'מלא', tone: 'neutral' };
  if (l.enrolled < l.min) return { label: `חסרים ${l.min - l.enrolled}`, tone: 'warning' };
  return { label: `נותרו ${l.max - l.enrolled}`, tone: 'success' };
}
