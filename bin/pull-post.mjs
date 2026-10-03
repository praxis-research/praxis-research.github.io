// Derive a standalone blog post in static/ from its read-only artifact.
//   node bin/pull-post.mjs <artifact-index.html> <slug> [<figs-dir>]
//
// The artifact is the source of truth for the post: prose, figure code and
// data all live in its page. This script is the only step between it and the
// site, so the published page is a strict downstream. It
//   - keeps the artifact's own CSS (everything after its "this page" marker)
//     and its body (inside <main class="doc">) and scripts, unchanged;
//   - drops the artifact's inlined copy of design.css and links the site's
//     stylesheets instead, so a change to assets/ reaches this page too;
//   - takes the title and summary from the post's entry in content/blog.json;
//   - rewrites figure paths from figs/ to /figures/<slug>/, and copies the
//     images there when a directory of them is given.
// Get the inputs from the artifact: its page is the file "index.html", its
// images are the published files under figs/.
import { readFileSync, writeFileSync, mkdirSync, readdirSync, copyFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const [src, slug, figsDir] = process.argv.slice(2);
if (!src || !slug) throw new Error('usage: pull-post.mjs <artifact-index.html> <slug> [<figs-dir>]');

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const site = JSON.parse(readFileSync(join(ROOT, 'site.config.json'), 'utf8'));
const url = `/${slug}`;
const entry = JSON.parse(readFileSync(join(ROOT, 'content/blog.json'), 'utf8')).find((p) => p.url === url);
if (!entry) throw new Error(`no entry with url ${url} in content/blog.json — add it first`);

let page = readFileSync(src, 'utf8');
// the artifact runtime wraps the page in a skeleton; keep only what is inside <body>
const bodyMatch = page.match(/<body[^>]*>([\s\S]*)<\/body>/i);
if (bodyMatch) page = bodyMatch[1];

const style = page.match(/<style>([\s\S]*?)<\/style>/);
const marker = style && style[1].indexOf('/* === this page');
if (!style || marker < 0) throw new Error('the artifact page needs one <style> whose post-specific rules start with a "/* === this page" comment');
const postCss = style[1].slice(marker)
  .replace(/^\.doc \{[^\n]*\n/m, '')                 // the site's .content column replaces the artifact's .doc
  .replace(/^\.doc > /gm, '.content > ');

const main = page.match(/<main class="doc">([\s\S]*?)<\/main>/);
if (!main) throw new Error('the artifact page needs <main class="doc">…</main> around the post');
const body = main[1].trim().replaceAll('src="figs/', `src="/figures/${slug}/`);
const scripts = page.slice(page.indexOf('</main>') + 7).trim();


const nav = site.nav.map((n) => `<a href="${n.href}">${esc(n.label)}</a>`).join('\n        ');
const title = `${entry.title} — ${site.title}`;
const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(entry.summary)}">
<link rel="canonical" href="${site.url}${url}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(entry.summary)}">
<meta property="og:url" content="${site.url}${url}">
<meta property="og:site_name" content="${esc(site.title)}">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary">
<link rel="alternate" type="application/rss+xml" title="${esc(site.title)}" href="/feed.xml">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">

<link rel="stylesheet" href="/assets/design.css">
<link rel="stylesheet" href="/assets/style.css">
<style>
/* === this post: from its artifact, unchanged === */
${postCss.trim()}
.content { max-width: var(--container); }
</style>
</head>
<body>

<header class="site-header">
  <div class="container">
    <a class="brand" href="/">${esc(site.title)}</a>
    <nav class="site-nav">
        ${nav}
    </nav>
  </div>
</header>
<main class="container">
<article class="content">

${body}

</article>
</main>
<footer class="site-footer">
  <div class="container">
    <p>${esc(site.footerNote)}</p>
  </div>
</footer>
${scripts}
</body></html>
`;

const dest = join(ROOT, 'static', `${slug}.html`);
writeFileSync(dest, html);
console.log(`${src} -> static/${slug}.html (${(html.length / 1024).toFixed(0)} KB)`);

if (figsDir) {
  const out = join(ROOT, 'static/figures', slug);
  mkdirSync(out, { recursive: true });
  const files = readdirSync(figsDir).filter((f) => /\.(png|svg|jpg|webp)$/i.test(f));
  for (const f of files) copyFileSync(join(figsDir, f), join(out, f));
  console.log(`${files.length} images -> static/figures/${slug}/`);
}
console.log('next: npm run check');
