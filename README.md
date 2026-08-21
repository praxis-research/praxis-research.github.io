# praxis-research.org

The lab website. Markdown in, static HTML out. No Notion, no CMS, no framework —
one build script (`build.mjs`), two stylesheets, and one dependency (`marked`).
The site loads no external assets: no web fonts, no CDN.

```bash
npm install
npm run serve     # build + preview on http://localhost:8080
npm run check     # build + validate; CI runs this and a failure blocks deploys
```

Push to `main` and GitHub Actions builds and deploys.

## Read this first

- **[CLAUDE.md](CLAUDE.md)** — the operating manual: where everything lives,
  recipes for the common changes, and the rules. Also `AGENTS.md`, same file.
  Most edits here are made by Claude, so that file is the primary documentation
  and is kept complete enough to work from alone.
- **[content/design.md](content/design.md)** — the design system, published at
  [/design/](https://praxis-research.org/design/). Point Claude at that page to
  generate an artifact that matches the site.
- **[DEPLOY.md](DEPLOY.md)** — hosting, DNS, and the Cloudflare settings.

## The shape of it

```
content/          markdown — one file per page, plus blog/ for posts
  notes.json      which ported artifacts /notes/ lists (written by a script)
assets/
  design.css      the design system: tokens, base type, six components
  style.css       site chrome: header, nav, footer. No colours.
static/           copied to the site root verbatim (CNAME, ported notes)
bin/
  port-artifact.mjs   turns a Claude artifact into a page under /notes/
build.mjs         the whole generator
```

## The three things you are most likely to want

**Add a blog post** — a markdown file in `content/blog/`. It appears on the
index and in RSS automatically.

**Add a person** — a line in `content/people.md`.

**Turn an artifact into a page:**

```bash
npm run add-note -- artifact.html my-slug "Title" "One-sentence summary"
npm run check
```

Templates and the full explanation for each are in [CLAUDE.md](CLAUDE.md).

## Conventions worth keeping

- `npm run check` passing is the definition of done.
- Internal links end in a slash (`/people/`, not `/people`).
- Frontmatter is a small YAML subset: `key: value`, one per line, no nesting.
- Never write a literal colour; use the tokens in `design.css`.
- `dist/` is generated. Never edit it, never commit it.
