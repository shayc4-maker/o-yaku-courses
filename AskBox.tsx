import { Button, Input } from '../../ds';

export function AskBox({
  value,
  onChange,
  onSubmit,
  placeholder,
  compact,
}: {
  value: string;
  onChange: (v: string) => void;
  onSubmit: (v: string) => void;
  placeholder?: string;
  compact?: boolean;
}) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(value);
      }}
      style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'stretch' }}
    >
      <Input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || 'למשל: מתי לגזום זית? איך עובדים על שורשים?'}
        wrapperStyle={{ flex: 1 }}
        style={{ height: compact ? 42 : 52, fontSize: compact ? 'var(--text-md)' : 'var(--text-lg)' }}
      />
      <Button size={compact ? 'md' : 'lg'} style={{ height: compact ? 42 : 52 }}>
        חפש
      </Button>
    </form>
  );
}
