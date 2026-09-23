#!/usr/bin/env node
// The entire site generator. Reads `content/`, writes `dist/`.
// Run `npm run build`. Run `npm run check` to build and validate links.

import { readFileSync, writeFileSync, readdirSync, mkdirSync, rmSync, cpSync, existsSync, statSync } from 'node:fs';
import { join, dirname, basename, extname, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { marked } from 'marked';

const ROOT = dirname(fileURLToPath(import.meta.url));
const SRC = join(ROOT, 'content');
const OUT = join(ROOT, 'dist');
const CHECK = process.argv.includes('--check');

const site = JSON.parse(readFileSync(join(ROOT, 'site.config.json'), 'utf8'));

/* ---------------------------------------------------------------- helpers */

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const slug = (s) => String(s).toLowerCase().trim()
  .replace(/[^\w\s-]/g, '').replace(/\s+/g, '-').replace(/-+/g, '-');

// Frontmatter: a deliberately small YAML subset — `key: value`, one per line,
// optional single or double quotes. No nesting, no lists. Keep it that way.
function parseFrontmatter(raw) {
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!m) return { data: {}, body: raw };
  const data = {};
  for (const line of m[1].split(/\r?\n/)) {
    if (!line.trim() || line.trim().startsWith('#')) continue;
    const i = line.indexOf(':');
    if (i === -1) throw new Error(`bad frontmatter line: ${line}`);
    const key = line.slice(0, i).trim();
    let val = line.slice(i + 1).trim();
    if (/^".*"$/.test(val) || /^'.*'$/.test(val)) val = val.slice(1, -1);
    data[key] = val;
  }
  return { data, body: raw.slice(m[0].length) };
}

// {{name}} is replaced from page frontmatter first, then site config.
function interpolate(text, scope) {
  return text.replace(/\{\{(\w+)\}\}/g, (whole, key) =>
    key in scope ? scope[key] : (key in site ? site[key] : whole));
}

// Stylesheets are cached by the host for hours; a content hash in the query
// string makes a style change show up on the next page load.
const assetVersion = createHash('sha1')
  .update(readFileSync(join(ROOT, 'assets', 'design.css')))
  .update(readFileSync(join(ROOT, 'assets', 'style.css')))
  .digest('hex').slice(0, 8);

function walkFiles(dir) {
  return readdirSync(dir).flatMap((name) => {
    const p = join(dir, name);
    return statSync(p).isDirectory() ? walkFiles(p) : [p];
  });
}

function formatDate(iso) {
  const [y, m, d] = String(iso).split('-').map(Number);
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
    'August', 'September', 'October', 'November', 'December'];
  return `${months[m - 1]} ${y}`;   // month and year only; the exact day is not shown
}

/* ------------------------------------------------------------- markdown */

// Heading ids, so any section can be deep-linked.
marked.use({
  gfm: true,
  renderer: {
    heading({ tokens, depth }) {
      const text = this.parser.parseInline(tokens);
      const id = slug(text.replace(/<[^>]+>/g, ''));
      return `<h${depth} id="${id}">${text}</h${depth}>\n`;
    },
    image({ href, title, text }) {
      const cap = text ? `<figcaption>${text}</figcaption>` : '';
      return `<figure><img src="${href}" alt="${esc(text)}"${title ? ` title="${esc(title)}"` : ''} loading="lazy">${cap}</figure>`;
    },
  },
});

const md = (text, scope = {}) => marked.parse(interpolate(text, scope));

// `Name — role` inside a list item: the tail becomes muted metadata.
function splitMeta(html) {
  return html.replace(/(<(li|p)>)([\s\S]*?)(<\/\2>)/g, (whole, open, tag, inner, close) => {
    const i = inner.indexOf(' — ');
    if (i === -1) return whole;
    return `${open}${inner.slice(0, i)}<span class="meta">${inner.slice(i + 3)}</span>${close}`;
  });
}

/* --------------------------------------------------------------- loading */


function loadPage(name) {
  const file = join(SRC, `${name}.md`);
  const { data, body } = parseFrontmatter(readFileSync(file, 'utf8'));
  const url = name === 'index' ? '/' : `/${name}/`;
  return { ...data, slug: name, url, body, source: `content/${name}.md` };
}

/* ---------------------------------------------------------------- layout */

function shell(page, inner) {
  const nav = site.nav.map((n) => {
    const active = n.href === page.url ||
      (n.href !== '/' && page.url.startsWith(n.href)) ? ' class="active"' : '';
    return `<a href="${n.href}"${active}>${esc(n.label)}</a>`;
  }).join('\n        ');

  const title = page.url === '/' ? site.title : `${page.title} — ${site.title}`;
  const desc = page.summary || site.description;
  const canonical = site.url + page.url;

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
<link rel="canonical" href="${canonical}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${canonical}">
<meta property="og:site_name" content="${esc(site.title)}">
<meta property="og:type" content="${page.date ? 'article' : 'website'}">
<meta name="twitter:card" content="summary">${page.noindex ? '\n<meta name="robots" content="noindex, nofollow">' : ''}
<link rel="alternate" type="application/rss+xml" title="${esc(site.title)}" href="/feed.xml">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/design.css?v=${assetVersion}">
<link rel="stylesheet" href="/assets/style.css?v=${assetVersion}">
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
${inner}
</main>
<footer class="site-footer">
  <div class="container">
    <p>${esc(site.footerNote)}</p>
  </div>
</footer>
</body>
</html>
`;
}

/* --------------------------------------------------------------- layouts */

const layouts = {
  home: (page) => `<article class="content home">
${md(page.body, page)}
</article>`,

  page: (page) => `<article class="content">
<h1>${esc(page.title)}</h1>
${md(page.body, page)}
</article>`,

  people: (page) => `<article class="content people">
${splitMeta(md(page.body, page))}
</article>`,

  'notes-index': (page, ctx) => {
    const items = ctx.notes.map((n) => `  <li>
    <h2><a href="/notes/${n.slug}/">${esc(n.title)}</a></h2>
    ${n.summary ? `<p class="summary">${esc(n.summary)}</p>` : ''}
  </li>`).join('\n');
    return `<article class="content">
<h1>${esc(page.title)}</h1>
${md(page.body, page)}
${items ? `<ul class="post-list">\n${items}\n</ul>` : '<p class="summary">No notes yet.</p>'}
</article>`;
  },

  'blog-index': (page, ctx) => {
    // One entry: title with a venue pill on the right (only for a published
    // venue; a "note" such as oral or spotlight joins the pill), then authors
    // (the date is kept for the feed, not shown), then the one-line summary.
    const entry = (p) => `  <li class="entry">
    <div class="entry-head">
      <h2><a href="${p.url}">${esc(p.title)}</a></h2>
      ${p.venue ? `<span class="pill${p.note ? ' pill--note' : ''}">${esc(p.venue)}${p.note ? ` · ${esc(p.note)}` : ''}</span>` : ''}
    </div>
    <p class="entry-meta"><span>${esc(p.authors || '')}</span></p>
    ${p.summary ? `<p class="summary">${esc(p.summary)}</p>` : ''}
  </li>`;
    const list = (items) => `<ul class="entries">\n${items.map(entry).join('\n')}\n</ul>`;
    // papers are grouped by year, newest year first, listing order within a year
    const years = [...new Set(ctx.papers.map((p) => String(p.year)))].sort().reverse();
    const papers = years.map((y) => `<h3 class="year">${y}</h3>\n${list(ctx.papers.filter((p) => String(p.year) === y))}`).join('\n');
    return `<article class="content">
${md(page.body, page)}
${ctx.posts.length ? `<section class="listing" id="posts">
<h2 class="eyebrow">Latest</h2>
${list(ctx.posts)}
</section>` : ''}
${ctx.papers.length ? `<section class="listing" id="papers">
${papers}
</section>` : ''}
</article>`;
  },

};

/* ----------------------------------------------------------------- write */

const written = [];
const noindexed = new Set();
function emit(url, html) {
  const rel = url === '/' ? 'index.html' : join(url.replace(/^\/|\/$/g, ''), 'index.html');
  const dest = join(OUT, rel);
  mkdirSync(dirname(dest), { recursive: true });
  writeFileSync(dest, html);
  written.push(url);
}

function render(page, ctx) {
  const layout = layouts[page.layout || 'page'];
  if (!layout) throw new Error(`${page.source}: unknown layout "${page.layout}"`);
  if (page.noindex) noindexed.add(page.url);
  emit(page.url, shell(page, layout(page, ctx)));
}

/* ------------------------------------------------------------------ main */

rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });

// Posts and papers share one shape and one ordering: an explicit "order"
// (1 = top) wins; otherwise newest first.
function listing(name) {
  const file = join(SRC, name);
  return existsSync(file)
    ? JSON.parse(readFileSync(file, 'utf8')).sort((a, b) =>
        (a.order ?? Infinity) - (b.order ?? Infinity) || String(b.date).localeCompare(String(a.date)))
    : [];
}
const posts = listing('blog.json');
const papers = listing('papers.json');   // listed under the posts, after a dashed rule
// Notes are ported artifacts living in static/notes/; this manifest is what
// bin/port-artifact.mjs writes, and it is the only thing the index reads.
const notesFile = join(SRC, 'notes.json');
const notes = existsSync(notesFile)
  ? JSON.parse(readFileSync(notesFile, 'utf8')).sort((a, b) => String(b.added).localeCompare(String(a.added)))
  : [];
const ctx = { posts, papers, notes };

const pages = readdirSync(SRC).filter((f) => extname(f) === '.md').map((f) => loadPage(basename(f, '.md')));

for (const p of pages) render(p, ctx);

// 404
emit('/404', shell({ url: '/404/', title: 'Not found' },
  `<article class="content"><h1>Not found</h1><p>That page doesn't exist. Try <a href="/">the front page</a>.</p></article>`));
// GitHub Pages serves /404.html for unmatched paths, not /404/index.html.
cpSync(join(OUT, '404/index.html'), join(OUT, '404.html'));
rmSync(join(OUT, '404'), { recursive: true, force: true });

cpSync(join(ROOT, 'assets'), join(OUT, 'assets'), { recursive: true });
if (existsSync(join(ROOT, 'static'))) cpSync(join(ROOT, 'static'), OUT, { recursive: true });
// Standalone pages link the same stylesheets; give them the same cache-busting
// query as generated pages, so one edit to assets/ shows up everywhere at once.
for (const f of walkFiles(OUT).filter((f) => f.endsWith('.html'))) {
  const html = readFileSync(f, 'utf8');
  const versioned = html.replace(/href="\/assets\/(design|style)\.css"/g, `href="/assets/$1.css?v=${assetVersion}"`);
  if (versioned !== html) writeFileSync(f, versioned);
}

// RSS. A listed entry may point off-site (a paper that lives on arXiv).
const absolute = (u) => /^https?:\/\//.test(u) ? u : site.url + u;
const rssItems = posts.map((p) => `  <item>
    <title>${esc(p.title)}</title>
    <link>${absolute(p.url)}</link>
    <guid isPermaLink="true">${absolute(p.url)}</guid>
    ${p.date ? `<pubDate>${new Date(`${p.date}T12:00:00Z`).toUTCString()}</pubDate>` : ''}
    <description>${esc(p.summary || '')}</description>
  </item>`).join('\n');
writeFileSync(join(OUT, 'feed.xml'), `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>${esc(site.title)}</title>
  <link>${site.url}/</link>
  <description>${esc(site.description)}</description>
${rssItems}
</channel></rss>
`);

// Sitemap + robots
writeFileSync(join(OUT, 'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${written.filter((u) => u !== '/404' && !noindexed.has(u)).map((u) => `  <url><loc>${site.url}${u}</loc></url>`).join('\n')}
</urlset>
`);
writeFileSync(join(OUT, 'robots.txt'), `User-agent: *\nAllow: /\nSitemap: ${site.url}/sitemap.xml\n`);
writeFileSync(join(OUT, '.nojekyll'), '');

console.log(`built ${written.length} pages -> dist/`);
for (const u of written) console.log(`  ${u}`);

/* ----------------------------------------------------------------- check */

if (CHECK) {
  const problems = [];
  const walk = (dir) => readdirSync(dir).flatMap((f) => {
    const p = join(dir, f);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });
  const files = walk(OUT);
  const exists = new Set(files.map((f) => '/' + relative(OUT, f).split('/').join('/')));
  // Only pages this build produced; static/ passthrough is not ours to lint.
  const generated = new Set(written.map((u) =>
    join(OUT, u === '/' ? 'index.html' : join(u.replace(/^\/|\/$/g, ''), 'index.html'))));
  generated.add(join(OUT, '404.html'));

  for (const f of files.filter((f) => f.endsWith('.html') && generated.has(f))) {
    const html = readFileSync(f, 'utf8');
    const where = '/' + relative(OUT, f);
    for (const m of html.matchAll(/(?:href|src)="(\/[^"#]*)"/g)) {
      const href = m[1].replace(/\?.*$/, "");   // ignore a cache-busting query
      const candidates = [href, href + 'index.html', href + '/index.html', href.replace(/\/$/, '') + '/index.html', href + '.html'];
      if (!candidates.some((c) => exists.has(c))) problems.push(`${where}: dead internal link ${href}`);
    }
  }
  // Markdown that failed to parse leaves its source syntax in the output.
  for (const f of files.filter((f) => f.endsWith('.html') && generated.has(f))) {
    const text = readFileSync(f, 'utf8').replace(/<[^>]+>/g, '');
    for (const m of text.matchAll(/\]\([^)\n]{0,120}\)/g)) {
      problems.push(`/${relative(OUT, f)}: unparsed markdown link "${m[0].slice(0, 60)}"`);
    }
  }

  // Every page, including anything copied through from static/, must be a real
  // document. A fragment without a viewport meta renders on a phone at ~980px
  // and zooms out, so its own responsive rules never fire.
  for (const f of files.filter((f) => f.endsWith('.html'))) {
    const html = readFileSync(f, 'utf8');
    const where = '/' + relative(OUT, f);
    if (!/<!doctype html>/i.test(html)) problems.push(`${where}: no doctype`);
    if (!/<meta[^>]+name=["']viewport["']/i.test(html)) problems.push(`${where}: no viewport meta — will not adapt to phones`);
    if (!/<meta[^>]+charset=/i.test(html)) problems.push(`${where}: no charset`);
  }

  for (const n of notes) {
    if (!exists.has(`/notes/${n.slug}/index.html`)) {
      problems.push(`content/notes.json: "${n.slug}" is listed but static/notes/${n.slug}/index.html does not exist — run bin/port-artifact.mjs`);
    }
  }

  for (const p of posts) {
    if (!p.date) problems.push(`${p.source}: missing "date"`);
    if (!p.title) problems.push(`${p.source}: missing "title"`);
  }
  if (problems.length) {
    console.error(`\ncheck failed (${problems.length}):`);
    for (const p of problems) console.error(`  ${p}`);
    process.exit(1);
  }
  console.log('\ncheck passed: no dead internal links, all frontmatter present');
}
