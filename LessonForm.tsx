import type { CSSProperties } from 'react';
import { Input, Select, Textarea } from '../../ds';
import { LESSON_TYPES, type Lesson } from '../../data/studio';

type Draft = Omit<Lesson, 'id'> & { id?: number };

const num: CSSProperties = { direction: 'ltr', textAlign: 'right', fontVariantNumeric: 'tabular-nums' };

export function LessonForm({ value, onChange }: { value: Draft; onChange: (v: Draft) => void }) {
  const set = (k: keyof Draft) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    onChange({ ...value, [k]: e.target.value });
  const setNum = (k: keyof Draft) => (e: React.ChangeEvent<HTMLInputElement>) =>
    onChange({ ...value, [k]: Math.max(0, +e.target.value.replace(/\D/g, '') || 0) });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
      <Input label="שם השיעור" value={value.title} onChange={set('title')} placeholder="סדנת חיווט" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(140px,1fr))', gap: 'var(--space-4)' }}>
        <Input label="תאריך" type="date" value={value.date} onChange={set('date')} style={num} />
        <Input label="שעה" type="time" value={value.time} onChange={set('time')} style={num} />
      </div>
      <Select label="סוג" options={LESSON_TYPES} value={value.type} onChange={set('type')} />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(110px,1fr))', gap: 'var(--space-4)' }}>
        <Input label="מינימום נרשמים" value={value.min} onChange={setNum('min')} style={num} hint="לפתיחת השיעור" />
        <Input label="מקסימום" value={value.max} onChange={setNum('max')} style={num} />
        <Input label="נרשמים כעת" value={value.enrolled} onChange={setNum('enrolled')} style={num} />
      </div>
      <Textarea label="פרטים" value={value.notes} onChange={set('notes')} rows={3} placeholder="מה מביאים, משך, מה כלול" />
    </div>
  );
}
