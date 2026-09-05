import { useEffect, useRef, useState } from 'react';
import { Button, Dialog, Textarea, Toast } from '../../ds';
import { runSearch } from '../../lib/search';
import type { Navigate } from '../../types/route';
import { AskBox } from './AskBox';
import { ResultArea, type AskState } from './ResultArea';

export function Ask({
  initialQuery,
  autorun,
  compact,
  placeholder,
  onNavigate,
  scopeSpeciesLabel,
  scopeSpeciesSlug,
}: {
  initialQuery?: string;
  autorun?: boolean;
  compact?: boolean;
  placeholder?: string;
  onNavigate: Navigate;
  scopeSpeciesLabel?: string;
  scopeSpeciesSlug?: string;
}) {
  const [q, setQ] = useState(initialQuery || '');
  const [state, setState] = useState<AskState | null>(null);
  const [report, setReport] = useState(false);
  const [toast, setToast] = useState(false);
  const requestId = useRef(0);

  const ask = (text: string) => {
    if (!text.trim()) return;
    const query = scopeSpeciesLabel && !text.includes(scopeSpeciesLabel) ? `${text} ${scopeSpeciesLabel}` : text;
    setQ(text);
    setState({ kind: 'loading' });
    const id = ++requestId.current;
    runSearch(query).then((result) => {
      if (requestId.current === id) setState(result);
    });
  };

  useEffect(() => {
    if (autorun && initialQuery) ask(initialQuery);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(false), 3000);
      return () => clearTimeout(t);
    }
  }, [toast]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-7)' }}>
      <AskBox value={q} onChange={setQ} onSubmit={ask} placeholder={placeholder} compact={compact} />
      <ResultArea
        state={state}
        onAsk={ask}
        onNavigate={onNavigate}
        onReport={() => setReport(true)}
        compact={compact}
        scopeSpeciesLabel={scopeSpeciesLabel}
        scopeSpeciesSlug={scopeSpeciesSlug}
      />
      {report ? (
        <div style={{ position: 'fixed', inset: 0, zIndex: 60 }}>
          <Dialog
            open
            title="הנושא חסר במאגר"
            description={`השאלה: "${q || (state && state.kind !== 'loading' ? state.query : '') || ''}"`}
            onClose={() => setReport(false)}
            width={520}
            footer={
              <>
                <Button variant="ghost" size="sm" onClick={() => setReport(false)}>
                  ביטול
                </Button>
                <Button
                  size="sm"
                  onClick={() => {
                    setReport(false);
                    setToast(true);
                  }}
                >
                  שליחה
                </Button>
              </>
            }
          >
            <Textarea label="מה חיפשתם ולא מצאתם?" placeholder="כמה מילים על העץ, העונה והבעיה" rows={4} />
          </Dialog>
        </div>
      ) : null}
      {toast ? (
        <div style={{ position: 'fixed', bottom: 24, insetInlineStart: 24, zIndex: 50 }}>
          <Toast tone="success" onDismiss={() => setToast(false)}>
            תודה. ההערה נשמרה.
          </Toast>
        </div>
      ) : null}
    </div>
  );
}
