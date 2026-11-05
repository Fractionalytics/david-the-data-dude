import path from 'node:path';
import {Config} from '@remotion/cli/config';

Config.setEntryPoint('./src/index.ts');
Config.setVideoImageFormat('jpeg');

// `@kit/...` imports the shared toolkit in shared/video-kit/src. Packages it imports (roughjs,
// @remotion/paths, fonts) resolve from this project's node_modules first; Remotion's own
// aliases, kept by the spread, already pin react and remotion.
const KIT = path.resolve(process.cwd(), '../../../shared/video-kit/src');
Config.overrideWebpackConfig((config) => ({
	...config,
	resolve: {
		...config.resolve,
		alias: {...(config.resolve?.alias ?? {}), '@kit': KIT},
		modules: [path.resolve(process.cwd(), 'node_modules'), 'node_modules'],
	},
}));
