import { AbsoluteFill, interpolate, Sequence, useCurrentFrame } from 'remotion';
import { Caption } from './components';
import type { ExplainerProps } from './content';
import { INTRO_FRAMES, Intro, Outro, OUTRO_FRAMES } from './scenes/Cards';
import { CLIP_LEAD, CLIP_TAIL, PatreonClip } from './scenes/PatreonClip';
import { SITE_FLOW_FRAMES, SiteFlow, T } from './scenes/SiteFlow';
import { BODY, C, FPS } from './theme';

const XFADE = 15;

export function timeline(props: ExplainerProps) {
  const clipFrames = Math.round(props.live.clipSeconds * FPS);
  const site = INTRO_FRAMES - XFADE;
  const patreon = site + SITE_FLOW_FRAMES - XFADE;
  const patreonFrames = CLIP_LEAD + clipFrames + CLIP_TAIL;
  const outro = patreon + patreonFrames - XFADE;
  return { site, patreon, patreonFrames, outro, total: outro + OUTRO_FRAMES };
}

/** Cross-fades a scene in over its first XFADE frames. */
function FadeIn({ children }: { children: React.ReactNode }) {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{ opacity: interpolate(f, [0, XFADE], [0, 1], { extrapolateRight: 'clamp' }) }}>{children}</AbsoluteFill>;
}

export function Explainer(props: ExplainerProps) {
  const tl = timeline(props);
  const s = tl.site;
  const p = tl.patreon;
  const timestamp = props.sources.find((x) => x.live)?.live?.timestamp ?? '0:00';

  return (
    <AbsoluteFill style={{ background: C.stone200, fontFamily: BODY }}>
      <Sequence durationInFrames={INTRO_FRAMES}>
        <Intro />
      </Sequence>

      <Sequence from={s} durationInFrames={SITE_FLOW_FRAMES}>
        <FadeIn>
          <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 40%, ${C.stone100}, ${C.stone200})` }} />
          <SiteFlow question={props.question} sources={props.sources} />
        </FadeIn>
      </Sequence>

      <Sequence from={p} durationInFrames={tl.patreonFrames}>
        <FadeIn>
          <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 40%, #f1efed, ${C.stone300})` }} />
          <PatreonClip live={props.live} timestamp={timestamp} />
        </FadeIn>
      </Sequence>

      <Sequence from={tl.outro} durationInFrames={OUTRO_FRAMES}>
        <FadeIn>
          <Outro />
        </FadeIn>
      </Sequence>

      {/* captions, absolute frames */}
      <Caption from={s + 15} to={s + T.clickConnect - 5} text="מנוע השאלות פתוח למנויי O-YAKU ב-Patreon" />
      <Caption from={s + T.clickConnect} to={s + T.connected + 20} text="התחברות בלחיצה, ובדיקה קצרה שהמנוי פעיל" />
      <Caption from={s + T.connected + 30} to={s + T.clickSearch} text="עכשיו אפשר לשאול כל שאלה" />
      <Caption from={s + T.clickSearch + 6} to={s + 590} text="התשובה מגיעה עם מקורות מהשיעורים והלייבים" />
      <Caption from={s + 596} to={s + SITE_FLOW_FRAMES - 10} text="וכל מקור מוביל לרגע המדויק בלייב" />
      <Caption from={p + 8} to={p + CLIP_LEAD + 45} text={`הלייב נפתח בפטרון, בדיוק מ-${timestamp}`} />
    </AbsoluteFill>
  );
}
