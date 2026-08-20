# Editing this site

This is a static site: markdown in `content/` becomes HTML in `dist/` via
`build.mjs`. Read `README.md` for the full map — it is short.

## The loop

```bash
npm install          # once
npm run check        # build + validate. Do this before every commit.
```

`npm run check` fails on dead internal links and missing frontmatter. A green
check is the bar for "done"; CI runs the same command and blocks the deploy.

## Rules

1. **Edit `content/`, `site.config.json`, or `assets/style.css`. Nothing else**,
   unless the task is explicitly about the generator.
2. **Never edit or commit `dist/`.** It is generated and gitignored.
3. **Frontmatter is `key: value` only** — no nesting, no lists, no multi-line
   values. The parser rejects anything else on purpose.
4. **Internal links end in a slash**: `/sprints/unsupervised-elicitation/`.
   Without the slash the link check fails.
5. **Keep the author's words.** When porting or restructuring content, move the
   prose verbatim. Do not rewrite copy that was not the point of the task.
6. **One dependency** (`marked`). Do not add more without being asked. The value
   of this repo is that a person can read all of it in ten minutes.

## Adding content

A new file in `content/blog/` or `content/sprints/` appears on its index page
automatically — you do not edit an index by hand. Required frontmatter: `title`
and `date` for posts, `title` and `phase` for sprints. `README.md` has the
templates.

## Layouts

`layout:` in frontmatter picks the renderer in `build.mjs`: `home`, `page`,
`people`, `sprints`, `blog-index`. Posts and sprint pages get theirs
automatically from their directory. Adding a layout means adding a function to
the `layouts` object — it is a plain string template, not a template language.
