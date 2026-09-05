import { useEffect, useMemo, useState } from 'react';
import { Card, Divider, Icon } from '../ds';
import { Ask } from '../components/search/Ask';
import { EYE } from '../components/chrome/constants';
import { Section } from '../components/chrome/Section';
import { listSpecies } from '../lib/data';
import type { Navigate, RouteParams } from '../types/route';
import type { SpeciesRow } from '../types/db';

const CATEGORIES: { id: string; name: string; desc: string }[] = [
  { id: 'deciduous_broadleaf', name: 'רחבי עלים נשירים', desc: 'אולמוס, זלקובה, מיש, אלון התבור ומינים נוספים' },
  { id: 'evergreen_broadleaf', name: 'רחבי עלים ירוקי עד', desc: 'זיתים, פיקוסים ומינים ירוקי־עד נוספים' },
  { id: 'conifer', name: 'מחטניים', desc: 'אורנים, ערערים ומחטניים אחרים' },
];

export function Knowledge({ params, onNavigate }: { params: RouteParams; onNavigate: Navigate }) {
  const [species, setSpecies] = useState<SpeciesRow[] | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    listSpecies()
      .then((rows) => {
        if (!cancelled) setSpecies(rows);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const byCategory = useMemo(() => {
    const map = new Map<string, SpeciesRow[]>();
    for (const s of species || []) {
      const list = map.get(s.category || '') || [];
      list.push(s);
      map.set(s.category || '', list);
    }
    return map;
  }, [species]);

  return (
    <>
      <Section narrow style={{ marginTop: 'var(--space-11)' }}>
        <div style={EYE}>Knowledge base</div>
        <h1 style={{ fontSize: 'var(--text-3xl)', fontWeight: 300, marginTop: 'var(--space-4)' }}>מאגר הידע</h1>
        <p style={{ marginTop: 'var(--space-4)', color: 'var(--text-muted)' }}>כתבו שאלה או נושא מתחום הבונסאי. התוצאות מופיעות מיד מתחת לשורת החיפוש.</p>
        <div style={{ marginTop: 'var(--space-8)' }}>
          <Ask key={params.q || ''} initialQuery={params.q} autorun={!!params.q} onNavigate={onNavigate} />
        </div>
      </Section>

      <Section style={{ marginTop: 'var(--space-12)' }}>
        <Divider label="או גלוש לפי קטגוריה" />
        <p style={{ textAlign: 'center', fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginTop: 'var(--space-5)' }}>
          הקטגוריות הן דרך חלופית לגלוש במאגר ואינן חלק מתוצאות החיפוש.
        </p>
        {error ? (
          <p style={{ textAlign: 'center', color: 'var(--status-danger-fg)', marginTop: 'var(--space-7)' }}>לא הצלחנו לטעון את רשימת המינים כרגע.</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(240px,1fr))', gap: 'var(--space-6)', marginTop: 'var(--space-9)' }}>
            {CATEGORIES.map((c) => {
              const list = byCategory.get(c.id) || [];
              return (
                <Card key={c.id} padding="var(--space-8)">
                  <h3 style={{ fontSize: 'var(--text-xl)', fontWeight: 400 }}>{c.name}</h3>
                  <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginTop: 'var(--space-3)', lineHeight: 1.7 }}>{c.desc}</p>
                  <div style={{ marginTop: 'var(--space-6)', display: 'flex', alignItems: 'center', gap: 6, fontSize: 'var(--text-sm)', fontWeight: 600, color: 'var(--text-link)' }}>
                    למינים <Icon name="arrow-left" size={16} /><span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>{list.length ? `${list.length}` : species ? '0' : '…'}</span>
                  </div>
                  <div style={{ marginTop: 'var(--space-6)', borderTop: '1px solid var(--line-hairline)' }}>
                    {list.slice(0, 3).map((s) => (
                      <a
                        key={s.id}
                        href="#"
                        onClick={(e) => {
                          e.preventDefault();
                          onNavigate('species', { slug: s.slug });
                        }}
                        style={{ display: 'flex', alignItems: 'center', padding: 'var(--space-4) 0', borderBottom: '1px solid var(--line-hairline)', color: 'var(--text-body)', fontSize: 'var(--text-sm)' }}
                      >
                        <span style={{ flex: 1 }}>{s.name_he}</span>
                        <Icon name="arrow-left" size={16} color="var(--text-subtle)" />
                      </a>
                    ))}
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </Section>
    </>
  );
}
