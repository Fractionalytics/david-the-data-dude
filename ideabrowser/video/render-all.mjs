// Renders every composition to out/<id>.mp4. Run: npm run render:all
// Ids come from `remotion compositions`, so new charts are picked up automatically.
import {execSync} from 'node:child_process';

const listing = execSync('npx remotion compositions', {encoding: 'utf8'});
const ids = [...listing.matchAll(/^(\S+)\s+\d+\s+\d+x\d+\s+\d+ \(/gm)].map((m) => m[1]);
if (ids.length === 0) throw new Error('No compositions found in `remotion compositions` output');

for (const id of ids) {
  console.log(`\n=== ${id}`);
  execSync(`npx remotion render ${id} out/${id}.mp4`, {stdio: 'inherit'});
}
