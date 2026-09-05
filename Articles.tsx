import { useState } from 'react';
import { Badge, Button, Card, Tag } from '../ds';
import { EYE } from '../components/chrome/constants';
import { Section } from '../components/chrome/Section';
import { useMobile } from '../lib/useMobile';
import { ARTICLE_KINDS, ARTICLES, type SeedArticle } from '../data/articles';
import type { Navigate, RouteParams } from '../types/route';

function kindLabel(kind: SeedArticle['kind']) {
  const found = ARTICLE_KINDS.find((k) => k.id === kind);
  return (found ? found.label : kind).replace('ים מוקלטים', ' מוקלט').replace(/ים$/, '');
}

function ArticleCard({ a, onOpen }: { a: SeedArticle; onOpen: (a: SeedArticle) => void }) {
  return (
    <Card interactive onClick={() => onOpen(a)} padding="0">
      <div style={{ height: 160, background: 'var(--surface-sunken)', borderRadius: '2px 2px 0 0' }} />
      <div style={{ padding: 'var(--space-6)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <span style={EYE}>{kindLabel(a.kind)}</span>
          <span style={{ flex: 1 }} />
          {a.locked ? <Badge tone="neutral">למנויים</Badge> : null}
        </div>
        <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 400, marginTop: 'var(--space-4)', lineHeight: 1.25 }}>{a.title}</h3>
        <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginTop: 'var(--space-3)', lineHeight: 1.7 }}>{a.text}</p>
        <div style={{ marginTop: 'var(--space-5)', fontSize: 'var(--text-xs)', color: 'var(--text-subtle)', display: 'flex', gap: 'var(--space-3)' }}>
          <span>{a.meta}</span>
          <span>·</span>
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>{a.date}</span>
        </div>
      </div>
    </Card>
  );
}

export function Articles({ onNavigate, params = {} }: { onNavigate: Navigate; params?: RouteParams }) {
  const mobile = useMobile();
  const [kind, setKind] = useState(params.kind || 'all');
  const list = kind === 'all' ? ARTICLES : ARTICLES.filter((a) => a.kind === kind);

  return (
    <>
      <Section narrow style={{ marginTop: 'var(--space-11)', textAlign: 'center' }}>
        <div style={{ ...EYE, color: 'var(--text-brand)' }}>Articles</div>
        <h1 style={{ fontSize: 'var(--text-4xl)', fontWeight: 300, marginTop: 'var(--space-5)' }}>מאמרים ושיעורים</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-lg)', maxWidth: '46ch', margin: 'var(--space-5) auto 0' }}>
          תיעוד עבודה על עצים, שיעורים מוקלטים ועדכונים מהסטודיו. השיעורים המוקלטים פתוחים למנויי מאגר הידע.
        </p>
      </Section>
      <Section style={{ marginTop: 'var(--space-10)' }}>
        <div style={{ display: 'flex', gap: 'var(--space-3)', flexWrap: mobile ? 'nowrap' : 'wrap', overflowX: mobile ? 'auto' : 'visible', paddingBottom: mobile ? 'var(--space-2)' : 0 }}>
          {ARTICLE_KINDS.map((k) => (
            <Tag key={k.id} selected={kind === k.id} onClick={() => setKind(k.id)}>
              {k.label}
            </Tag>
          ))}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: mobile ? '1fr' : 'repeat(auto-fill,minmax(280px,1fr))', gap: 'var(--space-6)', marginTop: 'var(--space-8)' }}>
          {list.map((a) => (
            <ArticleCard key={a.id} a={a} onOpen={(x) => onNavigate('article', { slug: x.id })} />
          ))}
        </div>
      </Section>
    </>
  );
}

export function Article({ params, onNavigate }: { params: RouteParams; onNavigate: Navigate }) {
  const mobile = useMobile();
  const a = ARTICLES.find((x) => x.id === params.slug) || ARTICLES[0];
  const related = ARTICLES.filter((x) => x.id !== a.id && (x.species === a.species || x.kind === a.kind)).slice(0, 2);

  return (
    <>
      <Section narrow style={{ marginTop: 'var(--space-9)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', fontSize: 'var(--text-sm)' }}>
          <a href="#" onClick={(e) => { e.preventDefault(); onNavigate('articles'); }} style={{ display: 'inline-flex', alignItems: 'center', gap: 4, border: 0, color: 'var(--text-muted)' }}>
            מאמרים
          </a>
          {a.species ? (
            <>
              <span style={{ color: 'var(--text-subtle)' }}>·</span>
              <a href="#" onClick={(e) => { e.preventDefault(); onNavigate('species', { slug: a.species }); }} style={{ border: 0, color: 'var(--text-muted)' }}>
                לעמוד המין
              </a>
            </>
          ) : null}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginTop: 'var(--space-8)' }}>
          <span style={{ ...EYE, color: 'var(--text-brand)' }}>{ARTICLE_KINDS.find((k) => k.id === a.kind)?.label}</span>
          {a.locked ? <Badge tone="neutral">למנויים</Badge> : null}
        </div>
        <h1 style={{ fontSize: mobile ? 'var(--text-3xl)' : 'var(--text-4xl)', fontWeight: 300, lineHeight: 1.1, marginTop: 'var(--space-4)' }}>{a.title}</h1>
        <div style={{ marginTop: 'var(--space-5)', fontSize: 'var(--text-sm)', color: 'var(--text-muted)', display: 'flex', gap: 'var(--space-3)' }}>
          <span>{a.meta}</span>
          <span>·</span>
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>{a.date}</span>
          <span>·</span>
          <span>שי כהן</span>
        </div>
      </Section>
      <Section narrow style={{ marginTop: 'var(--space-8)' }}>
        <div style={{ height: mobile ? 220 : 420, borderRadius: 2, overflow: 'hidden', background: 'var(--surface-sunken)' }} />
      </Section>
      <Section narrow style={{ marginTop: 'var(--space-8)' }}>
        {a.locked ? (
          <Card padding="var(--space-8)" style={{ background: 'var(--clay-50)', borderColor: 'var(--clay-100)' }}>
            <div style={EYE}>שיעור מוקלט</div>
            <h3 style={{ fontSize: 'var(--text-xl)', fontWeight: 400, marginTop: 'var(--space-4)' }}>השיעור פתוח למנויי מאגר הידע</h3>
            <p style={{ fontSize: 'var(--text-md)', color: 'var(--text-muted)', marginTop: 'var(--space-3)', lineHeight: 1.7 }}>
              המנוי כולל את כל השיעורים המוקלטים, מחזורי העבודה השנתיים לכל מין, ומענה לשאלות מתוך המאגר.
            </p>
            <div style={{ display: 'flex', gap: 'var(--space-3)', marginTop: 'var(--space-6)', flexWrap: 'wrap' }}>
              <Button onClick={() => onNavigate('kb')}>למאגר הידע</Button>
              <Button variant="ghost" onClick={() => onNavigate('contact')}>שאלות על המנוי</Button>
            </div>
          </Card>
        ) : (
          (a.body || []).map((p, i) => (
            <p key={i} className="oy-prose" style={{ fontSize: 'var(--text-lg)', lineHeight: 1.75, marginTop: i ? 'var(--space-6)' : 0 }}>
              {p}
            </p>
          ))
        )}
      </Section>
      {a.species ? (
        <Section narrow style={{ marginTop: 'var(--space-9)' }}>
          <Card padding="var(--space-6)" interactive onClick={() => onNavigate('species', { slug: a.species })}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-5)' }}>
              <div>
                <div style={EYE}>עמוד המין</div>
                <div style={{ fontSize: 'var(--text-lg)', marginTop: 4 }}>מחזור עבודה שנתי ופעולות החודש</div>
              </div>
              <span style={{ flex: 1 }} />
            </div>
          </Card>
        </Section>
      ) : null}
      {related.length ? (
        <Section eyebrow="Related" title="עוד בנושא">
          <div style={{ display: 'grid', gridTemplateColumns: mobile ? '1fr' : 'repeat(auto-fill,minmax(280px,1fr))', gap: 'var(--space-6)' }}>
            {related.map((r) => (
              <ArticleCard key={r.id} a={r} onOpen={(x) => onNavigate('article', { slug: x.id })} />
            ))}
          </div>
        </Section>
      ) : null}
    </>
  );
}
