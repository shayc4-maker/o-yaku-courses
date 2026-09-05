import { Button, Card, Tag } from '../../ds';
import { EYE } from '../chrome/constants';
import { SUGGESTED_QUESTIONS, type SearchResult } from '../../lib/search';
import { SourceRow } from './SourceRow';
import type { Navigate } from '../../types/route';

export type AskState = { kind: 'loading' } | SearchResult;

export function ResultArea({
  state,
  onAsk,
  onNavigate,
  onReport,
  compact,
  scopeSpeciesLabel,
  scopeSpeciesSlug,
}: {
  state: AskState | null;
  onAsk: (q: string) => void;
  onNavigate: Navigate;
  onReport: () => void;
  compact?: boolean;
  scopeSpeciesLabel?: string;
  scopeSpeciesSlug?: string;
}) {
  if (!state) {
    if (compact) return null;
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
        <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginInlineEnd: 'var(--space-2)' }}>שאלות לדוגמה</span>
        {SUGGESTED_QUESTIONS.map((q) => (
          <Tag key={q} onClick={() => onAsk(q)}>
            {q}
          </Tag>
        ))}
      </div>
    );
  }

  if (state.kind === 'loading') {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', padding: 'var(--space-7) 0', color: 'var(--text-muted)' }}>
        <span>מחפש במאגר הידע…</span>
      </div>
    );
  }

  if (state.kind === 'found') {
    return (
      <Card padding="var(--space-8)">
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
          <span style={EYE}>תוצאות</span>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-subtle)' }}>{state.segments.length} קטעי ידע רלוונטיים</span>
        </div>
        <h3 style={{ fontSize: 'var(--text-xl)', fontWeight: 400, marginTop: 'var(--space-4)' }}>{state.query}</h3>
        <div style={{ marginTop: 'var(--space-5)', borderBottom: '1px solid var(--line-hairline)' }}>
          {state.segments.map((s) => (
            <SourceRow key={s.id} segment={s} />
          ))}
        </div>
        {scopeSpeciesSlug && scopeSpeciesLabel && !compact ? (
          <div style={{ marginTop: 'var(--space-7)', display: 'flex', alignItems: 'center', gap: 'var(--space-5)', flexWrap: 'wrap' }}>
            <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>
              כל מה שצריך לדעת על {scopeSpeciesLabel}: מחזור עבודה שנתי ומה עושים החודש.
            </span>
            <span style={{ flex: 1 }} />
            <Button variant="secondary" size="sm" onClick={() => onNavigate('species', { slug: scopeSpeciesSlug })}>
              לעמוד המין
            </Button>
          </div>
        ) : null}
      </Card>
    );
  }

  // notfound
  return (
    <Card tone="sunken" padding="var(--space-8)">
      <div style={EYE}>אין תוצאות</div>
      <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 400, marginTop: 'var(--space-4)' }}>לא נמצאו קטעי ידע מתאימים לשאלה הזו.</h3>
      <p style={{ marginTop: 'var(--space-3)', color: 'var(--text-muted)', maxWidth: '58ch' }}>
        אנחנו מחפשים רק בתוך שיעורים ומאמרים שפורסמו. נסו ניסוח אחר, או עברו למאגר הידע לפי קטגוריה.
      </p>
      {scopeSpeciesSlug && scopeSpeciesLabel ? (
        <div style={{ marginTop: 'var(--space-6)' }}>
          <Button variant="secondary" size="sm" onClick={() => onNavigate('species', { slug: scopeSpeciesSlug })}>
            לעמוד {scopeSpeciesLabel}
          </Button>
        </div>
      ) : null}
      <div style={{ marginTop: 'var(--space-7)', display: 'flex', alignItems: 'center', gap: 'var(--space-5)', paddingTop: 'var(--space-6)', borderTop: '1px solid var(--line-hairline)', flexWrap: 'wrap' }}>
        <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>הערות כאלה מכוונות אילו שיעורים נכתבים הבאים.</span>
        <span style={{ flex: 1 }} />
        <Button variant="ghost" size="sm" onClick={onReport}>
          הנושא חסר? שלחו לנו הערה
        </Button>
      </div>
    </Card>
  );
}
