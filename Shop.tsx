import { useEffect, useState } from 'react';
import { Badge, Button, Card, Dialog, Divider, Input, Tag, Textarea, Toast } from '../ds';
import { EYE } from '../components/chrome/constants';
import { Section } from '../components/chrome/Section';
import { useMobile } from '../lib/useMobile';
import { SHOP_CATS, SHOP_ITEMS, type ShopItem } from '../data/shop';
import type { Navigate } from '../types/route';

export function Shop({ onNavigate }: { onNavigate: Navigate }) {
  const mobile = useMobile();
  const [cat, setCat] = useState('all');
  const [cart, setCart] = useState<ShopItem[]>([]);
  const [order, setOrder] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(null), 2400);
      return () => clearTimeout(t);
    }
  }, [toast]);

  const items = cat === 'all' ? SHOP_ITEMS : SHOP_ITEMS.filter((i) => i.cat === cat);
  const current = SHOP_CATS.find((c) => c.id === cat)!;
  const add = (i: ShopItem) => {
    setCart([...cart, i]);
    setToast(i.name);
  };
  const total = cart.reduce((s, i) => s + i.price, 0);

  return (
    <>
      <Section narrow style={{ marginTop: 'var(--space-11)', textAlign: 'center' }}>
        <div style={{ ...EYE, color: 'var(--text-brand)' }}>Shop</div>
        <h1 style={{ fontSize: 'var(--text-4xl)', fontWeight: 300, marginTop: 'var(--space-5)' }}>חנות</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-lg)', maxWidth: '46ch', margin: 'var(--space-5) auto 0' }}>
          עצים, כלים ומצע מהסטודיו. בוחרים פריטים, שולחים בקשת הזמנה, ואנחנו חוזרים אליכם לתיאום תשלום ואיסוף.
        </p>
      </Section>

      <Section style={{ marginTop: 'var(--space-10)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', flexWrap: 'wrap', ...(mobile ? { overflowX: 'auto', flexWrap: 'nowrap', paddingBottom: 'var(--space-2)' } : null) }}>
          {SHOP_CATS.map((c) => (
            <Tag key={c.id} selected={cat === c.id} onClick={() => setCat(c.id)}>
              {c.label}
            </Tag>
          ))}
          <span style={{ flex: 1 }} />
          <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', fontVariantNumeric: 'tabular-nums' }}>{items.length} פריטים</span>
          {cart.length ? (
            <Button size="sm" variant="secondary" onClick={() => setOrder(true)}>
              בקשת הזמנה · {cart.length}
            </Button>
          ) : null}
        </div>
        <div style={{ margin: 'var(--space-7) 0' }}>
          <Divider label={current.en || 'All'} />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: mobile ? '1fr 1fr' : 'repeat(auto-fill,minmax(220px,1fr))', gap: mobile ? 'var(--space-4)' : 'var(--space-6)' }}>
          {items.map((i) => (
            <Card key={i.name} padding="0">
              <div style={{ height: mobile ? 130 : 200, background: 'var(--surface-sunken)', borderRadius: '2px 2px 0 0', position: 'relative', display: 'grid', placeItems: 'center' }}>
                <span style={{ position: 'absolute', bottom: 10, insetInlineStart: 12, fontSize: 10, letterSpacing: '.16em', textTransform: 'uppercase', color: 'var(--text-subtle)', fontWeight: 600 }}>צילום מוצר</span>
              </div>
              <div style={{ padding: mobile ? 'var(--space-4)' : 'var(--space-6)', display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                <div style={EYE}>{SHOP_CATS.find((c) => c.id === i.cat)?.label}</div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: mobile ? 'var(--text-md)' : 'var(--text-lg)', lineHeight: 1.2 }}>{i.name}</div>
                <div style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>{i.meta}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginTop: 'var(--space-3)', flexWrap: 'wrap' }}>
                  <span style={{ fontWeight: 600, fontVariantNumeric: 'tabular-nums', whiteSpace: 'nowrap' }}>₪{i.price.toLocaleString('en-US')}</span>
                  <span style={{ flex: 1 }} />
                  {i.stock === 0 ? <Badge tone="neutral">מלא</Badge> : i.stock <= 2 ? <Badge tone="warning">נותרו {i.stock}</Badge> : null}
                </div>
                <Button size="sm" variant={i.stock === 0 ? 'secondary' : 'primary'} onClick={() => add(i)} style={{ width: '100%', marginTop: 'var(--space-2)' }}>
                  {i.stock === 0 ? 'הרשמה להמתנה' : 'הוספה לבקשה'}
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </Section>

      <Section narrow>
        <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', textAlign: 'center' }}>
          בשלב זה אין תשלום באתר.{' '}
          <a href="#" onClick={(e) => { e.preventDefault(); onNavigate('contact'); }}>
            צור קשר
          </a>{' '}
          · כלי בהתאמה אישית?{' '}
          <a href="#" onClick={(e) => { e.preventDefault(); onNavigate('ceramics'); }}>
            מחשבון כלי בהזמנה
          </a>
        </p>
      </Section>

      {mobile && cart.length ? (
        <div style={{ position: 'fixed', bottom: 0, insetInline: 0, zIndex: 45, background: 'rgba(251,249,246,.92)', backdropFilter: 'blur(10px)', borderTop: '1px solid var(--line-hairline)', padding: 'var(--space-4) var(--gutter-page)', display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
          <span style={{ fontSize: 'var(--text-sm)', fontVariantNumeric: 'tabular-nums' }}>
            {cart.length} פריטים · ₪{total.toLocaleString('en-US')}
          </span>
          <span style={{ flex: 1 }} />
          <Button size="sm" onClick={() => setOrder(true)}>בקשת הזמנה</Button>
        </div>
      ) : null}
      {order ? (
        <div style={{ position: 'fixed', inset: 0, zIndex: 60 }}>
          <Dialog
            open
            title="בקשת הזמנה"
            description="נחזור אליכם תוך יום עסקים לתיאום תשלום, איסוף או משלוח."
            onClose={() => setOrder(false)}
            footer={
              <>
                <Button variant="ghost" size="sm" onClick={() => setOrder(false)}>
                  ביטול
                </Button>
                <Button
                  size="sm"
                  onClick={() => {
                    setOrder(false);
                    setCart([]);
                    setToast('בקשת ההזמנה נשלחה');
                  }}
                >
                  שליחה
                </Button>
              </>
            }
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                {cart.map((i, n) => (
                  <div key={n} style={{ display: 'flex', gap: 'var(--space-4)', padding: 'var(--space-3) 0', borderBottom: '1px solid var(--line-hairline)', fontSize: 'var(--text-sm)' }}>
                    <span>{i.name}</span>
                    <span style={{ flex: 1 }} />
                    <span style={{ fontVariantNumeric: 'tabular-nums' }}>₪{i.price.toLocaleString('en-US')}</span>
                  </div>
                ))}
                <div style={{ display: 'flex', padding: 'var(--space-3) 0', fontSize: 'var(--text-sm)', fontWeight: 600 }}>
                  <span>סה״כ משוער</span>
                  <span style={{ flex: 1 }} />
                  <span style={{ fontVariantNumeric: 'tabular-nums' }}>₪{total.toLocaleString('en-US')}</span>
                </div>
              </div>
              <Input label="שם" placeholder="שם מלא" />
              <Input label="טלפון" placeholder="050-0000000" style={{ direction: 'ltr', textAlign: 'right' }} />
              <Input label="דואר אלקטרוני" placeholder="name@example.com" />
              <Textarea label="הערות" placeholder="איסוף או משלוח, מועד מועדף" rows={2} />
            </div>
          </Dialog>
        </div>
      ) : null}

      {toast ? (
        <div style={{ position: 'fixed', bottom: mobile ? 84 : 24, insetInlineStart: mobile ? 16 : 24, insetInlineEnd: mobile ? 16 : 'auto', zIndex: 50 }}>
          <Toast tone="success" title={toast === 'בקשת ההזמנה נשלחה' ? toast : 'נוסף לבקשה'} description={toast === 'בקשת ההזמנה נשלחה' ? 'נחזור אליכם בהקדם.' : toast} />
        </div>
      ) : null}
    </>
  );
}
