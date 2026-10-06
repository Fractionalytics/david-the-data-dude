// Renders every chart to out/<id>.mp4. Run: npm run render:all
import {execSync} from 'node:child_process';

const ids = ['hook-line', 'category-bars-jev', 'category-bars-forced', 'category-bars-detailed', 'season-stack', 'season-stack-100', 'season-stack-100-detailed', 'season-stack-100-simple', 'era-stack-100-simple', 'then-now-slope', 'then-now-seasons', 'then-now-endpoints', 'then-now-slope-combined', 'hook-line-steps', 'ddd-strike', 'd-words', 'category-morph'];
for (const id of ids) {
  console.log(`\n=== ${id}`);
  execSync(`npx remotion render ${id} out/${id}.mp4`, {stdio: 'inherit'});
}
