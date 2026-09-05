import { useEffect, useState } from 'react';
import { Badge, Button, Card, Dialog, Icon, IconButton, Toast } from '../ds';
import { EYE } from '../components/chrome/constants';
import { Section } from '../components/chrome/Section';
import { LessonForm } from '../components/studio/LessonForm';
import { useMobile } from '../lib/useMobile';
import { HE_MONTHS } from '../lib/data';
import { EMPTY_LESSON, HE_DAYS, LESSON_TYPES, SEED_LESSONS, iso, lessonState, pad2, type Lesson } from '../data/studio';

type Draft = Omit<Lesson, 'id'> & { id?: number };

const dotColor = (tone: 'success' | 'warning' | 'neutral') =>
  tone === 'success' ? 'var(--moss-500)' : tone === 'warning' ? 'var(--ochre-500)' : 'var(--stone-400)';

export function Studio() {
  const mobile = useMobile();
  const [lessons, setLessons] = useState<Lesson[]>(SEED_LESSONS);
  const [ym, setYm] = useState({ y: 2026, m: 8 });
  const [selected, setSelected] = useState('2026-09-08');
  const [editing, setEditing] = useState<Draft | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(null), 2400);
      return () => clearTimeout(t);
    }
  }, [toast]);

  const first = new Date(ym.y, ym.m, 1);
  const daysIn = new Date(ym.y, ym.m + 1, 0).getDate();
  const lead = first.getDay();
  const cells: (number | null)[] = [...Array(lead).fill(null), ...Array.from({ length: daysIn }, (_, i) => i + 1)];
  while (cells.length % 7) cells.push(null);

  const byDate = (d: string) => lessons.filter((l) => l.date === d).sort((a, b) => a.time.localeCompare(b.time));
  const dayLessons = byDate(selected);
  const monthLessons = lessons.filter((l) => l.date.startsWith(`${ym.y}-${pad2(ym.m + 1)}`));
  const shift = (n: number) => {
    const d = new Date(ym.y, ym.m + n, 1);
    setYm({ y: d.getFullYear(), m: d.getMonth() });
  };

  const save = () => {
    if (!editing || !editing.title || !editing.date) return;
    if (editing.id) {
      setLessons(lessons.map((l) => (l.id === editing.id ? (editing as Lesson) : l)));
    } else {
      setLessons([...lessons, { ...editing, id: Date.now() } as Lesson]);
    }
    setSelected(editing.date);
    setToast(editing.id ? 'השיעור עודכן' : 'השיעור נוסף ללוח');
    setEditing(null);
  };

  const remove = (id: number) => {
    setLessons(lessons.filter((l) => l.id !== id));
    setEditing(null);
    setToast('השיעור הוסר');
  };

  const selDate = new Date(selected + 'T00:00');
  const isSelectedMonth = selDate.getFullYear() === ym.y && selDate.getMonth() === ym.m;

  return (
    <>
      <Section narrow style={{ marginTop: 'var(--space-11)', textAlign: 'center' }}>
        <div style={{ ...EYE, color: 'var(--text-brand)' }}>Studio</div>
        <h1 style={{ fontSize: 'var(--text-4xl)', fontWeight: 300, marginTop: 'var(--space-5)' }}>שיעורים בסטודיו</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-lg)', maxWidth: '46ch', margin: 'var(--space-5) auto 0' }}>
          לוח השיעורים החודשי. שיעור נפתח כשמספר הנרשמים מגיע למינימום.
        </p>
      </Section>

      <Section style={{ marginTop: 'var(--space-10)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: mobile ? '1fr' : 'minmax(0,1.5fr) minmax(300px,1fr)', gap: mobile ? 'var(--space-6)' : 'var(--space-8)', alignItems: 'start' }}>
          <Card padding="0">
            <div style={{ display: 'flex', alignItems: 'center', gap: mobile ? 'var(--space-2)' : 'var(--space-4)', padding: mobile ? 'var(--space-3) var(--space-4)' : 'var(--space-5) var(--space-6)', borderBottom: '1px solid var(--line-hairline)', flexWrap: 'wrap' }}>
              <IconButton icon={<Icon name="chevron-right" size={18} />} label="חודש קודם" variant="ghost" size="sm" onClick={() => shift(-1)} />
              <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: 300, minWidth: '9ch' }}>
                {HE_MONTHS[ym.m]} {ym.y}
              </h2>
              <IconButton icon={<Icon name="chevron-left" size={18} />} label="חודש הבא" variant="ghost" size="sm" onClick={() => shift(1)} />
              <span style={{ flex: 1 }} />
              {mobile ? null : <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>{monthLessons.length} שיעורים</span>}
              <Button size="sm" onClick={() => setEditing({ ...EMPTY_LESSON, date: isSelectedMonth ? selected : iso(ym.y, ym.m, 1) })}>
                שיעור חדש
              </Button>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7,minmax(0,1fr))', padding: 'var(--space-3) var(--space-3) 0' }}>
              {HE_DAYS.map((d) => (
                <div key={d} style={{ ...EYE, textAlign: 'center', padding: 'var(--space-2) 0' }}>
                  {d}
                </div>
              ))}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7,minmax(0,1fr))', gap: 2, padding: '0 var(--space-3) var(--space-3)' }}>
              {cells.map((d, i) => {
                if (!d) return <div key={i} />;
                const date = iso(ym.y, ym.m, d);
                const ls = byDate(date);
                const on = date === selected;
                return (
                  <button
                    key={i}
                    onClick={() => setSelected(date)}
                    style={{
                      all: 'unset',
                      cursor: 'pointer',
                      boxSizing: 'border-box',
                      minHeight: mobile ? 48 : 84,
                      padding: mobile ? 'var(--space-2) 0' : 'var(--space-2) var(--space-3)',
                      alignItems: mobile ? 'center' : 'stretch',
                      borderRadius: 'var(--radius-control)',
                      background: on ? 'var(--clay-50)' : ls.length ? 'var(--surface-sunken)' : 'transparent',
                      border: '1px solid ' + (on ? 'var(--clay-500)' : 'transparent'),
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 4,
                    }}
                  >
                    <span style={{ fontSize: 'var(--text-sm)', fontVariantNumeric: 'tabular-nums', color: ls.length ? 'var(--text-heading)' : 'var(--text-muted)', fontWeight: ls.length ? 600 : 400 }}>{d}</span>
                    {mobile
                      ? ls.length
                        ? (
                            <span style={{ display: 'flex', gap: 3 }}>
                              {ls.map((l) => (
                                <span key={l.id} style={{ width: 5, height: 5, borderRadius: '50%', background: dotColor(lessonState(l).tone) }} />
                              ))}
                            </span>
                          )
                        : null
                      : ls.slice(0, 2).map((l) => {
                          const s = lessonState(l);
                          return (
                            <span key={l.id} style={{ fontSize: 'var(--text-2xs)', lineHeight: 1.3, color: s.tone === 'neutral' ? 'var(--text-muted)' : 'var(--text-body)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 4 }}>
                              <span style={{ width: 5, height: 5, borderRadius: '50%', flex: 'none', background: dotColor(s.tone) }} />
                              {l.time} {l.title}
                            </span>
                          );
                        })}
                    {!mobile && ls.length > 2 ? <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)' }}>+{ls.length - 2}</span> : null}
                  </button>
                );
              })}
            </div>
          </Card>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
            <div>
              <div style={EYE}>
                {HE_DAYS[selDate.getDay()]}׳ · {selDate.getDate()}.{selDate.getMonth() + 1}
              </div>
              <h3 style={{ fontSize: 'var(--text-xl)', fontWeight: 300, marginTop: 6 }}>{dayLessons.length ? `${dayLessons.length} שיעורים ביום זה` : 'אין שיעורים ביום זה'}</h3>
            </div>
            {dayLessons.map((l) => {
              const s = lessonState(l);
              return (
                <Card key={l.id} padding="var(--space-6)">
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-4)' }}>
                    <div style={{ minWidth: 0 }}>
                      <div style={EYE}>
                        {LESSON_TYPES.find((t) => t.value === l.type)?.label} · {l.time}
                      </div>
                      <div style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-lg)', marginTop: 6 }}>{l.title}</div>
                    </div>
                    <span style={{ flex: 1 }} />
                    <Badge tone={s.tone} dot={s.tone === 'success'}>
                      {s.label}
                    </Badge>
                  </div>
                  <div style={{ marginTop: 'var(--space-5)', fontSize: 'var(--text-sm)', color: 'var(--text-muted)', display: 'flex', gap: 'var(--space-3)', fontVariantNumeric: 'tabular-nums', flexWrap: 'wrap' }}>
                    <span>{l.enrolled} נרשמים</span>
                    <span>·</span>
                    <span>מינימום {l.min}</span>
                    <span>·</span>
                    <span>מקסימום {l.max}</span>
                  </div>
                  <div style={{ marginTop: 'var(--space-3)', height: 2, background: 'var(--stone-200)', borderRadius: 1, display: 'flex' }}>
                    <div style={{ width: `${Math.min(100, (l.enrolled / l.max) * 100)}%`, background: dotColor(s.tone) }} />
                  </div>
                  {l.notes ? <p style={{ marginTop: 'var(--space-5)', fontSize: 'var(--text-sm)', color: 'var(--text-body)' }}>{l.notes}</p> : null}
                  <div style={{ marginTop: 'var(--space-6)', display: 'flex', gap: 'var(--space-3)' }}>
                    <Button size="sm" variant="secondary" onClick={() => setEditing({ ...l })}>
                      עריכה
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => setEditing({ ...l })}>
                      נרשמים
                    </Button>
                  </div>
                </Card>
              );
            })}
            <Button variant={dayLessons.length ? 'ghost' : 'secondary'} size="sm" onClick={() => setEditing({ ...EMPTY_LESSON, date: selected })} style={{ alignSelf: 'flex-start' }}>
              הוספת שיעור ל־{selDate.getDate()}.{selDate.getMonth() + 1}
            </Button>
          </div>
        </div>
      </Section>

      {editing ? (
        <div style={{ position: 'fixed', inset: 0, zIndex: 60 }}>
          <Dialog
            open
            title={editing.id ? 'עריכת שיעור' : 'שיעור חדש'}
            description={editing.id ? undefined : 'השיעור יופיע בלוח מיד לאחר השמירה.'}
            onClose={() => setEditing(null)}
            width={560}
            footer={
              <>
                {editing.id ? (
                  <Button variant="ghost" size="sm" onClick={() => remove(editing.id!)}>
                    הסרה
                  </Button>
                ) : null}
                <span style={{ flex: 1 }} />
                <Button variant="ghost" size="sm" onClick={() => setEditing(null)}>
                  ביטול
                </Button>
                <Button size="sm" onClick={save} disabled={!editing.title || !editing.date}>
                  שמירה
                </Button>
              </>
            }
          >
            <LessonForm value={editing} onChange={setEditing} />
          </Dialog>
        </div>
      ) : null}
      {toast ? (
        <div style={{ position: 'fixed', bottom: 24, insetInlineStart: mobile ? 16 : 24, insetInlineEnd: mobile ? 16 : 'auto', zIndex: 50 }}>
          <Toast tone="success" title={toast} />
        </div>
      ) : null}
    </>
  );
}
