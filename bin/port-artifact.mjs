// Restyle a standalone artifact onto the shared design system and wrap it in a
// real HTML document.
//   node bin/port-artifact.mjs <source.html> <slug> "<Title>" "<summary>"
//
// Artifacts are authored as FRAGMENTS: no doctype, no <html>, no <head>, no
// <body>. The artifact runtime supplies that skeleton at publish time — which
// is where the viewport meta comes from. Serve the fragment as a file and
// phones render it at a ~980px virtual viewport and zoom out, so the
// document's own max-width:760px rules never fire. Hence: build the skeleton.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const [src, slug, titleArg, summary] = process.argv.slice(2);
if (!src || !slug) throw new Error('usage: port-artifact.mjs <source.html> <slug> <title> <summary>');

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

let frag = readFileSync(src, 'utf8');
const design = readFileSync(join(ROOT, 'assets/design.css'), 'utf8');

// 1. pull the pieces apart
const titleMatch = frag.match(/<title>([^<]*)<\/title>/i);
const title = titleArg || (titleMatch ? titleMatch[1] : slug);
frag = frag.replace(/<title>[^<]*<\/title>/i, '');

let styles = '';
frag = frag.replace(/<style[^>]*>([\s\S]*?)<\/style>/gi, (_, css) => { styles += css + '\n'; return ''; });

// If the fragment already carries a skeleton, keep only what is inside <body>.
const bodyMatch = frag.match(/<body[^>]*>([\s\S]*)<\/body>/i);
if (bodyMatch) frag = bodyMatch[1];
frag = frag.replace(/<\/?(?:!doctype|html|head)[^>]*>/gi, '').trim();

// 2. map the artifact's tokens onto the system's. Longest names first, so
//    --surface-2 is not eaten by --surface.
const RENAME = [
  ['--surface-2', '--surface'], ['--rule-soft', '--rule'],
  ['--above-wash', '--pos-wash'], ['--below-wash', '--neg-wash'],
  ['--ground', '--bg'], ['--ink-2', '--ink'], ['--datum', '--muted'],
  ['--above', '--pos'], ['--below', '--neg'],
  ['--serif', '--font-body'], ['--mono', '--font-mono'],
];
for (const [from, to] of RENAME) { styles = styles.replaceAll(from, to); frag = frag.replaceAll(from, to); }

// 3. drop the artifact's own token blocks; design.css supplies them
styles = styles
  .replace(/:root\s*\{[^}]*\}/, '')
  .replace(/:root:not\(\[data-theme="light"\]\)\s*\{[^}]*\}/, '')
  .replace(/:root\[data-theme="dark"\]\s*\{[^}]*\}/, '')
  .replace(/@media\s*\(prefers-color-scheme:\s*dark\)\s*\{\s*\}/g, '')
  .replace(/box-shadow:\s*var\(--shadow\)\s*;?/g, '')
  .replace(/--shadow:[^;]*;/g, '');

// 4. a note is a document, not a landing page
styles = styles.replace(/font-size:\s*clamp\(2\.3rem,\s*6vw,\s*3\.4rem\)/g,
                        'font-size: clamp(1.6rem, 4vw, 2.1rem)');

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
${summary ? `<meta name="description" content="${esc(summary)}">` : ''}
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<style>
${design}
</style>
<style>
${styles.trim()}
</style>
</head>
<body>
<p style="max-width:1080px;margin:1.25rem auto 0;padding:0 20px;font-size:0.9rem">
<a href="/notes/">← Praxis notes</a></p>
${frag}
</body>
</html>
`;

const dest = join(ROOT, 'static/notes', slug, 'index.html');
mkdirSync(dirname(dest), { recursive: true });
writeFileSync(dest, html);
console.log(`${src} -> static/notes/${slug}/ (${(html.length / 1024).toFixed(0)} KB)`);
