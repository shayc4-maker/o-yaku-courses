import { Fragment } from 'react';
import { AbsoluteFill, Audio, getStaticFiles, interpolate, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { Caption } from './components';
import type { Cue, ExplainerProps } from './content';
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
  const clipFrom = p + CLIP_LEAD;
  const clipTo = clipFrom + Math.round(props.live.clipSeconds * FPS);

  const files = new Set(getStaticFiles().map((x) => x.name));
  const voiceFile = (cue: Cue) => {
    const set = props.narration[cue].audio;
    if (set) return `voice/${set}`;
    return files.has(`voice/${cue}.mp3`) ? `voice/${cue}.mp3` : null;
  };

  // [cue, from, to] in absolute frames, anchored to the animation's own events.
  const cues: [Cue, number, number][] = [
    ['intro', 8, s],
    ['locked', s + 15, s + T.clickConnect - 5],
    ['check', s + T.clickConnect, s + T.connected + 20],
    ['ask', s + T.connected + 30, s + T.clickSearch],
    ['answer', s + T.clickSearch + 6, s + 590],
    ['toLive', s + 596, s + SITE_FLOW_FRAMES - 10],
    ['patreon', p + 8, clipFrom + 45],
    ['outro', tl.outro + 10, tl.total],
  ];

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

      {/* captions + voice-over, one per cue */}
      {cues.map(([cue, from, to]) => {
        const line = props.narration[cue];
        const audio = voiceFile(cue);
        return (
          <Fragment key={cue}>
            {line.caption ? <Caption from={from} to={to} text={line.caption} /> : null}
            {audio ? (
              <Sequence from={from} layout="none">
                <Audio src={staticFile(audio)} />
              </Sequence>
            ) : null}
          </Fragment>
        );
      })}

      {props.music ? (
        <Audio
          src={staticFile(props.music)}
          volume={(f) => {
            const inClip = f >= clipFrom && f < clipTo;
            const underVoice = cues.some(([cue, a, b]) => voiceFile(cue) && f >= a && f < b);
            const fadeOut = interpolate(f, [tl.total - 45, tl.total], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
            return (inClip ? 0.03 : underVoice ? 0.08 : 0.22) * fadeOut;
          }}
        />
      ) : null}
    </AbsoluteFill>
  );
}
