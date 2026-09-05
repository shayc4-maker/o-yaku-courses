import type { CSSProperties, SVGAttributes } from 'react';
import { ICONS, type IconName } from './icons';

export interface IconProps extends Omit<SVGAttributes<SVGSVGElement>, 'color'> {
  name: IconName | (string & {});
  size?: number;
  strokeWidth?: number;
  color?: string;
}

export function Icon({ name, size = 18, strokeWidth = 1.5, color = 'currentColor', style, ...rest }: IconProps) {
  const shape = ICONS[name as IconName];
  if (!shape && import.meta.env.DEV) {
    console.warn('[Icon] unknown icon: ' + name);
  }
  return (
    <svg
      aria-hidden="true"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{ display: 'block', flex: 'none', ...(style as CSSProperties) }}
      {...rest}
    >
      {shape}
    </svg>
  );
}
