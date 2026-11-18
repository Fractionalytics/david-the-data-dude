// One clip per storyboard card, so a revised card is re-rendered on its own.
// Renders each card composition (id `card-NN`) as a transparent ProRes 4444 .mov to out/cards/<id>.mov,
// for laying over David's footage in CapCut. Name each composition `card-NN` after its storyboard card.
//   node render-cards.mjs                   every card, then the review preview
//   node render-cards.mjs card-06 card-11   just those cards (no preview)
//   node render-cards.mjs preview           just the review preview
//   node render-cards.mjs --out=out/cards-v2 card-06   write to another folder, e.g. when CapCut has the
//                                           old clips open (Windows then refuses to replace them: EPERM rename)
//   node render-cards.mjs --reel3 ...       the same for Reel 3 (src/reel3/, ids r3-card-NN and r3-preview,
//                                           default folder out/reel3/cards)
import {execSync} from 'node:child_process';

const args = process.argv.slice(2);
const r3 = args.includes('--reel3');
const entry = r3 ? 'src/reel3/index.ts ' : '';
const prefix = r3 ? 'r3-' : '';
const listing = execSync(`npx remotion compositions ${entry}`, {encoding: 'utf8'});
const all = [...listing.matchAll(new RegExp(`^(${prefix}card-\\d+)\\s`, 'gm'))].map((m) => m[1]);
const previewId = `${prefix}preview`;
const hasPreview = new RegExp(`^${previewId}\\s`, 'm').test(listing);
const outDir = (args.find((a) => a.startsWith('--out=')) ?? `--out=${r3 ? 'out/reel3/cards' : 'out/cards'}`).slice('--out='.length);
const asked = args.filter((a) => !a.startsWith('--'));
const unknown = asked.filter((id) => id !== previewId && !all.includes(id));
if (unknown.length) throw new Error(`No such card composition: ${unknown.join(', ')} (have: ${all.join(', ')})`);

const cards = asked.length ? asked.filter((id) => id !== previewId) : all;
for (const id of cards) {
	console.log(`=== ${id}`);
	execSync(
		`npx remotion render ${entry}${id} ${outDir}/${id}.mov --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png`,
		{stdio: 'inherit'},
	);
}
if (hasPreview && (!asked.length || asked.includes(previewId))) {
	console.log(`=== ${previewId}`);
	execSync(`npx remotion render ${entry}${previewId} ${outDir}/${previewId}.mp4 --codec=h264`, {stdio: 'inherit'});
}
