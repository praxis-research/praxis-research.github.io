// Move figures between a page and a Claude Doc. A figure has one home at a
// time: the doc while a post is drafted, the page once it is published.
//
//   node bin/figures.mjs flatten <page.html> <outDir>
//     Each inline <svg> figure on the page -> <outDir>/fig<N>.svg, self-contained:
//     class rules become attributes and tokens become light-theme values,
//     because a doc strips <style> from an uploaded SVG. Do not commit these.
//
//   node bin/figures.mjs tokenize <figure.svg>
//     The reverse, for publishing: prints the SVG with every colour that matches
//     a design token written as var(--token), ready to paste into the page.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const [mode, src, outArg] = process.argv.slice(2);

const design = readFileSync(join(ROOT, 'assets/design.css'), 'utf8').replace(/\/\*[\s\S]*?\*\//g, '');
const lightBlock = design.match(/^:root \{([\s\S]*?)^\}/m);
if (!lightBlock) throw new Error('light token block not found in assets/design.css');
const tokens = Object.fromEntries([...lightBlock[1].matchAll(/--([a-z0-9-]+):\s*([^;]+);/g)]
  .map(([, name, value]) => [name, value.replace(/\s+/g, ' ').trim().replace(/"/g, "'")]));

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

const literal = (value) => value.replace(/var\(--([a-z0-9-]+)\)/g, (_, name) => {
  if (!(name in tokens)) throw new Error(`unknown token --${name}`);
  return tokens[name];
});

if (mode === 'flatten') {
  if (!src || !outArg) throw new Error('usage: figures.mjs flatten <page.html> <outDir>');
  const page = readFileSync(src, 'utf8');
  let pageCss = '';
  for (const m of page.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/gi)) pageCss += m[1] + '\n';
  // class -> declarations, later rules winning, as in the cascade
  const byClass = {};
  for (const [, selectors, body] of pageCss.replace(/\/\*[\s\S]*?\*\//g, '').matchAll(/^([.][^{}@]+)\{([^{}]*)\}/gm)) {
    const decls = [...body.matchAll(/([a-z-]+)\s*:\s*([^;]+);?/g)].map(([, p, v]) => [p, v.trim()]);
    for (const sel of selectors.split(',')) {
      const name = sel.trim().match(/^\.([A-Za-z0-9_-]+)$/)?.[1];
      if (name) Object.assign(byClass[name] ??= {}, Object.fromEntries(decls));
    }
  }

  const figures = [...page.matchAll(/<figure[^>]*>[\s\S]*?<\/figure>/gi)]
    .map(([figure]) => figure.match(/<svg[\s\S]*?<\/svg>/i)?.[0]).filter(Boolean);
  if (!figures.length) throw new Error(`no <figure> with an inline <svg> in ${src}`);
  const outDir = resolve(outArg);
  mkdirSync(outDir, { recursive: true });

  figures.forEach((svg, i) => {
    const viewBox = svg.match(/viewBox="([^"]+)"/)?.[1];
    if (!viewBox) throw new Error(`figure ${i + 1} has no viewBox`);
    const [x, y, w, h] = viewBox.split(/\s+/).map(Number);

    let out = toXml(svg).replace(/<([a-zA-Z]+)((?:\s+[^<>]*?)?)(\s*\/?)>/g, (whole, tag, attrs, close) => {
      const cls = attrs.match(/\sclass="([^"]*)"/);
      let rest = attrs.replace(/\sclass="[^"]*"/, '');
      if (cls) {
        const decls = {};
        for (const c of cls[1].split(/\s+/)) Object.assign(decls, byClass[c]);
        for (const [prop, value] of Object.entries(decls)) {
          rest = rest.replace(new RegExp(`\\s${prop}="[^"]*"`), '') + ` ${prop}="${value}"`;
        }
      }
      return `<${tag}${literal(rest)}${close}>`;
    });
    out = out.replace(/<svg([^>]*)>/, (_, attrs) =>
      `<svg xmlns="http://www.w3.org/2000/svg"${attrs.replace(/\s+xmlns="[^"]*"/, '')} width="${w}" height="${h}">\n` +
      `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${tokens.bg}"/>`);

    const file = join(outDir, `fig${i + 1}.svg`);
    writeFileSync(file, out + '\n');
    console.log(file);
  });
} else if (mode === 'tokenize') {
  if (!src) throw new Error('usage: figures.mjs tokenize <figure.svg>');
  let svg = readFileSync(src, 'utf8');
  const colours = Object.entries(tokens).filter(([, v]) => /^#|^rgba?\(/.test(v));
  for (const [name, value] of colours) svg = svg.split(`"${value}"`).join(`"var(--${name})"`);
  const left = [...new Set(svg.match(/"#[0-9a-fA-F]{3,8}"/g) ?? [])];
  if (left.length) console.error(`not a design token, fix by hand: ${left.join(' ')}`);
  process.stdout.write(svg);
} else {
  throw new Error('usage: figures.mjs flatten <page.html> <outDir> | tokenize <figure.svg>');
}
