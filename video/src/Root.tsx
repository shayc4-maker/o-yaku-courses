import { Composition } from 'remotion';
import { defaultProps, narratedProps, type ExplainerProps } from './content';
import { Explainer, timeline } from './Explainer';
import { FPS, H, W } from './theme';

export function RemotionRoot() {
  // Explainer = live clip with its own sound; ExplainerNarrated = work shots with voice-over.
  return (
    <>
      {([['Explainer', defaultProps], ['ExplainerNarrated', narratedProps]] as const).map(([id, props]) => (
        <Composition
          key={id}
          id={id}
          component={Explainer}
          width={W}
          height={H}
          fps={FPS}
          durationInFrames={timeline(props).total}
          defaultProps={props}
          calculateMetadata={({ props: p }: { props: ExplainerProps }) => ({ durationInFrames: timeline(p).total })}
        />
      ))}
    </>
  );
}
