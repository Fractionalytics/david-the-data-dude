// The pencil hand for the "Audit" label, vendored like the kit's fonts so a render never reaches
// the network. Caveat (SIL OFL) stands in until David picks the pencil font.
import {continueRender, delayRender} from 'remotion';
import caveat600 from '../fonts/Caveat-600.woff2';

export const pencil = 'Caveat';

if (typeof document !== 'undefined') {
	const handle = delayRender('Loading pencil font');
	new FontFace(pencil, `url(${caveat600})`, {weight: '600'})
		.load()
		.then((loaded) => {
			document.fonts.add(loaded);
			continueRender(handle);
		})
		.catch((err) => {
			console.error('Pencil font failed to load', err);
			continueRender(handle);
		});
}
