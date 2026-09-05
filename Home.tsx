import { useState } from 'react';
import { Button, Card, Icon } from '../ds';
import { AskBox } from '../components/search/AskBox';
import { EYE, WRAP } from '../components/chrome/constants';
import { Section } from '../components/chrome/Section';
import { useMobile } from '../lib/useMobile';
import type { Navigate, PageId } from '../types/route';

// No live source for "featured content" yet (no featured/pinned flag in articles or lessons).
// Kept as curated seed data until the studio defines what "featured" means in the database.
const FEATURED: { id: string; title: string; text: string; kind: string }[] = [
  { id: 'olive-2019', title: 'זית: תיעוד פיתוח 2019–2024', text: 'חמש שנים על עץ אחד שנאסף מבוסתן נטוש. מהשתלה ראשונה ועד תצוגה.', kind: 'מאמר' },
  { id: 'lesson-wire', title: 'שיעור חדש: חיווט ענפים עבים', text: 'מתי מותר לכופף ענף בעובי אצבע, ואיך לא לשבור אותו. 52 דקות.', kind: 'עדכון' },
  { id: 'juniper-year-one', title: 'ערער: שנה ראשונה אחרי איסוף', text: 'מה עושים ומה לא עושים לעץ שהגיע מההר. בעיקר: לא לגעת.', kind: 'מאמר' },
];

const CTAS: [PageId, string][] = [
  ['kb', 'כניסה למאגר הידע'],
  ['articles', 'קורסים ושיעורים'],
  ['studio', 'שיעורים בסטודיו'],
];

export function Home({ onNavigate }: { onNavigate: Navigate }) {
  const mobile = useMobile();
  const [q, setQ] = useState('');

  return (
    <>
      <section className="oy-wrap" style={{ ...WRAP, paddingTop: mobile ? 'var(--space-9)' : 'var(--space-12)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: mobile ? '1fr' : '1fr 1fr', gap: mobile ? 'var(--space-8)' : 'var(--space-11)', alignItems: 'center' }}>
          <div>
            <div style={{ ...EYE, color: 'var(--text-brand)' }}>O-YAKU · בית ספר לבונסאי</div>
            <h1 style={{ fontSize: 'var(--text-4xl)', fontWeight: 300, lineHeight: 1.08, marginTop: 'var(--space-6)' }}>
              בונסאי,
              <br />
              ידע ותהליכי עומק
            </h1>
            <p style={{ marginTop: 'var(--space-6)', fontSize: 'var(--text-lg)', lineHeight: 1.65, color: 'var(--text-muted)', maxWidth: '38ch' }}>
              ידע מעשי בבונסאי, שיעורים מוקלטים, תהליכי פיתוח של עצים ומאגר ידע שמתעדכן לאורך זמן.
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0, marginTop: 'var(--space-8)', maxWidth: 360, borderTop: '1px solid var(--line-hairline)' }}>
              {CTAS.map(([id, l]) => (
                <a
                  key={id}
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    onNavigate(id);
                  }}
                  style={{ display: 'flex', alignItems: 'center', padding: 'var(--space-4) 0', borderBottom: '1px solid var(--line-hairline)', color: 'var(--text-heading)', fontSize: 'var(--text-md)', fontWeight: 600 }}
                >
                  <span style={{ flex: 1 }}>{l}</span>
                  <Icon name="arrow-left" size={16} color="var(--clay-600)" />
                </a>
              ))}
            </div>
          </div>
          <div style={{ height: mobile ? 240 : 460, order: mobile ? -1 : 0, background: 'var(--stone-100)', borderRadius: 2, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ fontSize: 10, letterSpacing: '.16em', textTransform: 'uppercase', color: 'var(--text-subtle)', fontWeight: 600 }}>תמונת רקע · בהמתנה לחומרי צילום</span>
          </div>
        </div>
      </section>

      <Section narrow style={{ marginTop: 'var(--space-11)' }}>
        <div style={{ borderTop: '1px solid var(--line-hairline)', borderBottom: '1px solid var(--line-hairline)', padding: 'var(--space-8) 0' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--space-4)', marginBottom: 'var(--space-5)', flexWrap: 'wrap' }}>
            <h2 style={{ fontSize: 'var(--text-lg)', fontWeight: 400 }}>יש שאלה על עץ?</h2>
            <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>התשובה מחכה במאגר הידע.</span>
          </div>
          <AskBox value={q} onChange={setQ} onSubmit={(v) => onNavigate('kb', { q: v })} compact />
        </div>
      </Section>

      <Section narrow eyebrow="About" title="מי זה O-YAKU">
        <p className="oy-prose" style={{ fontSize: 'var(--text-lg)', lineHeight: 1.6 }}>
          שי כהן, אמן בונסאי וקרמיקה. עוסק בבונסאי משנת 2014, למד אצל עופר גרינוולד ואנריקו סביני, ומנהל את אוסף עצי הבונסאי של הגן הבוטני בירושלים.
        </p>
        <div style={{ marginTop: 'var(--space-6)' }}>
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              onNavigate('about');
            }}
            style={{ fontSize: 'var(--text-sm)', fontWeight: 600 }}
          >
            לקרוא עוד
          </a>
        </div>
      </Section>

      <Section eyebrow="Featured" title="תוכן נבחר" action={<Button variant="ghost" size="sm" onClick={() => onNavigate('articles')}>כל המאמרים</Button>}>
        <div style={{ display: 'grid', gridTemplateColumns: mobile ? '1fr' : 'repeat(3,1fr)', gap: 'var(--space-6)' }}>
          {FEATURED.map((f) => (
            <Card key={f.id} interactive onClick={() => onNavigate('article', { slug: f.id })}>
              <div style={EYE}>{f.kind}</div>
              <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 400, marginTop: 'var(--space-4)' }}>{f.title}</h3>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginTop: 'var(--space-3)', lineHeight: 1.7 }}>{f.text}</p>
              <div style={{ marginTop: 'var(--space-6)', display: 'flex', alignItems: 'center', gap: 6, fontSize: 'var(--text-sm)', fontWeight: 600, color: 'var(--text-link)' }}>
                לקריאה <Icon name="arrow-left" size={16} />
              </div>
            </Card>
          ))}
        </div>
      </Section>
    </>
  );
}
