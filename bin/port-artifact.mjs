// Restyle a standalone artifact onto the shared design system.
//   node bin/port-artifact.mjs <source.html> <slug> "<Title>" "<one-line summary>"
//
// The artifacts were already written against CSS variables, so this is a token
// swap rather than a rewrite: rename their variables onto ours, replace the
// three :root blocks with design.css's, and let every component inherit.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const [src, slug, title, summary] = process.argv.slice(2);
if (!src || !slug) throw new Error('usage: port-artifact.mjs <source.html> <slug> <title> <summary>');

let html = readFileSync(src, 'utf8');
const design = readFileSync(join(ROOT, 'assets/design.css'), 'utf8');

// Longest names first, so --surface-2 is not eaten by --surface.
const RENAME = [
  ['--surface-2', '--surface'], ['--rule-soft', '--rule'],
  ['--above-wash', '--pos-wash'], ['--below-wash', '--neg-wash'],
  ['--ground', '--bg'], ['--ink-2', '--ink'], ['--datum', '--muted'],
  ['--above', '--pos'], ['--below', '--neg'],
  ['--serif', '--font-body'], ['--mono', '--font-mono'],
];
for (const [from, to] of RENAME) html = html.replaceAll(from, to);

// Drop the artifact's own token blocks; design.css supplies them.
const dropBlock = (re) => { html = html.replace(re, ''); };
dropBlock(/:root\s*\{[^}]*\}/);
dropBlock(/:root:not\(\[data-theme="light"\]\)\s*\{[^}]*\}/);
dropBlock(/@media\s*\(prefers-color-scheme:\s*dark\)\s*\{\s*\}/);
dropBlock(/:root\[data-theme="dark"\]\s*\{[^}]*\}/);
// ...including any now-empty dark media wrapper left behind.
html = html.replace(/@media\s*\(prefers-color-scheme:\s*dark\)\s*\{\s*\}/g, '');

// design.css goes first so the document's own rules still win where they are
// doing real work (its components), while base typography comes from us.
html = html.replace(/(<style[^>]*>)/i, `<style>\n${design}\n--SPLIT--</style>\n$1`);
html = html.replace('--SPLIT--', '');

// A shadow token survives in a few rules; the system does not use shadows.
html = html.replace(/box-shadow:\s*var\(--shadow\)\s*;?/g, '');
html = html.replace(/--shadow:[^;]*;/g, '');

// Trim the display size so a note reads as a document, not a landing page.
html = html.replace(/font-size:\s*clamp\(2\.3rem,\s*6vw,\s*3\.4rem\)/g,
                    'font-size: clamp(1.6rem, 4vw, 2.1rem)');

// A way back to the site.
html = html.replace(/(<body[^>]*>)/i,
  `$1\n<p style="max-width:var(--container);margin:1.25rem auto 0;padding:0 1.5rem;font-size:0.9rem">` +
  `<a href="/notes/">← Praxis notes</a></p>`);

if (title) html = html.replace(/<title>[^<]*<\/title>/i, `<title>${title}</title>`);
if (summary && !/name="description"/i.test(html)) {
  html = html.replace(/(<\/title>)/i, `$1\n<meta name="description" content="${summary}">`);
}
// These are working notes, not publications: keep them out of search indexes.
html = html.replace(/(<\/title>)/i, `$1\n<meta name="robots" content="noindex, nofollow">`);

const dest = join(ROOT, 'static/notes', slug, 'index.html');
mkdirSync(dirname(dest), { recursive: true });
writeFileSync(dest, html);
console.log(`${src} -> static/notes/${slug}/ (${(html.length / 1024).toFixed(0)} KB)`);
