// Radiology's chart kit: the shared Sharpie look (shared/video-kit) plus this project's
// helpers. Charts import everything from here. Every chart lays out inside ZONES.chart.
import {setScrawlTilt} from '@kit/sharpie';

export * from '@kit/sharpie';
export {VIDEO, ZONES} from '@kit/zones';

// David wants handwritten text level on every chart: no random tilt.
setScrawlTilt(0);

// Fades a value in over [start, start + frames], clamped.
export const ramp = (frame: number, start: number, frames: number) =>
	Math.min(1, Math.max(0, (frame - start) / frames));
