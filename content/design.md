---
title: Design
layout: page
summary: The design system shared by this website and everything generated to sit alongside it.
---

One small system, used by this website and by any artifact meant to sit
alongside it. If you are an agent generating something for Praxis, read this
page and follow it exactly; the result should be indistinguishable in style
from the page you are reading now.

The whole system is one stylesheet: **[/assets/design.css](/assets/design.css)**.
Read it — it is about 200 lines and it is the authority. This page explains the
decisions it encodes.

## How to use it

**On this website:** it is already linked. Site chrome — header, navigation,
footer — lives separately in `style.css`. Never put a colour in `style.css`;
use the tokens.

**In an artifact:** paste the contents of `design.css` inside a `<style>` tag.
Artifacts cannot load external stylesheets, so inlining is the only option.
Then write plain semantic HTML. You should need almost no additional CSS; if
you are writing a lot, you are fighting the system rather than using it.

## The rules

1. **One typeface, plus mono.** The system sans for everything, `--font-mono`
   for data, identifiers, and code. No display face, no serif, no web fonts —
   which also means no network requests. If you want emphasis, use weight and
   space, not a new family.

2. **Colour carries meaning or it does not appear.** There is exactly one
   accent (`--accent`), and it means *link*. There is one semantic pair,
   `--pos` and `--neg`, for things that genuinely oppose: supports and refutes,
   above and below, pass and fail. Decorative colour is not part of the system.

3. **Never write a literal colour.** Every colour is a token. A colour defined
   only inside a media query or a `[data-theme]` block will not apply in the
   default state, and the page renders one theme's text on the other theme's
   ground. This is the single most common way an artifact breaks.

4. **Set `background` on `body` explicitly.** An artifact composites over a
   ground the viewer paints in *their* theme. A transparent body silently
   borrows it, and the page becomes unreadable in one of the two themes.

5. **One reading column.** Running text stays at `--measure` (50rem). Tables
   and figures may use `--container`. Nothing is full-bleed.

6. **Wide things scroll themselves.** Wrap wide tables in `<div class="scroll">`.
   The page body must never scroll sideways.

7. **Do not repeat the title.** The site name appears once per page, and a page
   does not restate what the navigation already says. The same discipline
   applies inside a document: a section heading and its first sentence should
   not say the same thing.

8. **Six components, and no more.** They are listed below. Anything past them
   is a one-off; put it in the page that needs it, not in `design.css`.

9. **A file needs the skeleton the runtime would have given it.** Artifacts are
   authored as fragments — no doctype, no `<html>`, no `<head>`, no `<body>` —
   because the artifact runtime wraps them at publish time. Save one as a file
   and serve it, and it loses all of that, including
   `<meta name="viewport" content="width=device-width, initial-scale=1">`.
   Without that line a phone renders the page at a virtual width near 980px and
   zooms out, so every responsive rule the document already has silently never
   fires. `npm run check` fails on any page in `dist/` missing a doctype,
   charset, or viewport, static passthrough included.

## Tokens

| Token | Means |
| --- | --- |
| `--bg` | page ground |
| `--surface` | callouts, code, anything raised off the ground |
| `--ink` | body text |
| `--heading` | headings and `strong` |
| `--muted` | captions, bylines, secondary table cells |
| `--rule` | hairlines and borders |
| `--accent` | links, and nothing else |
| `--pos` / `--neg` | supports / refutes, above / below, pass / fail |
| `--pos-wash` / `--neg-wash` | the same pair as a background tint |
| `--measure` / `--container` | reading column (50rem) / full width |

Each is redefined for dark in three places — bare `:root`, the
`prefers-color-scheme` block guarded with `:root:not([data-theme="light"])`,
and `:root[data-theme="dark"]`. All three are needed: the viewer's default
setting stamps nothing on the root element, so only the media query
distinguishes light from dark, while an explicit choice must beat the OS in
both directions.

## The components

<h3>1. Callout</h3>

<div class="callout">An aside that must not be skimmed past. Neutral by default.</div>
<div class="callout callout--pos"><strong>Supports.</strong> Use the positive wash only where something genuinely passed or held.</div>
<div class="callout callout--neg"><strong>Refutes.</strong> And the negative only where something genuinely failed.</div>

<h3>2. Chip</h3>

<p>
<span class="chip">phase 1</span>
<span class="chip chip--pos">confirmed</span>
<span class="chip chip--neg">killed</span>
</p>

A short status or label, inline, in mono. Never a sentence.

<h3>3. Meta</h3>

<p class="meta">Bylines, dates, captions, affiliations — anything secondary to the sentence it sits under.</p>

<h3>4. Figure</h3>

Any image or diagram with a `figcaption`. Bordered, never wider than its
container.

<h3>5. Lede</h3>

<p class="lede">The one paragraph that states the point. At most one per document, at the top.</p>

<h3>6. Semantic text</h3>

<p>Inline <span class="pos">supports</span> and <span class="neg">refutes</span>, for use inside a sentence or a table cell.</p>

## Tables

Dense, ruled, no stripes. Put digits that line up in columns in `.num`, which
is mono and tabular.

<div class="scroll">

| Run | Effect | Verdict |
| --- | --- | --- |
| baseline | <span class="num">0.41</span> | <span class="chip">reference</span> |
| ablation | <span class="num">0.09</span> | <span class="chip chip--neg">below</span> |
| full | <span class="num">0.63</span> | <span class="chip chip--pos">above</span> |

</div>

## What not to do

- Do not add a font. Do not add an accent colour.
- Do not use colour as decoration, or to distinguish things that do not oppose.
- Do not centre body text, or set headings in all caps with wide tracking.
- Do not build a hero. A document starts with its title and its lede.
- Do not reach for a card, a shadow, or a rounded corner to create hierarchy
  that spacing and a hairline would carry.
