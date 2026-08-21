# praxis-research.org

The lab website. Markdown in, static HTML out. No Notion, no CMS, no
framework — one build script (`build.mjs`, ~300 lines) and two stylesheets:
`assets/design.css` (the design system, shared verbatim with artifacts) and
`assets/style.css` (site chrome). The site loads no external assets: no web
fonts, no CDN.

```bash
npm install
npm run serve     # build + preview on http://localhost:8080
npm run check     # build + fail on dead internal links or missing frontmatter
```

Push to `main` and GitHub Actions builds and deploys. There is no other step.
(Setting that up is a one-time job — see `DEPLOY.md`.)

## Where things live

| You want to change | Edit |
| --- | --- |
| Front page text, research focuses | `content/index.md` |
| The people list | `content/people.md` |
| Blog intro | `content/blog.md` |
| A blog post | `content/blog/<slug>.md` |
| Nav links, site title, contact form URL | `site.config.json` |
| Colours, fonts, spacing | `assets/design.css` — the shared system, all of it in `:root` |
| Header, nav, footer, page layouts | `assets/style.css` (site chrome only, no colours) |
| The design guideline itself | `content/design.md`, published at `/design/` |
| Images | `assets/` — reference as `/assets/…` |

`serve.mjs`, `preview.mjs` and `deploy.mjs` are development helpers; `build.mjs`
is the only one the site depends on.

**A page's URL is its path.** `content/blog/foo.md` is served at `/blog/foo/`.
Rename the file to change the URL; nothing else refers to it.

## Adding things

**A blog post** — create `content/blog/my-post.md`:

```markdown
---
title: The title of the post
date: 2026-08-19
authors: Ada Lovelace, Shi Feng
venue: NeurIPS 2026            # optional
paper_url: https://arxiv.org/abs/…   # optional, renders a "Read the paper" link
summary: One sentence, used on the blog index, in RSS, and for link previews.
---

Body in normal markdown.
```

It appears on `/blog/` and in `feed.xml` automatically, newest first.

**A person** — add a line to `content/people.md`:

```markdown
- [Their Name](https://their-site.example) — MATS 11.0
```

The text after the em dash (` — `) is styled as muted metadata. That is the only
formatting convention on the page; everything else is plain markdown.

**A new section** — add `content/<name>.md` with `layout: page`, then add it to
`nav` in `site.config.json`. A directory of entries with its own index page
(the way `content/blog/` works) needs a layout in `build.mjs`; copy
`blog-index`.

## Conventions worth keeping

- **`{{name}}` in a page body** is substituted from that page's frontmatter,
  falling back to `site.config.json`. `{{email}}` is the useful one — it means
  the address is written down once.
- **Frontmatter is a small YAML subset**: `key: value`, one per line, quotes
  optional. No nesting, no lists. `build.mjs` will throw on anything else, and
  that is deliberate — it keeps the parser 15 lines long.
- **Internal links end in a slash** (`/people/`, not `/people`), so
  `npm run check` can verify them.
- `npm run check` runs in CI. If it fails, the deploy does not happen.
- `dist/` is generated. Never edit it, never commit it.

## Deployment

`DEPLOY.md` has the whole story: GitHub Pages, the one-time setup, and the
Cloudflare records for moving `praxis-research.org` off super.so.

Short version — once set up, push to `main` and Actions builds and publishes.
`npm run deploy` is the manual fallback that pushes `dist/` to `gh-pages`.
