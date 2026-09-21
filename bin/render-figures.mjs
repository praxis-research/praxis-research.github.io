// Render standalone SVG figures to 2x PNG, light theme, for places that cannot
// show a styled SVG (a Claude Doc strips <style> from uploaded SVGs).
//   node bin/render-figures.mjs <outDir> <figure.svg>...
//
// Uses the locally installed Chrome; set CHROME to point somewhere else.
import { execFileSync } from 'node:child_process';
import { readFileSync, mkdirSync } from 'node:fs';
import { basename, join, resolve } from 'node:path';

const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const [outArg, ...files] = process.argv.slice(2);
if (!outArg || !files.length) throw new Error('usage: render-figures.mjs <outDir> <figure.svg>...');

const outDir = resolve(outArg);
mkdirSync(outDir, { recursive: true });

for (const file of files) {
  const size = readFileSync(file, 'utf8').match(/<svg[^>]*\swidth="(\d+)"[^>]*\sheight="(\d+)"/);
  if (!size) throw new Error(`${file}: <svg> needs integer width and height`);
  const out = join(outDir, basename(file, '.svg') + '.png');
  execFileSync(CHROME, [
    '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=2',
    '--blink-settings=preferredColorScheme=1', // 1 = light
    `--window-size=${size[1]},${size[2]}`, `--screenshot=${out}`, `file://${resolve(file)}`,
  ], { stdio: 'ignore', timeout: 60000 });
  console.log(out);
}
