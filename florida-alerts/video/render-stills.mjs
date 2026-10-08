// Renders the last frame of every composition to out/stills/<id>.png. Run: npm run stills
// Durations come from `remotion compositions`, so new or retimed videos are picked up automatically.
import {execSync} from 'node:child_process';

const listing = execSync('npx remotion compositions', {encoding: 'utf8'});
const comps = [...listing.matchAll(/^(\S+)\s+\d+\s+\d+x\d+\s+(\d+) \(/gm)].map((m) => ({id: m[1], frames: Number(m[2])}));
if (comps.length === 0) throw new Error('No compositions found in `remotion compositions` output');

for (const {id, frames} of comps) {
  console.log(`=== ${id} (frame ${frames - 1})`);
  execSync(`npx remotion still ${id} out/stills/${id}.png --frame=${frames - 1}`, {stdio: 'inherit'});
}
