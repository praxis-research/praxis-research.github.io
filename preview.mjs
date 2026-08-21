// Generates a single self-contained preview of the built site, for review.
// `node preview.mjs [outfile]`. Not part of the site; nothing links to it.
import { readFileSync, writeFileSync, statSync } from 'node:fs';
import { join, dirname, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(fileURLToPath(import.meta.url));
const OUT = join(ROOT, 'dist');
const dest = process.argv[2] || join(ROOT, 'preview.html');

const css = readFileSync(join(OUT, 'assets/design.css'), 'utf8');
const site = readFileSync(join(OUT, 'assets/style.css'), 'utf8');

const PAGES = [
  ['About', '/'],
  ['People', '/people/'],
  ['Blog', '/blog/'],
  ['Design', '/design/'],
  ['Notes', '/notes/'],
  ['Note: Two Vocabularies', '/notes/two-vocabularies/'],
  ['Note: Confession', '/notes/confession-as-certificate/'],
  ['Not found', '/404.html'],
];

const docs = {};
for (const [, url] of PAGES) {
  const file = url.endsWith('.html') ? url.slice(1) : join(url === '/' ? '' : url.slice(1), 'index.html');
  let html = readFileSync(join(OUT, file), 'utf8');
  // Inline the stylesheets the generated pages link; the notes already carry
  // design.css inside them, so those replacements simply find nothing.
  html = html
    .replace('<link rel="stylesheet" href="/assets/design.css">', `<style>${css}</style>`)
    .replace('<link rel="stylesheet" href="/assets/style.css">', `<style>${site}</style>`)
    .replace(/<link rel="icon"[^>]*>/, '');
  docs[url] = html;
}

const tabs = PAGES.map(([label, url], i) =>
  `<button class="tab${i === 0 ? ' on' : ''}" data-url="${url}">${label}</button>`).join('');

writeFileSync(dest, `<title>Praxis Design System</title>
<style>
  :root {
    --shell: #eceef0; --panel: #ffffff; --ink: #1a1d21; --dim: #5f6b74;
    --line: #dce1e6; --accent: #125fa8;
    --ui: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --shell: #101315; --panel: #15181b; --ink: #dfe4e8; --dim: #96a2ab;
      --line: #2c3238; --accent: #7fb3e8;
    }
  }
  :root[data-theme="dark"] {
    --shell: #101315; --panel: #15181b; --ink: #dfe4e8; --dim: #96a2ab;
    --line: #2c3238; --accent: #7fb3e8;
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--shell); color: var(--ink);
         font-family: var(--ui); display: flex; flex-direction: column; min-height: 100vh; }
  .bar { position: sticky; top: 0; z-index: 5; background: var(--panel);
         border-bottom: 1px solid var(--line); display: flex; flex-wrap: wrap;
         align-items: center; gap: 0.5rem 1.25rem; padding: 0.7rem 1.1rem; }
  .label { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.11em;
           color: var(--dim); white-space: nowrap; }
  .tabs { display: flex; flex-wrap: wrap; gap: 0.3rem; flex: 1; }
  .tab { font: inherit; font-size: 0.78rem; cursor: pointer; background: none;
         border: 1px solid transparent; border-radius: 4px; color: var(--dim);
         padding: 0.28rem 0.6rem; }
  .tab:hover { color: var(--ink); }
  .tab.on { color: var(--accent); border-color: var(--line); background: var(--shell); }
  .tab:focus-visible, .mode button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .mode { display: flex; border: 1px solid var(--line); border-radius: 4px; overflow: hidden; }
  .mode button { font: inherit; font-size: 0.72rem; cursor: pointer; background: none;
                 border: 0; color: var(--dim); padding: 0.3rem 0.7rem; }
  .mode button.on { background: var(--accent); color: var(--panel); }
  .stage { flex: 1; padding: 1.1rem; display: flex; }
  iframe { width: 100%; min-height: 80vh; border: 1px solid var(--line);
           border-radius: 5px; background: #fff; display: block; }
  .foot { padding: 0.75rem 1.1rem 1.4rem; font-size: 0.72rem; color: var(--dim); line-height: 1.6; }
</style>
<div class="bar">
  <span class="label">Praxis · preview</span>
  <div class="tabs">${tabs}</div>
  <div class="mode">
    <button data-mode="light" class="on">Light</button>
    <button data-mode="dark">Dark</button>
  </div>
</div>
<div class="stage"><iframe id="frame" title="Site preview"></iframe></div>
<p class="foot">Rendered from the real build output. The two notes were generated as standalone
artifacts and restyled onto the same system by swapping tokens — nothing about their structure changed.
The theme switch stamps data-theme on the document, which is exactly how an artifact viewer does it.</p>
<script>
  const DOCS = ${JSON.stringify(docs)};
  let url = '/', mode = 'light';

  function paint() {
    const frame = document.getElementById('frame');
    // Stamp the theme the same way an artifact viewer does, rather than
    // rewriting tokens — if this works, the token structure is correct.
    frame.srcdoc = DOCS[url].replace(/<html([^>]*)>/i,
      (m, attrs) => '<html' + attrs.replace(/\\sdata-theme="[^"]*"/, '') + ' data-theme="' + mode + '">');
  }
  document.getElementById('frame').addEventListener('load', (e) => {
    try {
      const d = e.target.contentDocument;
      if (d) e.target.style.height = Math.max(d.body.scrollHeight + 40, 500) + 'px';
    } catch (_) { /* height stays at the CSS minimum */ }
  });
  document.querySelectorAll('.tab').forEach((b) => b.onclick = () => {
    document.querySelectorAll('.tab').forEach((x) => x.classList.toggle('on', x === b));
    url = b.dataset.url; paint();
  });
  document.querySelectorAll('.mode button').forEach((b) => b.onclick = () => {
    document.querySelectorAll('.mode button').forEach((x) => x.classList.toggle('on', x === b));
    mode = b.dataset.mode; paint();
  });
  paint();
</script>
`);
console.log(`preview -> ${relative(ROOT, dest)} (${(statSync(dest).size / 1024).toFixed(0)} KB)`);
