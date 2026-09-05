import { Icon } from '../../ds';
import { EYE } from '../chrome/constants';
import { HE_MONTHS } from '../../lib/data';
import type { KnowledgeSegmentRow } from '../../types/db';

function segmentMeta(s: KnowledgeSegmentRow): string {
  const parts: string[] = [];
  if (s.month) parts.push(HE_MONTHS[s.month - 1]);
  if (s.season) parts.push(s.season);
  return parts.join(' · ');
}

export function SourceRow({ segment }: { segment: KnowledgeSegmentRow }) {
  const text = segment.summary || segment.content || '';
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-4)', padding: 'var(--space-4) 0', borderTop: '1px solid var(--line-hairline)' }}>
      <Icon name="file-text" size={16} color="var(--clay-600)" style={{ marginTop: 3 }} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 'var(--text-sm)', fontWeight: 600 }}>{segment.title || 'קטע ידע'}</div>
        {text ? (
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginTop: 4, lineHeight: 1.6 }}>
            {text.length > 220 ? text.slice(0, 220) + '…' : text}
          </p>
        ) : null}
      </div>
      {segmentMeta(segment) ? (
        <span style={{ ...EYE, whiteSpace: 'nowrap', fontSize: 'var(--text-3xs)' }}>{segmentMeta(segment)}</span>
      ) : null}
    </div>
  );
}
