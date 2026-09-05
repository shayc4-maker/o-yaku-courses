import { useEffect, useMemo, useState } from 'react';
import { Badge, Card, Icon } from '../ds';
import { Ask } from '../components/search/Ask';
import { EYE } from '../components/chrome/constants';
import { Section } from '../components/chrome/Section';
import { useMobile } from '../lib/useMobile';
import {
  HE_MONTHS,
  getSpeciesBySlug,
  listActionMonths,
  listPublishedArticles,
  listSeasonalActionsForCategory,
  listSeasonalActionsForSpecies,
} from '../lib/data';
import type { Navigate, RouteParams } from '../types/route';
import type { ArticleRow, SeasonalActionRow, SpeciesRow } from '../types/db';

interface ActionWithMonths extends SeasonalActionRow {
  months: number[];
}

function ActionRow({ a, last }: { a: SeasonalActionRow; last: boolean }) {
  const speciesSpecific = a.species_id != null;
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(96px,112px) minmax(0,1fr)', gap: 'var(--space-4)', padding: 'var(--space-5) 0', borderBottom: last ? 'none' : '1px solid var(--line-hairline)' }}>
      <div>
        <Badge tone={speciesSpecific ? 'brand' : 'neutral'}>{speciesSpecific ? 'ספציפי למין' : 'כללי לקטגוריה'}</Badge>
      </div>
      <div>
        <h4 style={{ fontFamily: 'var(--font-body)', fontSize: 'var(--text-md)', fontWeight: 600 }}>{a.name_he}</h4>
        {a.guidance_he ? <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginTop: 'var(--space-1)', lineHeight: 1.7 }}>{a.guidance_he}</p> : null}
      </div>
    </div>
  );
}

function MonthBlock({ label, month, actions }: { label: string; month: number; actions: SeasonalActionRow[] }) {
  return (
    <div style={{ padding: 'var(--space-7)' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--space-3)', paddingBottom: 'var(--space-4)', borderBottom: '1px solid var(--line-strong)' }}>
        <span style={EYE}>{label}</span>
        <span style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-lg)' }}>{HE_MONTHS[month - 1]}</span>
      </div>
      {actions.length ? (
        actions.map((a, i) => <ActionRow key={a.id} a={a} last={i === actions.length - 1} />)
      ) : (
        <p style={{ padding: 'var(--space-6) 0 0', color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}>אין פעולות ייעודיות החודש. נותנים לעץ לנוח ובודקים השקיה בלבד.</p>
      )}
    </div>
  );
}

export function Species({ params, onNavigate }: { params: RouteParams; onNavigate: Navigate }) {
  const mobile = useMobile();
  const [sp, setSp] = useState<SpeciesRow | null | undefined>(undefined);
  const [actions, setActions] = useState<ActionWithMonths[]>([]);
  const [articles, setArticles] = useState<ArticleRow[]>([]);

  const now = useMemo(() => new Date(), []);
  const curMonth = now.getMonth() + 1;
  const nextMonth = curMonth === 12 ? 1 : curMonth + 1;

  useEffect(() => {
    let cancelled = false;
    if (!params.slug) {
      setSp(null);
      return;
    }
    getSpeciesBySlug(params.slug).then(async (row) => {
      if (cancelled) return;
      setSp(row ?? null);
      if (!row) return;

      const [speciesActions, categoryActions, allArticles] = await Promise.all([
        listSeasonalActionsForSpecies(row.id),
        row.category ? listSeasonalActionsForCategory(row.category) : Promise.resolve([]),
        listPublishedArticles(50),
      ]);
      const all = [...speciesActions, ...categoryActions];
      const months = await listActionMonths(all.map((a) => a.id));
      const monthsByAction = new Map<string, number[]>();
      for (const m of months) {
        const list = monthsByAction.get(m.action_id) || [];
        list.push(m.month);
        monthsByAction.set(m.action_id, list);
      }
      if (!cancelled) {
        setActions(all.map((a) => ({ ...a, months: monthsByAction.get(a.id) || [] })));
        setArticles(allArticles.filter((a) => a.species_href && a.species_href.includes(row.slug)));
      }
    });
    return () => {
      cancelled = true;
    };
  }, [params.slug]);

  if (sp === undefined) {
    return (
      <Section narrow style={{ marginTop: 'var(--space-11)' }}>
        <p style={{ color: 'var(--text-muted)' }}>טוען…</p>
      </Section>
    );
  }

  if (sp === null) {
    return (
      <Section narrow style={{ marginTop: 'var(--space-11)' }}>
        <div style={EYE}>לא נמצא</div>
        <h1 style={{ fontSize: 'var(--text-3xl)', fontWeight: 300, marginTop: 'var(--space-4)' }}>המין המבוקש לא נמצא</h1>
        <div style={{ marginTop: 'var(--space-6)' }}>
          <a href="#" onClick={(e) => { e.preventDefault(); onNavigate('kb'); }} style={{ fontSize: 'var(--text-sm)', fontWeight: 600 }}>
            חזרה למאגר הידע
          </a>
        </div>
      </Section>
    );
  }

  const nowActions = actions.filter((a) => a.months.includes(curMonth));
  const nextActions = actions.filter((a) => a.months.includes(nextMonth));

  const monthTags: string[][] = Array.from({ length: 12 }, (_, i) => {
    const month = i + 1;
    return actions.filter((a) => a.months.includes(month)).map((a) => a.name_he);
  });

  return (
    <>
      <Section style={{ marginTop: 'var(--space-9)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', fontSize: 'var(--text-sm)' }}>
          <a href="#" onClick={(e) => { e.preventDefault(); onNavigate('kb'); }} style={{ display: 'inline-flex', alignItems: 'center', gap: 4, border: 0, color: 'var(--text-muted)' }}>
            <Icon name="arrow-right" size={16} /> חזרה למינים
          </a>
          {sp.category ? (
            <>
              <span style={{ color: 'var(--text-subtle)' }}>·</span>
              <span style={{ color: 'var(--text-muted)' }}>{sp.category}</span>
            </>
          ) : null}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: mobile ? '1fr' : 'minmax(0,1.2fr) minmax(0,1fr)', gap: mobile ? 'var(--space-7)' : 'var(--space-10)', alignItems: 'end', marginTop: 'var(--space-8)' }}>
          <div>
            <h1 style={{ fontSize: 'var(--text-4xl)', fontWeight: 300, lineHeight: 1.08 }}>{sp.name_he}</h1>
            {sp.botanical_name ? (
              <div style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic', color: 'var(--text-muted)', fontSize: 'var(--text-lg)', marginTop: 'var(--space-2)', direction: 'ltr', textAlign: 'right' }}>
                {sp.botanical_name}
              </div>
            ) : null}
            {sp.description_he ? (
              <p className="oy-prose" style={{ marginTop: 'var(--space-6)', fontSize: 'var(--text-lg)', color: 'var(--text-muted)' }}>
                {sp.description_he}
              </p>
            ) : null}
          </div>
          <figure style={{ margin: 0, order: mobile ? -1 : 0 }}>
            <div
              style={{
                height: mobile ? 240 : 340,
                borderRadius: 2,
                overflow: 'hidden',
                background: 'var(--surface-sunken)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--text-subtle)',
                fontSize: 'var(--text-xs)',
              }}
            >
              צילום {sp.name_he} · בהמתנה
            </div>
          </figure>
        </div>
      </Section>

      <Section narrow eyebrow="Ask" title={`שאלה על ${sp.name_he}`} lede="התשובה נבנית מהשיעורים והמאמרים במאגר, ומכוונת מראש למין הזה." style={{ marginTop: 'var(--space-11)' }}>
        <Ask compact scopeSpeciesLabel={sp.name_he} scopeSpeciesSlug={sp.slug} placeholder={`למשל: מתי לגזום ${sp.name_he}?`} onNavigate={onNavigate} />
      </Section>

      <Section eyebrow="Annual cycle" title="מחזור עבודה שנתי" action={<Badge tone="success" dot>פתוח לכולם</Badge>}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(64px,1fr))', borderTop: '1px solid var(--line-hairline)', borderBottom: '1px solid var(--line-hairline)' }}>
          {monthTags.map((tags, i) => {
            const isNow = i + 1 === curMonth;
            return (
              <div key={i} style={{ padding: 'var(--space-5) var(--space-3)', borderInlineStart: i ? '1px solid var(--line-hairline)' : 'none', background: isNow ? 'var(--surface-brand-soft)' : 'transparent', minHeight: 150 }}>
                <div style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: isNow ? 'var(--text-brand)' : 'var(--text-heading)' }}>{HE_MONTHS[i]}</div>
                {isNow ? <div style={{ ...EYE, fontSize: 'var(--text-3xs)', color: 'var(--text-brand)', marginTop: 2 }}>עכשיו</div> : <div style={{ height: 15, marginTop: 2 }} />}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginTop: 'var(--space-4)' }}>
                  {tags.map((t, ti) => (
                    <span key={ti} style={{ fontSize: 'var(--text-xs)', color: 'var(--text-body)', lineHeight: 1.3 }}>
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </Section>

      <Section eyebrow="This month" title="מה עושים עכשיו">
        <Card padding="0">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))' }}>
            <MonthBlock label="עכשיו" month={curMonth} actions={nowActions} />
            <div style={{ borderInlineStart: mobile ? 'none' : '1px solid var(--line-hairline)', borderTop: mobile ? '1px solid var(--line-hairline)' : 'none' }}>
              <MonthBlock label="החודש הבא" month={nextMonth} actions={nextActions} />
            </div>
          </div>
        </Card>
      </Section>

      {articles.length ? (
        <Section eyebrow="Related" title="מאמרים קשורים" action={<a href="#" onClick={(e) => { e.preventDefault(); onNavigate('articles'); }} style={{ fontSize: 'var(--text-sm)', fontWeight: 600, border: 0 }}>כל המאמרים</a>}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(260px,1fr))', gap: 'var(--space-6)' }}>
            {articles.map((a) => (
              <Card key={a.id} interactive onClick={() => onNavigate('article', { slug: a.slug })}>
                <div style={EYE}>מאמר</div>
                <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 400, marginTop: 'var(--space-4)' }}>{a.title_he}</h3>
                {a.lead_he ? <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginTop: 'var(--space-3)', lineHeight: 1.7 }}>{a.lead_he}</p> : null}
                <div style={{ marginTop: 'var(--space-6)', display: 'flex', alignItems: 'center', gap: 6, fontSize: 'var(--text-sm)', fontWeight: 600, color: 'var(--text-link)' }}>
                  לקריאה <Icon name="arrow-left" size={16} />
                </div>
              </Card>
            ))}
          </div>
        </Section>
      ) : null}
    </>
  );
}
