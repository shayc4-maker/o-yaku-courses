import { useState } from 'react';
import { Button, Divider, Icon, Input, Select, Textarea } from '../ds';
import { EYE } from '../components/chrome/constants';
import { Section } from '../components/chrome/Section';
import { useMobile } from '../lib/useMobile';
import type { Navigate } from '../types/route';

export function About({ onNavigate }: { onNavigate: Navigate }) {
  const mobile = useMobile();
  return (
    <>
      <Section narrow style={{ marginTop: 'var(--space-11)' }}>
        <div style={{ ...EYE, color: 'var(--text-brand)' }}>About</div>
        <h1 style={{ fontSize: 'var(--text-4xl)', fontWeight: 300, marginTop: 'var(--space-5)', lineHeight: 1.1 }}>העץ, והכלי שהעץ גדל בו</h1>
        <p className="oy-prose" style={{ fontSize: 'var(--text-lg)', color: 'var(--text-muted)', marginTop: 'var(--space-6)' }}>
          O-Yaku הוא בית ספר לבונסאי וסטודיו לקרמיקה בירושלים. אנחנו מלמדים את שני המקצועות באותו חדר: איך מעצבים עץ, ואיך בונים את הכלי שמתאים לו.
        </p>
      </Section>
      <Section style={{ marginTop: 'var(--space-9)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: mobile ? '1fr' : '1fr 1fr', gap: 2 }}>
          <div style={{ height: mobile ? 240 : 420, borderRadius: 2, overflow: 'hidden', background: 'var(--surface-sunken)' }} />
          <div style={{ height: mobile ? 240 : 420, borderRadius: 2, overflow: 'hidden', background: 'var(--surface-sunken)' }} />
        </div>
      </Section>
      <Section narrow eyebrow="Shay Cohen" title="שי כהן">
        <p className="oy-prose" style={{ fontSize: 'var(--text-lg)', lineHeight: 1.75 }}>
          אמן בונסאי וקרמיקה. עוסק בבונסאי משנת 2014, למד אצל עופר גרינוולד ואנריקו סביני, ומנהל את אוסף עצי הבונסאי של הגן הבוטני בירושלים.
        </p>
        <p className="oy-prose" style={{ fontSize: 'var(--text-lg)', lineHeight: 1.75, marginTop: 'var(--space-6)' }}>
          הקרמיקה הגיעה מתוך הצורך: כלי לבונסאי צריך להתאים לעץ במידות, בצבע ובמשקל, וכלים כאלה קשה למצוא. הכלים נבנים ביד, נשרפים בסטודיו ומיועדים לעצים ספציפיים.
        </p>
      </Section>
      <Section narrow eyebrow="Teaching" title="איך אנחנו מלמדים">
        <p className="oy-prose" style={{ fontSize: 'var(--text-lg)', lineHeight: 1.75 }}>
          כל קורס נפתח בקבוצה של שמונה תלמידים. שנים־עשר מפגשים שמתחילים בעץ אחד ונגמרים בעץ אחד. בין המפגשים, מאגר הידע עונה על השאלות שעולות בבית.
        </p>
        <div style={{ display: 'flex', gap: 'var(--space-3)', marginTop: 'var(--space-7)', flexWrap: 'wrap' }}>
          <Button onClick={() => onNavigate('studio')}>לוח השיעורים</Button>
          <Button variant="secondary" onClick={() => onNavigate('contact')}>כתבו לנו</Button>
        </div>
      </Section>
    </>
  );
}

const CONTACT_TOPICS = [
  { value: 'course', label: 'הרשמה לקורס או סדנה' },
  { value: 'pot', label: 'כלי בהזמנה' },
  { value: 'shop', label: 'הזמנה מהחנות' },
  { value: 'kb', label: 'מנוי למאגר הידע' },
  { value: 'visit', label: 'ביקור בסטודיו' },
  { value: 'other', label: 'אחר' },
];

export function Contact({ onNavigate }: { onNavigate: Navigate }) {
  const mobile = useMobile();
  const [f, setF] = useState({ name: '', phone: '', email: '', topic: 'course', msg: '' });
  const [sent, setSent] = useState(false);
  const set = (k: keyof typeof f) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setF({ ...f, [k]: e.target.value });
  const ok = f.name && (f.phone || f.email) && f.msg;

  const row = (icon: string, a: string, b?: string) => (
    <div style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'flex-start' }}>
      <Icon name={icon} size={18} color="var(--text-muted)" />
      <div style={{ fontSize: 'var(--text-md)', lineHeight: 1.6 }}>
        <div>{a}</div>
        {b ? <div style={{ color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}>{b}</div> : null}
      </div>
    </div>
  );

  return (
    <>
      <Section narrow style={{ marginTop: 'var(--space-11)' }}>
        <div style={{ ...EYE, color: 'var(--text-brand)' }}>Contact</div>
        <h1 style={{ fontSize: 'var(--text-4xl)', fontWeight: 300, marginTop: 'var(--space-5)' }}>צור קשר</h1>
        <p className="oy-prose" style={{ fontSize: 'var(--text-lg)', color: 'var(--text-muted)', marginTop: 'var(--space-5)' }}>כתבו לנו ונחזור אליכם תוך יום עסקים. לביקור בסטודיו מתאמים מראש.</p>
      </Section>
      <Section style={{ marginTop: 'var(--space-9)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: mobile ? '1fr' : 'minmax(0,1.2fr) minmax(280px,1fr)', gap: mobile ? 'var(--space-9)' : 'var(--space-11)', alignItems: 'start' }}>
          {sent ? (
            <div style={{ border: '1px solid var(--line-hairline)', borderRadius: 'var(--radius-card)', padding: 'var(--space-9)', background: 'var(--surface-card)' }}>
              <div style={EYE}>נשלח</div>
              <h2 style={{ fontSize: 'var(--text-2xl)', fontWeight: 300, marginTop: 'var(--space-4)' }}>תודה, {f.name}.</h2>
              <p style={{ color: 'var(--text-muted)', marginTop: 'var(--space-3)', lineHeight: 1.7 }}>נחזור אליכם תוך יום עסקים ל{f.email ? 'דוא״ל' : 'טלפון'} שהשארתם.</p>
              <div style={{ marginTop: 'var(--space-7)' }}>
                <Button variant="secondary" onClick={() => onNavigate('home')}>לדף הבית</Button>
              </div>
            </div>
          ) : (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (ok) setSent(true);
              }}
              style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}
            >
              <Input label="שם" value={f.name} onChange={set('name')} placeholder="שם מלא" />
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(200px,1fr))', gap: 'var(--space-4)' }}>
                <Input label="טלפון" value={f.phone} onChange={set('phone')} placeholder="050-0000000" style={{ direction: 'ltr', textAlign: 'right' }} />
                <Input label="דוא״ל" value={f.email} onChange={set('email')} placeholder="name@example.com" style={{ direction: 'ltr', textAlign: 'right' }} />
              </div>
              <Select label="נושא" options={CONTACT_TOPICS} value={f.topic} onChange={set('topic')} />
              <Textarea label="הודעה" value={f.msg} onChange={set('msg')} rows={5} placeholder="במה נוכל לעזור" />
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', marginTop: 'var(--space-2)' }}>
                <Button type="submit" disabled={!ok}>שליחה</Button>
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-subtle)' }}>טלפון או דוא״ל, לפחות אחד מהם.</span>
              </div>
            </form>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
            <Divider label="Studio" />
            {row('map-pin', 'הסטודיו, ירושלים', 'הכתובת המדויקת נשלחת בתיאום ביקור.')}
            {row('clock', 'סטודיו פתוח · יום שישי 10:00–14:00', 'שאר הימים בתיאום מראש.')}
            {row('mail', 'studio@o-yaku.co.il')}
            {row('phone', '050-000-0000', 'הודעות בוואטסאפ עדיפות.')}
            <Divider label="Follow" />
            <div style={{ display: 'flex', gap: 'var(--space-5)', color: 'var(--text-muted)' }}>
              <Icon name="instagram" size={18} />
              <Icon name="youtube" size={18} />
            </div>
            <div style={{ height: mobile ? 180 : 220, borderRadius: 2, overflow: 'hidden', marginTop: 'var(--space-2)', background: 'var(--surface-sunken)' }} />
          </div>
        </div>
      </Section>
    </>
  );
}
