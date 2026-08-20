# praxis-research.org

The lab website. Markdown in, static HTML out. No Notion, no CMS, no
framework — one build script (`build.mjs`, ~250 lines) and one stylesheet
(`assets/style.css`).

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
| Sprints intro and process | `content/sprints.md` |
| A sprint project | `content/sprints/<slug>.md` |
| A blog post | `content/blog/<slug>.md` |
| Nav links, site title, contact form URL | `site.config.json` |
| Colours, fonts, spacing | `assets/style.css` (all of it is in `:root`) |
| Images | `assets/` — reference as `/assets/…` |

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

**A sprint project** — create `content/sprints/my-sprint.md`:

```markdown
---
title: "Sprint: My Sprint"
nav_title: My sprint       # short label for the table on /sprints/
topic: Coherence
phase: 1
order: 3                   # position in the table
submit_url: "https://airtable.com/…"
contact_subject: "Praxis Sprint XX questions"
---

Use {{submit_url}}, {{contact_subject}} and {{email}} in the body and they get
substituted, so the form URL is written down exactly once.
```

**A person** — add a line to `content/people.md`:

```markdown
- [Their Name](https://their-site.example) — MATS 11.0
```

The text after the em dash (` — `) is styled as muted metadata. That is the only
formatting convention on the page; everything else is plain markdown.

## Conventions worth keeping

- **Frontmatter is a small YAML subset**: `key: value`, one per line, quotes
  optional. No nesting, no lists. `build.mjs` will throw on anything else, and
  that is deliberate — it keeps the parser 15 lines long.
- **Internal links end in a slash** (`/sprints/`, not `/sprints`), so
  `npm run check` can verify them.
- `npm run check` runs in CI. If it fails, the deploy does not happen.
- `dist/` is generated. Never edit it, never commit it.

## Deployment

`DEPLOY.md` has the whole story: GitHub Pages, the one-time setup, and the
Cloudflare records for moving `praxis-research.org` off super.so.

Short version — once set up, push to `main` and Actions builds and publishes.
`npm run deploy` is the manual fallback that pushes `dist/` to `gh-pages`.
