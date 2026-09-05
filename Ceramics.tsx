import { useEffect, useState } from 'react';
import { Button, Card, Dialog, Divider, Input, Select, Textarea, Toast } from '../ds';
import { PotPreview } from '../components/ceramics/PotPreview';
import { EYE } from '../components/chrome/constants';
import { Section } from '../components/chrome/Section';
import { useMobile } from '../lib/useMobile';
import { AWARDS, GALLERY, SHAPES } from '../data/ceramics';

export function Ceramics() {
  const mobile = useMobile();
  const [dims, setDims] = useState({ L: '35', W: '25', H: '7' });
  const [shape, setShape] = useState('rect');
  const [order, setOrder] = useState(false);
  const [toast, setToast] = useState(false);

  const L = +dims.L || 0;
  const W = +dims.W || 0;
  const H = +dims.H || 0;
  const k = SHAPES.find((s) => s.value === shape)!.k;
  const price = Math.round(((L * W * 0.6 + H * 15) * k) / 10) * 10;
  const set = (key: 'L' | 'W' | 'H') => (e: React.ChangeEvent<HTMLInputElement>) =>
    setDims({ ...dims, [key]: e.target.value.replace(/[^\d.]/g, '') });
  const shapeLabel = SHAPES.find((s) => s.value === shape)!.label;

  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(false), 3000);
      return () => clearTimeout(t);
    }
  }, [toast]);

  const num: React.CSSProperties = { fontVariantNumeric: 'tabular-nums', direction: 'ltr', textAlign: 'right' };

  return (
    <>
      <Section narrow style={{ marginTop: 'var(--space-11)', textAlign: 'center' }}>
        <div style={{ ...EYE, color: 'var(--text-brand)' }}>O-Yaku ceramics</div>
        <h1 style={{ fontSize: 'var(--text-4xl)', fontWeight: 300, marginTop: 'var(--space-5)' }}>קרמיקה לבונסאי</h1>
        <p style={{ marginTop: 'var(--space-5)', color: 'var(--text-muted)', fontSize: 'var(--text-lg)', maxWidth: '48ch', margin: 'var(--space-5) auto 0' }}>
          כלי בונסאי שנבנים מתוך חיבור בין העץ, המידות, הצורה והגלזורה. כאן ירוכזו עבודות, תערוכות והזמנות של כלים בהתאמה אישית.
        </p>
      </Section>

      <Section eyebrow="Awards" title="פרסים">
        <div style={{ display: 'grid', gridTemplateColumns: mobile ? '1fr' : '1fr 1fr', gap: 'var(--space-6)' }}>
          {AWARDS.map((a) => (
            <Card key={a.title} padding="var(--space-8)">
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--space-4)' }}>
                <span style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-2xl)', fontWeight: 300, color: 'var(--text-brand)' }}>{a.year}</span>
                <span style={EYE}>{a.where}</span>
              </div>
              <h3 style={{ fontSize: 'var(--text-xl)', fontWeight: 400, marginTop: 'var(--space-4)' }}>{a.title}</h3>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginTop: 'var(--space-3)' }}>{a.text}</p>
            </Card>
          ))}
        </div>
      </Section>

      <Section eyebrow="Exhibitions" title="תערוכות ועבודות" lede="תיעוד מתערוכות Trophy בבלגיה ומהתחרויות ביפן.">
        <div style={{ display: 'grid', gridTemplateColumns: mobile ? '1fr 1fr' : 'repeat(3,1fr)', gap: 2 }}>
          {GALLERY.map((g, i) => (
            <figure key={i} style={{ margin: 0 }}>
              <div style={{ height: mobile ? 160 : 260, background: g.t, borderRadius: 2, position: 'relative' }} />
              <figcaption style={{ padding: 'var(--space-4) var(--space-2) var(--space-6)' }}>
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-brand)', fontWeight: 600 }}>{g.m}</div>
                <div style={{ fontSize: 'var(--text-sm)', marginTop: 4 }}>{g.c}</div>
              </figcaption>
            </figure>
          ))}
        </div>
      </Section>

      <Section eyebrow="Commission" title="מחשבון כלי בהזמנה" lede="הכניסו מידות ובחרו צורה לקבלת הדמיה ומחיר משוער.">
        <Card padding="0">
          <div style={{ display: 'grid', gridTemplateColumns: mobile ? '1fr' : 'minmax(0,1fr) minmax(0,1.2fr)' }}>
            <div style={{ minWidth: 0, padding: mobile ? 'var(--space-6)' : 'var(--space-8)', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,minmax(0,1fr))', gap: 'var(--space-4)' }}>
                <Input label="אורך (ס״מ)" value={dims.L} onChange={set('L')} style={{ ...num, minWidth: 0, width: '100%' }} wrapperStyle={{ minWidth: 0 }} />
                <Input label="רוחב (ס״מ)" value={dims.W} onChange={set('W')} style={{ ...num, minWidth: 0, width: '100%' }} wrapperStyle={{ minWidth: 0 }} />
                <Input label="גובה (ס״מ)" value={dims.H} onChange={set('H')} style={{ ...num, minWidth: 0, width: '100%' }} wrapperStyle={{ minWidth: 0 }} />
              </div>
              <Select label="צורה" options={SHAPES.map(({ value, label }) => ({ value, label }))} value={shape} onChange={(e) => setShape(e.target.value)} />
              <Divider />
              <div>
                <div style={EYE}>מחיר משוער</div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: mobile ? 'var(--text-3xl)' : 'var(--text-4xl)', fontWeight: 300, marginTop: 'var(--space-2)', fontVariantNumeric: 'tabular-nums' }}>
                  ≈ ₪{price.toLocaleString('en-US')}
                </div>
                <div style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginTop: 'var(--space-2)' }}>
                  {shapeLabel} ·{' '}
                  <span style={{ direction: 'ltr', unicodeBidi: 'isolate' }}>
                    {L} × {W} × {H}
                  </span>{' '}
                  ס״מ
                </div>
              </div>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>זהו אומדן ראשוני בלבד. המחיר הסופי נקבע לאחר התאמת המבנה, הגלזורה ופרטי העבודה.</p>
              <div>
                <Button onClick={() => setOrder(true)} style={mobile ? { width: '100%' } : undefined}>
                  לבירור והזמנה
                </Button>
              </div>
            </div>
            <div style={{ minWidth: 0, padding: mobile ? 'var(--space-6)' : 'var(--space-8)', background: 'var(--surface-sunken)', order: mobile ? -1 : 0, borderInlineStart: mobile ? 'none' : '1px solid var(--line-hairline)', borderBottom: mobile ? '1px solid var(--line-hairline)' : 'none' }}>
              <PotPreview shape={shape} L={L} W={W} H={H} />
            </div>
          </div>
        </Card>
      </Section>

      {order ? (
        <div style={{ position: 'fixed', inset: 0, zIndex: 60 }}>
          <Dialog
            open
            title="בירור והזמנה"
            description={`${shapeLabel} · ${L} × ${W} × ${H} ס״מ · ≈ ₪${price.toLocaleString('en-US')}`}
            onClose={() => setOrder(false)}
            width={520}
            footer={
              <>
                <Button variant="ghost" size="sm" onClick={() => setOrder(false)}>
                  ביטול
                </Button>
                <Button
                  size="sm"
                  onClick={() => {
                    setOrder(false);
                    setToast(true);
                  }}
                >
                  שליחה
                </Button>
              </>
            }
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
              <Input label="שם" placeholder="שם מלא" />
              <Input label="דואר אלקטרוני" placeholder="name@example.com" />
              <Textarea label="לאיזה עץ הכלי מיועד?" placeholder="מין, גודל העץ, גלזורה מועדפת" rows={3} />
            </div>
          </Dialog>
        </div>
      ) : null}
      {toast ? (
        <div style={{ position: 'fixed', bottom: 24, insetInlineStart: 24, zIndex: 50 }}>
          <Toast tone="success" onDismiss={() => setToast(false)}>
            הפנייה נשלחה. נחזור אליכם תוך יומיים.
          </Toast>
        </div>
      ) : null}
    </>
  );
}
