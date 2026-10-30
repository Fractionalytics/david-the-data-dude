// Altman vs. Almonds chart kit: the shared Sharpie look (shared/video-kit) on Box Office's
// off-white Screenplay background. Charts import everything from here.
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {setScrawlTilt} from '@kit/sharpie';
import {VIDEO, ZoneGuide} from '@kit/zones';

export * from '@kit/sharpie';
export {VIDEO, ZONES} from '@kit/zones';

// Level handwritten text, as on Radiology.
setScrawlTilt(0);

export const BG = '#f3ecdc'; // Screenplay, from projects/box-office/video/src/theme.ts
export const MUTED = '#52514e'; // secondary text; clears 7:1 on BG

// Fades a value in over [start, start + frames], clamped.
export const ramp = (frame: number, start: number, frames: number) =>
	Math.min(1, Math.max(0, (frame - start) / frames));

// The kit's Page on the off-white background instead of white, with the same marker-edge filter.
// `bgBottom` stops the background there and leaves the rest transparent: the traditional cards
// end it at the caption band (1150) so David's caption and face show through below.
export const Page: React.FC<{children: React.ReactNode; bgBottom?: number}> = ({children, bgBottom = VIDEO.height}) => (
	<AbsoluteFill>
		<div style={{position: 'absolute', top: 0, left: 0, width: VIDEO.width, height: bgBottom, backgroundColor: BG}} />
		<svg style={{position: 'absolute'}} width={VIDEO.width} height={VIDEO.height} viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`}>
			<defs>
				<filter id="marker-edge" filterUnits="userSpaceOnUse" x={0} y={0} width={VIDEO.width} height={VIDEO.height}>
					<feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves={1} seed={3} result="noise" />
					<feDisplacementMap in="SourceGraphic" in2="noise" scale={2.5} />
				</filter>
			</defs>
			{children}
		</svg>
		<ZoneGuide />
	</AbsoluteFill>
);
