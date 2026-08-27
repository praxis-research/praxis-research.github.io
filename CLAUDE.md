# Working on this site

The full operating manual. If you are an agent, this file is enough — you should
not need to read `build.mjs` to make a normal change.

Markdown in `content/` becomes HTML in `dist/` via `build.mjs`. There is no
framework and one dependency (`marked`). Push to `main` and GitHub Actions
deploys. Deployment details are in `DEPLOY.md`; you almost never need them.

## The loop

```bash
npm install          # once
npm run check        # build + validate — do this before every commit
npm run serve        # build + preview on http://localhost:8080
```

**`npm run check` passing is the bar for "done."** CI runs the same command and
a failure blocks the deploy. It catches dead internal links, missing
frontmatter, markdown that failed to parse, notes listed but never ported, and
any page missing a doctype, charset, or viewport.

## Where everything lives

| To change | Edit |
| --- | --- |
| Front page copy, research focuses | `content/index.md` |
| The people list | `content/people.md` |
| Blog intro | `content/blog.md` |
| A blog post | `content/blog/<slug>.md` |
| Notes intro | `content/notes.md` |
| Which notes are listed | `content/notes.json` — written by the port script, not by hand |
| Nav, site title, contact URL, email | `site.config.json` |
| Colours, type, components | `assets/design.css` — the shared system |
| Header, nav, footer, page layouts | `assets/style.css` — site chrome, no colours |
| The design guideline | `content/design.md`, published at `/design/` |
| Files served as-is | `static/` — copied to the site root verbatim |

**A page's URL is its path.** `content/blog/foo.md` serves at `/blog/foo/`.
Rename the file to change the URL.

## Recipes

### Add a blog post

Create `content/blog/my-post.md`:

```markdown
---
title: The title of the post
date: 2026-08-21
authors: Ada Lovelace, Shi Feng
venue: NeurIPS 2026                   # optional
paper_url: https://arxiv.org/abs/…    # optional, renders a "Read the paper" link
summary: One sentence, used on the index, in RSS, and for link previews.
---

Body in normal markdown.
```

It appears on `/blog/` and in `feed.xml` automatically, newest first. Do not
edit an index by hand.

### Add a person

A line in `content/people.md`:

```markdown
- [Their Name](https://their-site.example) — MATS 11.0
```

The text after the em dash (` — `) becomes muted metadata. That is the only
convention on the page.

### Add an artifact as a page

Artifacts — the HTML documents Claude generates — become notes at
`/notes/<slug>/`. One command:

```bash
npm run add-note -- <path/to/artifact.html> <slug> "Title" "One-sentence summary"
npm run check
```

That restyles the artifact onto the design system, wraps it in a real HTML
document, writes it to `static/notes/<slug>/`, and adds it to
`content/notes.json` so `/notes/` lists it. Re-running with the same slug
updates in place.

**Why it needs restyling at all:** artifacts are authored as *fragments* — no
doctype, no `<html>`, no `<head>`, no `<body>` — because the artifact runtime
supplies that skeleton at publish time. Served as a file, a fragment has no
viewport meta, so phones render it at ~980px and zoom out and its own
responsive rules never fire. The port script builds the skeleton and swaps the
artifact's design tokens for the site's.

**If the artifact was generated against `/design/`,** the token swap is a no-op
and it already matches. If it was generated some other way, the script maps a
known set of token names (`--ground`, `--above`, `--serif`, …). An artifact
using neither will port structurally but keep its own colours — check the
result, and prefer regenerating it against the design guideline.

To remove a note: delete `static/notes/<slug>/` **and** its entry in
`content/notes.json`. The check fails if you do only one.

### Add or edit a standalone HTML post

Some blog posts are full HTML files in `static/` rather than markdown. They
inline `design.css` and a block of site-chrome CSS from `style.css`. When
editing them:

- **Keep width tokens identical to `design.css`:** `--container: 58rem` and
  `--measure: 50rem`. A page that redefines these shifts the header sideways
  relative to every other page.
- **`.container` must use** `max-width: var(--container); padding: 0 1.5rem;`.
  Custom padding (e.g. `28px`) or a page-specific max-width variable breaks
  alignment with the header and footer.
- **`html` must include `scrollbar-gutter: stable`** so pages with and without
  a scrollbar keep centered content in the same position.
- **Site chrome CSS** (`.site-header`, `.brand`, `.site-nav`, `.site-footer`)
  must match `style.css`. Copy the block; do not improvise.

### Change how the site looks

Read `/design/` (`content/design.md`) first. Then edit `assets/design.css` if it
is a system-wide change, or `assets/style.css` if it is header/nav/footer only.
Never write a literal colour in either.

## Rules

1. **Edit `content/`, `site.config.json`, `assets/`, or `static/`.** Touch
   `build.mjs` only when the task is explicitly about the generator.
2. **Never edit or commit `dist/`.** Generated and gitignored.
3. **Frontmatter is `key: value` only** — no nesting, no lists, no multi-line
   values. The parser rejects anything else on purpose; it keeps it 15 lines.
4. **Internal links end in a slash**: `/blog/some-post/`. Without it the check
   fails.
5. **Never write a literal colour.** Use the tokens in `design.css`. A colour
   defined only inside a media or `[data-theme]` block does not apply in the
   default state and breaks one of the two themes.
6. **Keep the author's words.** When porting or restructuring, move prose
   verbatim. Do not rewrite copy that was not the point of the task.
7. **One dependency.** Do not add more without being asked. The value of this
   repo is that a person can read all of it in ten minutes.
8. **Notes are public.** Everything under `static/notes/` is reachable by
   anyone with the URL. They carry `noindex` and stay out of the sitemap, but
   that is not privacy. Do not publish a working memo without being asked to.
9. **Use the width tokens as-is.** Every page — generated or standalone — must
   use `--container: 58rem` and `--measure: 50rem` from `design.css`. Redefining
   them or substituting a custom variable (e.g. `--max-width: 1000px`) misaligns
   the header with other pages.

## Layouts

`layout:` in frontmatter picks a renderer in `build.mjs`: `home`, `page`,
`people`, `blog-index`, `notes-index`. Posts get `post` automatically from their
directory. A layout is a function returning a string — a plain template, not a
template language. Add one only if an existing one genuinely does not fit.

`noindex: true` in frontmatter adds the robots meta and drops the page from the
sitemap.
