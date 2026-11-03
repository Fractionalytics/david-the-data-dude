// One clip per storyboard card, so a revised card is re-rendered on its own.
// Renders each card composition (id `card-NN`) as a transparent ProRes 4444 .mov to out/cards/<id>.mov,
// for laying over David's footage in CapCut. Name each composition `card-NN` after its storyboard card.
//   node render-cards.mjs                   every card, then the review preview
//   node render-cards.mjs card-06 card-11   just those cards (no preview)
//   node render-cards.mjs preview           just the review preview
//   node render-cards.mjs --out=out/cards-v2 card-06   write to another folder, e.g. when CapCut has the
//                                           old clips open (Windows then refuses to replace them: EPERM rename)
import {execSync} from 'node:child_process';

const listing = execSync('npx remotion compositions', {encoding: 'utf8'});
const all = [...listing.matchAll(/^(card-\d+)\s/gm)].map((m) => m[1]);
const hasPreview = /^preview\s/m.test(listing);
const args = process.argv.slice(2);
const outDir = (args.find((a) => a.startsWith('--out=')) ?? '--out=out/cards').slice('--out='.length);
const asked = args.filter((a) => !a.startsWith('--out='));
const unknown = asked.filter((id) => id !== 'preview' && !all.includes(id));
if (unknown.length) throw new Error(`No such card composition: ${unknown.join(', ')} (have: ${all.join(', ')})`);

const cards = asked.length ? asked.filter((id) => id !== 'preview') : all;
for (const id of cards) {
	console.log(`=== ${id}`);
	execSync(
		`npx remotion render ${id} ${outDir}/${id}.mov --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png`,
		{stdio: 'inherit'},
	);
}
if (hasPreview && (!asked.length || asked.includes('preview'))) {
	console.log('=== preview');
	execSync(`npx remotion render preview ${outDir}/preview.mp4 --codec=h264`, {stdio: 'inherit'});
}
