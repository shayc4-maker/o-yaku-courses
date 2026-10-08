import { Composition } from 'remotion';
import { defaultProps, type ExplainerProps } from './content';
import { Explainer, timeline } from './Explainer';
import { FPS, H, W } from './theme';

export function RemotionRoot() {
  return (
    <Composition
      id="Explainer"
      component={Explainer}
      width={W}
      height={H}
      fps={FPS}
      durationInFrames={timeline(defaultProps).total}
      defaultProps={defaultProps}
      calculateMetadata={({ props }: { props: ExplainerProps }) => ({ durationInFrames: timeline(props).total })}
    />
  );
}
