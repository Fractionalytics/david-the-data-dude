// Renders mid-animation check frames (the playbook's "final frames hide timing bugs") to
// out/check/<id>_<frame>.png. Run: node render-checks.mjs
import {execSync} from 'node:child_process';

const CHECKS = [
	['c07-waterfall-ceiling', 12], ['c07-waterfall-ceiling', 345], ['c08-waterfall-pretrend', 65],
	['c10-waterfall-remaining', 217], ['c11-top-declines', 150], ['c14-forces-list', 170],
	['c14-forces-list', 861], ['c15-forces-table', 12], ['c15-forces-table', 200],
	['c16a-office-vs-rest', 60], ['c17a-radiology-grid', 70], ['c17b-paralegals', 100],
	['c17c-forces-slow', 122], ['c19-call-centers-square', 100], ['c19-call-centers-square', 333],
];
for (const [id, frame] of CHECKS) {
	console.log(`=== ${id} @ ${frame}`);
	execSync(`npx remotion still ${id} out/check/${id}_${frame}.png --frame=${frame}`, {stdio: 'ignore'});
}
