// Renders the Four Forces carousel to out/carousel/01.png-06.png, then the LinkedIn PDF.
// Slide 2 is the Reel's final four-forces frame, cropped to 4:5 by the shared kit.
// Run: node render-carousel.mjs
import {execSync} from 'node:child_process';
import {mkdirSync} from 'node:fs';

mkdirSync('out/carousel', {recursive: true});
const run = (cmd) => execSync(cmd, {stdio: 'ignore'});
run('npx remotion still carousel-01-title out/carousel/01.png --frame=0');
run('npx remotion still c17c-forces-slow out/carousel/02-final.png --frame=122');
run('python ../../../shared/video-kit/carousel_frame.py out/carousel/02-final.png out/carousel/02.png');
for (const i of [1, 2, 3, 4]) run(`npx remotion still carousel-0${i + 2}-force-${i} out/carousel/0${i + 2}.png --frame=0`);
console.log('slides done');
