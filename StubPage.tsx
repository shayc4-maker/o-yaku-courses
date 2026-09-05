import { Button } from '../../ds';
import type { Navigate } from '../../types/route';
import { EYE } from './constants';
import { Section } from './Section';

export function StubPage({ title, onNavigate }: { title: string; onNavigate: Navigate }) {
  return (
    <Section narrow style={{ minHeight: 360 }}>
      <div style={EYE}>עמוד בבנייה</div>
      <h1 style={{ fontSize: 'var(--text-3xl)', fontWeight: 300, marginTop: 'var(--space-4)' }}>{title}</h1>
      <p style={{ marginTop: 'var(--space-5)', color: 'var(--text-muted)' }}>העמוד הזה עדיין לא זמין.</p>
      <div style={{ marginTop: 'var(--space-7)' }}>
        <Button variant="secondary" onClick={() => onNavigate('home')}>
          חזרה לבית
        </Button>
      </div>
    </Section>
  );
}
