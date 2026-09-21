// Turn the inline <svg> figures of a standalone page into standalone files.
//   node bin/extract-figures.mjs <page.html> <slug>
//
// Writes static/figures/<slug>/fig<N>.svg. An SVG loaded through <img> cannot
// see the page's stylesheet, so each file carries the colour tokens from
// design.css (light, and dark under prefers-color-scheme) plus the page's own
// rules for the classes the figure uses.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const [src, slug] = process.argv.slice(2);
if (!src || !slug) throw new Error('usage: extract-figures.mjs <page.html> <slug>');

const page = readFileSync(src, 'utf8');
const design = readFileSync(join(ROOT, 'assets/design.css'), 'utf8');

const light = design.match(/^:root \{[\s\S]*?^\}/m);
const dark = design.match(/^@media \(prefers-color-scheme: dark\) \{[\s\S]*?^\}/m);
if (!light || !dark) throw new Error('token blocks not found in assets/design.css');
const tokens = `${light[0]}\n${dark[0]}`.replace(/\/\*[\s\S]*?\*\//g, '');

let pageCss = '';
for (const m of page.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/gi)) pageCss += m[1] + '\n';
const rules = [...pageCss.replace(/\/\*[\s\S]*?\*\//g, '').matchAll(/^([.][^{}@]+)\{([^{}]*)\}/gm)]
  .map(([, selector, body]) => ({ selector: selector.trim(), body: body.trim() }));

// A standalone SVG is XML, which knows only five named entities.
const XML_ENTITIES = new Set(['amp', 'lt', 'gt', 'quot', 'apos']);
const HTML_ENTITIES = {
  minus: '−', plusmn: '±', times: '×', middot: '·', deg: '°',
  larr: '←', rarr: '→', uarr: '↑', darr: '↓',
  ldquo: '“', rdquo: '”', lsquo: '‘', rsquo: '’',
  ndash: '–', mdash: '—', hellip: '…',
  nbsp: ' ', thinsp: ' ', le: '≤', ge: '≥', Delta: 'Δ', mu: 'μ',
};
const toXml = (s) => s.replace(/&([A-Za-z][A-Za-z0-9]*);/g, (whole, name) => {
  if (XML_ENTITIES.has(name)) return whole;
  if (!(name in HTML_ENTITIES)) throw new Error(`unknown entity &${name}; — add it to HTML_ENTITIES`);
  return HTML_ENTITIES[name];
});

const outDir = join(ROOT, 'static/figures', slug);
mkdirSync(outDir, { recursive: true });

const figures = [...page.matchAll(/<figure[^>]*>[\s\S]*?<\/figure>/gi)]
  .map(([figure]) => figure.match(/<svg[\s\S]*?<\/svg>/i)?.[0])
  .filter(Boolean);
if (!figures.length) throw new Error(`no <figure> with an inline <svg> in ${src}`);

figures.forEach((svg, i) => {
  const used = new Set([...svg.matchAll(/class="([^"]+)"/g)].flatMap(([, c]) => c.split(/\s+/)));
  const css = rules
    .filter(({ selector }) => selector.split(',').some((s) => used.has(s.trim().replace(/^\./, ''))))
    .map(({ selector, body }) => `${selector} { ${body} }`)
    .join('\n');

  const viewBox = svg.match(/viewBox="([^"]+)"/)?.[1];
  if (!viewBox) throw new Error(`figure ${i + 1} has no viewBox`);
  const [x, y, w, h] = viewBox.split(/\s+/).map(Number);

  const out = toXml(svg).replace(/<svg([^>]*)>/i, (_, attrs) =>
    `<svg xmlns="http://www.w3.org/2000/svg"${attrs.replace(/\s+xmlns="[^"]*"/, '')} width="${w}" height="${h}">\n` +
    `<style>\n${tokens}\n${css}\n</style>\n` +
    `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="var(--bg)"/>`);

  const file = join(outDir, `fig${i + 1}.svg`);
  writeFileSync(file, out + '\n');
  console.log(`${file.slice(ROOT.length + 1)}  ${w}x${h}  ${used.size} classes`);
});
