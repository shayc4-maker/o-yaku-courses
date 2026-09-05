/**
 * No brand logo file was supplied with the design handoff (the prototype pointed at
 * assets/logo-oyaku.png / logo-oyaku-white.png placeholders that don't exist). Until a real
 * mark arrives, render a simple type wordmark using the design system's own display font so
 * the header/footer never ship a broken <img>. Swap this for an <img> once a logo file lands.
 */
export function Logo({ inverse = false, height = 44 }: { inverse?: boolean; height?: number }) {
  return (
    <span
      style={{
        fontFamily: 'var(--font-display)',
        fontWeight: 500,
        fontSize: height * 0.5,
        letterSpacing: '0.04em',
        lineHeight: 1,
        color: inverse ? 'var(--text-inverse)' : 'var(--text-heading)',
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
      }}
    >
      <span
        aria-hidden="true"
        style={{
          width: height * 0.36,
          height: height * 0.36,
          borderRadius: '50%',
          border: `2px solid ${inverse ? 'var(--stone-300)' : 'var(--clay-500)'}`,
          display: 'inline-block',
        }}
      />
      O-YAKU
    </span>
  );
}
