import { Fragment } from 'react';
import { AbsoluteFill, Audio, getStaticFiles, interpolate, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { Caption } from './components';
import { clipSeconds, type Cue, type ExplainerProps } from './content';
import { INTRO_FRAMES, Intro, Outro, OUTRO_FRAMES } from './scenes/Cards';
import { CLIP_LEAD, CLIP_TAIL, PatreonClip } from './scenes/PatreonClip';
import { R, REAL_SITE_FRAMES as SITE_FLOW_FRAMES, RealSite } from './scenes/RealSite';
import { BODY, C, FPS } from './theme';

const XFADE = 15;

export function timeline(props: ExplainerProps) {
  const clipFrames = Math.round(clipSeconds(props.live) * FPS);
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
  const clipTo = clipFrom + Math.round(clipSeconds(props.live) * FPS);

  const files = new Set(getStaticFiles().map((x) => x.name));
  const soundtrack = props.soundtrack && (props.stem ?? 'mix') === 'mix' ? props.soundtrack : null;
  const stem = soundtrack ? 'none' : props.stem ?? 'mix';
  const voiceFile = (cue: Cue) => {
    if (stem === 'live' || stem === 'none') return null;
    if (props.rawVoice && files.has(`voice-raw/${cue}.wav`)) return `voice-raw/${cue}.wav`;
    const set = props.narration[cue].audio;
    if (set) return `voice/${set}`;
    return files.has(`voice/${cue}.mp3`) ? `voice/${cue}.mp3` : null;
  };

  // [cue, from, to] in absolute frames, anchored to the animation's own events.
  const cues: [Cue, number, number][] = [
    ['intro', 0, s + 25],
    ['locked', s + R.blocked + 10, s + R.clickLogin],
    ['check', s + R.clickLogin + 4, s + R.homeMember],
    ['ask', s + R.homeMember, s + R.clickAsk2 + 10],
    ['answer', s + R.stage0 + 10, s + R.answer + 100],
    ['toLive', s + R.answer + 100, s + SITE_FLOW_FRAMES - 8],
    ['patreon', p + 8, clipFrom],
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
          <RealSite />
        </FadeIn>
      </Sequence>

      <Sequence from={p} durationInFrames={tl.patreonFrames}>
        <FadeIn>
          <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 40%, #f1efed, ${C.stone300})` }} />
          <PatreonClip live={props.live} timestamp={timestamp} muteLive={stem === 'voice' || stem === 'none'} />
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

      {soundtrack ? <Audio src={staticFile(soundtrack)} /> : null}

      {props.music && stem === 'mix' ? (
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
