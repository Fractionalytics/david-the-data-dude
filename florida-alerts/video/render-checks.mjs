// Renders the key frames David's cues hang on, plus mid-animation frames, to out/checks/<id>-<frame>.png.
// Run: node render-checks.mjs [id ...]   (no ids = all). Bundles once, then renders each still.
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';

const CHECKS = {
	'card5-years-dots': [40, 300, 376, 386, 683, 698, 858, 868, 1066],
	'card6-found-by': [24, 295],
	'card7-channels': [24, 240],
	'card8-map': [0, 120, 190, 206, 318, 331, 480],
	'card9-takeaways': [56, 62, 172, 366, 372, 820],
};
const only = process.argv.slice(2);

const serveUrl = await bundle({
	entryPoint: path.resolve('src/index.ts'),
	webpackOverride: (config) => ({
		...config,
		resolve: {
			...config.resolve,
			alias: {...(config.resolve?.alias ?? {}), '@kit': path.resolve('../../../shared/video-kit/src')},
			modules: [path.resolve('node_modules'), 'node_modules'],
		},
	}),
});
for (const [id, frames] of Object.entries(CHECKS)) {
	if (only.length && !only.includes(id)) continue;
	const composition = await selectComposition({serveUrl, id});
	for (const frame of frames) {
		const output = `out/checks/${id}-${String(frame).padStart(4, '0')}.png`;
		await renderStill({composition, serveUrl, output, frame});
		console.log(output);
	}
}
