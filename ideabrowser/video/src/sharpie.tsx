// Ideabrowser's chart kit: the shared Sharpie look (shared/video-kit) plus this project's
// colors. Charts import everything from here. Every chart lays out inside ZONES.chart.
import {INK} from '@kit/sharpie';

export * from '@kit/sharpie';
export {VIDEO, ZONES} from '@kit/zones';

// One color per business type, used the same way on every chart.
export const TYPE_INK = {
	service: INK.red,
	software: INK.blue,
	other: '#d9d9d6',
};

// Fades a value in over [start, start + frames], clamped.
export const ramp = (frame: number, start: number, frames: number) =>
	Math.min(1, Math.max(0, (frame - start) / frames));
