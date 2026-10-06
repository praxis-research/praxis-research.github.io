"""Port the grafting paper page onto the site: static/grafting.html, served at /grafting.

The page itself is built outside this repo (Peter and Dani's builder, github.com/peternutter/mats_project,
experiments/paper/interactive/build_graft_results.py), which writes one self-contained file, graft_results.html.
This script takes that file unchanged and fits it to the site and to /design/:

  1. stylesheets: drop the inlined copy of design.css and link /assets/design.css and /assets/style.css,
     as every standalone page does (CLAUDE.md: "Do not inline design.css or the site chrome");
  2. chrome: the site header and footer; the page's own fixed bar becomes a sticky in-page bar under the
     site header, its theme toggle goes (no other page has one; the theme follows the OS), and its sub-row
     overlays the content so opening a branch still moves nothing;
  3. the page container is renamed .paper, so the page's .container rules stop reaching the site header and
     footer, and it keeps the site's 1.5rem gutter at every width so text lines up with the header;
  4. head: a plain <title>, the site favicon, a description, canonical, and noindex (as before);
  5. one column: everything in the paper body, figures included, stays within --measure; the
     abstract is at body size;
  6. condition colours (Shi, 2026-10-05): graft #7733C3, native #A34335, midtrain #4E7D73, overriding
     the builder's chart tokens in all three theme states (COLOURS below);
  7. blog text (Shi, 2026-10-05): the TL;DR, introduction and conclusion come from the "LW Blog - Prose" tab of
     the MATS progress-report doc, kept in blog/*.html; they replace the abstract, Figure 1 and the paper's
     introduction (its three route diagrams stay, as Figures 1-3), and the conclusion goes before Related work;
  8. a midtraining chart (midtraining.json + midtraining.js) in the Midtraining branch, from the paper's Figure 4;
  9a. the results row of the bar shows only while reading the results, as an overlay like AuditBench's row (2026-10-06);
  9. tidying (Shi, 2026-10-05): results as a tab row in the blog's order with AuditBench open on load (no tree),
     References folded, links underlined once, no doubled hairline under "More details";
  10. results (Shi, 2026-10-05): the doc's results prose leads AuditBench, false facts and midtraining, with the
     paper's paragraphs folded under "More details"; Evaluations is one fold; the results sit on a --surface band;
     open folds are indented behind a rule, keep their summary under the bar, and close from the rule;
  11. chart keys (Shi, 2026-10-05): one format and placement for every chart in the results (see legends());
  12. "mid-train" / "pre-train" everywhere visible, case kept, except other papers' titles (hyphenate(), HYPHEN_JS);
  13. fixes: the intro's "Our method" heading sat centred in the figure column; the hidden comment
     widget no longer calls /api/comments (it does not exist here); Shi's author link is shifeng.me.

Stdlib only. Usage:
    python pages/grafting/port.py <graft_results.html>      # writes static/grafting.html
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "static" / "grafting.html"

TITLE = "Pre-training interventions, ex post facto: grafting model beliefs across checkpoints"
DESC = ("Grafting: train the SDF adapter on the pre-trained checkpoint, then add the learned weight update "
        "to the post-trained model.")

HEAD = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="https://praxis-research.org/grafting">
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/design.css">
<link rel="stylesheet" href="/assets/style.css">
"""

SITE_HEADER = """<header class="site-header">
  <div class="container">
    <a class="brand" href="/">Praxis Research</a>
    <nav class="site-nav">
        <a href="/people">People</a>
    </nav>
  </div>
</header>
"""

SITE_FOOTER = """<footer class="site-footer">
  <div class="container">
    <p>Praxis Research</p>
  </div>
</footer>
"""

# Last in the head, so it wins over the page's own layers at equal weight. No literal colours.
SITE_CSS = """<style>
/* ==== site port (pages/grafting/port.py) ==== */
html body .site-header{margin-bottom:0}
/* the page's own footer rules (measure width, left margin) stay off the site footer */
html body footer.site-footer{max-width:none!important;width:auto!important;margin:0!important;color:var(--muted)}
html body footer.site-footer,html body footer.site-footer *{font-size:.9rem!important}
html body footer.site-footer .container{max-width:var(--container)!important;margin:0 auto!important}
/* the page's bare-link rule (an underline border) stays off the site chrome */
.site-header a,.site-footer a{border-bottom:0}
/* the page's bar: in flow under the site header, sticky once it reaches the top */
html body .topbar{position:sticky!important;top:0;left:auto;right:auto;z-index:100}
html body .topbar .hrow{margin:0 auto!important;padding:.6rem 1.5rem!important}
/* the branch sub-row overlays the content instead of pushing it down */
html body .topbar .hrow.hsub{position:absolute;top:100%;left:0;right:0;background:var(--bg);
 border-bottom:1px solid var(--rule);padding-top:.4rem!important;padding-bottom:.4rem!important}
html body .topbar .hrow.hsub{max-width:none!important;padding-left:max(1.5rem,calc((100% - var(--container))/2 + 1.5rem))!important}
/* the page column: the site's container, the site's gutter at every width */
html body .paper{max-width:var(--container)!important;margin:0 auto!important;padding:2.5rem 1.5rem 4rem!important;width:100%}
@media(max-width:900px){html body .topbar .hrow{padding:.5rem 1.5rem!important}html body .paper{padding:2rem 1.5rem 3rem!important}}
/* "Our method" and the other intro headings: on the text column, not centred in the figure column */
html body main #intro>h3{margin-left:0!important;margin-right:auto!important}
/* one column: figures, charts and controls stay within the text column (--measure), not --container */
html body main.main{max-width:var(--measure)!important;margin-left:0!important}
html body main.main :is(.fig,.controls,.hero,.wx,.figrow,.facets,.bff,.bff-fig3,.bff-f3,.f1-fig,figure.mf,.cyoa,.legend,
 .searchrow,.scroll,.howto,#intro,.trunk-end,section.abstract,.bem,.bcmt,#tocboxes,figure,svg){max-width:100%!important}
/* at the text column the charts are ~10% narrower, so their 12px labels need a little more room:
   results-map cards never shrink below their longest word ("misalignment") */
html body .cy-row>.bcard.cy{min-width:min-content!important}
/* overview bars: group labels at the small chart size (neighbours touched at 12px), room for two-line labels */
html body #ov-all svg text.glab,html body #ov-all svg text.glab tspan{font-size:calc(var(--fs-chart-xs) * var(--k,1))!important}
html body #ov-all svg{margin-bottom:.75rem}
/* false-facts capabilities: the CI line under "graft − native" a few units lower so the two lines clear */
html body #bff3-caps svg text.bff-val+text.bff-tick{transform:translateY(4px)}
/* links: the design system's underline only (the page's bare-link rule also drew a bottom border) */
html body main a{border-bottom:0!important}
/* "More details": one hairline above; the section after it brings its own, so no second line below */
html body details.more{border-bottom:0!important}
/* results: a section heading over a plain tab row (no tree); the open result's tab is underlined */
#cytree{display:none!important}
html body #branchnav .cy-start{display:none!important}
html body #branchnav .cy-bubble{margin:3rem 0 .75rem!important}
html body #branchnav .cy-row{display:grid!important;grid-template-columns:repeat(6,minmax(0,1fr));gap:0 1rem;
 border-bottom:1px solid var(--rule);margin:0 0 1.5rem;padding:0;max-width:var(--measure)}
html body #branchnav .cy-row>.bcard.cy{display:block;flex:none;width:auto;min-width:0!important;margin:0 0 -1px!important;
 padding:.5rem 0 .6rem!important;text-align:left!important;border:0!important;border-bottom:2px solid transparent!important;cursor:pointer}
html body #branchnav .bcard.cy .bt{display:block;font-weight:400!important;color:var(--ink)!important;text-decoration:none!important;
 border:0!important;line-height:1.3;overflow-wrap:anywhere}
html body #branchnav .bcard.cy:hover .bt{text-decoration:underline!important}
html body #branchnav .bcard.cy[aria-pressed="true"]{border-bottom-color:var(--heading)!important}
html body #branchnav .bcard.cy[aria-pressed="true"] .bt{font-weight:700!important;color:var(--heading)!important;text-decoration:none!important}
@media(max-width:600px){html body #branchnav .cy-row{grid-template-columns:repeat(3,minmax(0,1fr))}}
/* the AuditBench section links in the bar show only while reading that result */
html:not(.in-results) #tocmain{visibility:hidden}
/* references: folded by default */
html body .refs-fold{border:0!important;padding:0!important;background:none!important}
html body .refs-fold>summary{cursor:pointer;display:list-item}
html body .refs-fold>summary>h2{display:inline;margin:0!important}
html body .refs-fold[open]>summary{margin-bottom:1rem}
/* monospace reads large: the prompt template and inline code a step smaller, so they sit level with the text */
html body main code{font-size:.9em!important}
html body main blockquote.ptq,html body main blockquote.ptq *{font-size:13px!important;line-height:1.5!important}
/* fewer decorative rules: none above "More details", the evaluation headings, the chart controls or the acknowledgments */
html body details.more{border-top:0!important;border-bottom:0!important;padding:0!important;margin:.5rem 0 1rem!important}
html body details.evl:not(.evl-sub),html body .evl-axis{border-top:0!important}
html body .controls,html body .controls.loc,html body .bff-ctl{border-top:0!important;border-bottom:0!important}
html body main footer{border-top:0!important}
/* folds: an open fold is indented behind a rule; its summary stays under the bar while you read; the rule closes it */
html body :is(details.more,details.howto,details.refs-fold)[open]{border-left:2px solid var(--rule)!important;padding-left:1rem!important}
html body :is(details.more,details.howto,details.refs-fold)[open]>summary{position:sticky;top:var(--stick,0px);z-index:6;
 background:var(--fold-bg,var(--bg));margin-left:calc(-1rem - 2px)!important;padding:.35rem 0!important}
html body :is(details.more,details.howto,details.refs-fold).rule-hot{border-left-color:var(--muted)!important;cursor:pointer}
html body details.howto>summary{cursor:pointer;display:list-item}
html body details.howto>summary>h2{display:inline;margin:0!important}
html body details.howto{margin:2.5rem 0 1rem!important;border-top:0!important;border-right:0!important;border-bottom:0!important;background:none!important}
html body details.howto:not([open]){border-left:0!important;padding:0!important}
html body details.howto[open]>summary{margin-bottom:.75rem!important}
/* the interactive results sit on their own ground, set apart from the post around them */
html body .results-band{--fold-bg:var(--surface);background:var(--surface);margin:3.5rem -1.5rem;padding:.25rem 1.5rem 2.5rem}
html body .results-band #branchnav .cy-bubble{margin-top:1.75rem!important}
html body .results-band :is(.controls,.controls.loc,.bff-ctl){background:var(--surface)!important}
html body .results-band .hero{background:transparent!important}
html body .results-band+*{margin-top:0}
/* Figures 1-3, the route drawings: 35rem wide, centred in the column; black line art on a transparent ground, so they
   keep a light ground in dark mode */
html body main.main #intro figure.route-fig{margin:1.5rem auto 1.75rem!important;max-width:35rem!important}
html body main figure.route-fig img{display:block;width:100%;height:auto;border:0;background:var(--c-fig-ground);padding:.5rem 0}
html body main figure.route-fig figcaption{margin-top:.6rem;text-align:left}
/* the reality-drift figure: reality-drift.png, and reality-drift-dark.png in dark mode (both from make_drift_pngs.py) */
html body main figure.drift-fig{margin:1.5rem 0 2rem}
html body main figure.drift-fig img{display:block;width:100%;height:auto;border:0}
/* chart keys: one format and one place for every chart in the results: above the chart, left-aligned, 10px swatches,
   small muted labels. Keys drawn inside a chart (overview, EM) are hidden in favour of the HTML key above it. */
html body svg text.akey,html body svg text.akey+rect{display:none!important}
html body :is(.legend.armkey,#swarmLeg,.bff-key,.bcmt-key,.bem-key,.ukey){display:flex!important;flex-wrap:wrap;
 justify-content:flex-start!important;align-items:center;gap:.25rem 1rem!important;margin:.75rem 0 .5rem!important;padding:0!important;
 max-width:var(--measure)!important;font-size:var(--fs-small)!important;color:var(--muted)!important;text-align:left!important}
html body :is(.legend.armkey,#swarmLeg,.bff-key,.bcmt-key,.bem-key,.ukey) *{font-size:var(--fs-small)!important;font-weight:400!important}
html body :is(.legend.armkey,#swarmLeg,.bff-key,.bcmt-key,.ukey) :is(i,.sw){display:inline-block!important;width:10px!important;
 height:10px!important;margin:0 .35rem 0 0!important;vertical-align:-1px;border:0!important;border-radius:0!important}
html body .bem-key:empty,html body .bem-key:has(> .bem-na:empty):not(:has(i)){display:none!important}
/* post header as on the site's other posts: the byline is design.css's .meta (0.9rem, muted), and the TL;DR its
   neutral callout; undo the build's type-scale overrides on both */
html body main h1{margin-bottom:.75rem!important}
html body main p.meta.byline,html body main p.meta.byline *{font-size:.9rem!important;color:var(--muted)!important;
 margin:0 0 1rem!important;line-height:1.6!important}
html body main #tldr.callout{background:var(--surface)!important;border-left:3px solid var(--rule)!important;
 padding:.8rem 1rem!important;margin:1.5rem 0!important;max-width:var(--measure)!important}
html body main #tldr.callout,html body main #tldr.callout *{font-size:var(--fs-body)!important}
html body main #tldr.callout>:last-child{margin-bottom:0!important}
/* text renders like every other page: the build set body{-webkit-font-smoothing:antialiased}, which on macOS draws
   thinner strokes than the browser default the site uses; and its title (.name) had line-height 1.15, not 1.25 */
html body{-webkit-font-smoothing:auto!important;-moz-osx-font-smoothing:auto!important}
html body main h1.name{line-height:1.25!important}
/* the section in view, in the main row: the same mark as the AuditBench row */
html body .topbar .hrow:not(.hsub) .hnav a.on{font-weight:700!important;text-decoration:underline!important;
 text-decoration-thickness:2px!important;text-underline-offset:.35em;color:var(--heading)!important}
/* the bar's three levels (Shi, 2026-10-06): sections; results, one level down; AuditBench's parts, two down.
   Each child row has its own line, starts under its parent item (--res-x, --ab-x, set by SPY_JS), opens with a
   muted ↳, and is set in muted text; the current item in any row is underlined in --heading. */
html body .topbar .hrow:not(.hsub) .hbr::before,html body .topbar .hrow.hsub .hnav::before{content:"↳";color:var(--muted);
 margin-right:.15rem;font-size:var(--fs-small)}
html body .topbar .hrow:not(.hsub) .hbr .bcard.hb:not([aria-pressed="true"]),html body #tocmain .hnav a:not(.on){color:var(--muted)!important}
html body #tocmain>.hk{display:none!important}
/* the results row hangs below the bar like the AuditBench row (an overlay, so it never moves the page), and both
   show only while the reader is in the results (html.in-results); each starts under its parent item */
html body .topbar .hrow:not(.hsub){position:static!important}
html body .topbar .hrow:not(.hsub)>.hbr{position:absolute;top:100%;left:0;right:0;z-index:99;background:var(--bg);
 border-bottom:1px solid var(--rule);display:flex;flex-wrap:nowrap;overflow-x:auto;gap:0 1.25rem;
 padding:.4rem 1.5rem .4rem calc(var(--res-left,1.5rem) - 1.15rem)!important;margin:0!important}
html body #tocmain.hrow.hsub{top:calc(100% + var(--hbr-h,0px) - 1px)!important;padding-left:calc(var(--ab-left,1.5rem) - 1.15rem)!important}
html body #tocmain .hnav{margin-left:0!important}
html:not(.in-results) body .topbar .hrow:not(.hsub)>.hbr{visibility:hidden}
html body .topbar .hrow:not(.hsub)>.hbr{scrollbar-width:none}
html body .topbar .hrow:not(.hsub)>.hbr::-webkit-scrollbar{display:none}
@media(max-width:900px){
 html body .topbar .hrow:not(.hsub)>.hbr{padding-left:1rem!important}
 html body #tocmain.hrow.hsub{padding-left:1rem!important}
}
/* bar items keep one width whether highlighted (bold) or not: each reserves its bold width with a hidden copy */
html body .topbar :is(.hnav a,.hbr .bcard.hb){display:inline-flex!important;flex-direction:column;align-items:flex-start}
html body .topbar :is(.hnav a,.hbr .bcard.hb)::after{content:attr(data-label);font-weight:700;height:0;visibility:hidden;
 overflow:hidden;pointer-events:none;user-select:none;speak:never}
/* the abstract at body size, like the rest of the text */
html body main section.abstract p.lede,html body main section.abstract p.lede *{font-size:var(--fs-body)!important}
</style>
"""

# Condition colours (Shi, 2026-10-05). The builder draws every chart, legend and Figure 1 from these tokens, so
# redefining them recolours the whole page. Light values are Shi's; dark values keep the hue and lift the lightness
# (>= 6.7:1 on the dark ground); washes are a 10% tint for Figure 1's verdict boxes, which keep a light ground in both
# themes. --c-cmt-mid is the mid-trained CMT model (= midtrain) and --c-plain the plain graft (a graft tint).
COLOURS_LIGHT = {"--c-graft": "#7733c3", "--c-native": "#a34335", "--c-midtrain": "#4e7d73",
                 "--c-cmt-mid": "#4e7d73", "--c-plain": "#b48fde"}
COLOURS_DARK = {"--c-graft": "#b58ee1", "--c-native": "#dc9c93", "--c-midtrain": "#8eb8af",
                "--c-cmt-mid": "#8eb8af", "--c-plain": "#d5beee"}
COLOURS_FIG = {"--c-fig-graft": "#7733c3", "--c-fig-native": "#a34335", "--c-fig-midtrain": "#4e7d73",
               "--c-fig-graft-wash": "#f1ebf9", "--c-fig-native-wash": "#f6eceb", "--c-fig-midtrain-wash": "#edf2f1"}


def _tokens(d):
    return ";".join(f"{k}:{v}" for k, v in {**d, **COLOURS_FIG}.items())


COLOUR_CSS = ("<style>\n/* condition colours (pages/grafting/port.py), after the builder's chart tokens */\n"
              f":root{{{_tokens(COLOURS_LIGHT)}}}\n"
              f"@media (prefers-color-scheme: dark){{:root:not([data-theme=\"light\"]){{{_tokens(COLOURS_DARK)}}}}}\n"
              f":root[data-theme=\"dark\"]{{{_tokens(COLOURS_DARK)}}}\n</style>\n")

HERE = pathlib.Path(__file__).resolve().parent
BLOG = HERE / "blog"
MID_CAPTION = ('<b>Grafting avoids the GSM8K collapse of native training.</b> Qwen3-14B, two-seed means. Top: installed '
               'belief, capability (MMLU-Pro, GPQA-D, IFEval and tool calls), GSM8K, μ-decisiveness and real − made-up '
               'separation, where higher is better. Bottom: <i>P</i>(real) for known-fiction and made-up entities, where '
               'lower is better. <span class="sc">native</span> is SDF on the instruction-tuned <span class="sc">control</span> '
               'model; <span class="sc">graft</span> is the anchored graft.')


def _one(pattern: str, html: str, what: str, flags=re.S) -> re.Match:
    m = re.search(pattern, html, flags)
    if not m:
        sys.exit(f"port: {what} not found in the build")
    return m


ROUTES = {   # width, height (the SVGs' own), alt text
    "midtrain": (2837, 416, "Mid-train: the base model is trained on synthetic documents (SDF), then post-trained, "
                             "giving an intact model that holds the new belief."),
    "native": (2855, 416, "Native: the base model is post-trained, then trained on synthetic documents (SDF), "
                         "giving a model that holds the belief but is visibly falling apart."),
    "graft": (2838, 426, "Grafting: post-training and SDF are applied to the base model separately and their weight "
                        "updates added, giving an intact model that holds the new belief."),
}


def blog(html: str) -> str:
    """the blog's TL;DR, introduction and conclusion in place of the paper's abstract, Figure 1 and introduction"""
    # Figures 1-3: the three route drawings (static/figures/grafting/route-*.png, Shi's {midtrain,native,grafting}_new.png),
    # with the blog's captions
    intro = (BLOG / "intro.html").read_text()
    for m in re.finditer(r"\{\{FIG:(\w+)\|(.*?)\}\}", intro, re.S):
        w, h, alt = ROUTES[m.group(1)]
        fig = (f'<figure class="route-fig"><img src="/figures/grafting/route-{m.group(1)}.png" width="{w}" height="{h}" '
               f'loading="lazy" alt="{alt}"><figcaption>{m.group(2)}</figcaption></figure>')
        intro = intro.replace(m.group(0), fig, 1)
    if "{{" in intro:
        sys.exit("port: a figure placeholder in blog/intro.html was not replaced: "
                 + intro[intro.index("{{"):intro.index("{{") + 40])

    # byline: the build's two-tier linked author block (with its lead-author coin flip) becomes the site's .meta line
    m = _one(r'<div class="authors meta">.*?</div></div>', html, "the author block")
    html = html[:m.start()] + BYLINE + html[m.end():]

    m = _one(r'<section class="abstract" id="abstract">.*?</section>', html, "the abstract")
    html = html[:m.start()] + (BLOG / "tldr.html").read_text() + html[m.end():]
    # the paper's Figure 1 goes (the blog's Figures 1-3 replace it)
    m = _one(r'<figure class="fig1 f1-fig" id="fig1">.*?</figure>', html, "Figure 1")
    html = html[:m.start()] + html[m.end():]
    m = _one(r'<div id="intro">.*?</div>\s*(?=<details class="cbox" data-sec="s0">)', html, "the introduction")
    html = html[:m.start()] + intro + html[m.end():]

    anchor = '<section class="trunk-end" id="relwork">'
    _one(re.escape(anchor), html, "Related work")
    html = html.replace(anchor, (BLOG / "conclusion.html").read_text() + anchor, 1)
    nav = '<a href="#relwork">Related work</a>'
    _one(re.escape(nav), html, "the Related work nav link")
    html = html.replace(nav, '<a href="#conclusion">Conclusion</a>' + nav, 1)

    return html



def _fold(inner: str) -> str:
    return f'<details class="more"><summary>More details</summary><div class="more-body">\n{inner.strip()}\n</div></details>\n'


def _section(html: str, key: str):
    m = _one(r'<section class="branch" id="b-' + key + r'"[^>]*>', html, f"the {key} result")
    depth, end = 0, None
    for t in re.finditer(r"<(/?)section\b[^>]*>", html[m.start():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            end = m.start() + t.end()
            break
    return m.start(), end


def _sub(sec: str, pattern: str, repl, what: str) -> str:
    m = _one(pattern, sec, what)
    out = repl(m) if callable(repl) else repl
    return sec[:m.start()] + out + sec[m.end():]


def results(html: str) -> str:
    """the doc's results prose leads each of the blog's three results; the paper's paragraphs fold under it"""
    frag = lambda name: (BLOG / name).read_text()

    a, b = _section(html, "mainline")
    sec = html[a:b]
    sec = sec.replace('<span class="bn">AuditBench organisms (mainline)</span>', '<span class="bn">AuditBench organisms</span>', 1)
    sec = _sub(sec, r'(</div>\n)((?:<p>.*?</p>\n)+)(?=<div class="hero" data-hero>)',
               lambda m: m.group(1) + frag("results-auditbench-lead.html") + _fold(m.group(2)), "AuditBench's opening paragraphs")
    claim = '<p class="claim">Grafting installs belief in the target entities with a fraction of the reality drift.</p>'
    sec = _sub(sec, re.escape(claim), claim + "\n" + frag("results-auditbench-drift.html"), "the belief claim")
    sec = _sub(sec, r'<p>After stage one, .*?</p>\s*<p><span class="sc">native</span> organisms also start.*?</p>',
               lambda m: _fold(m.group(0)), "the paper's cloze paragraphs")
    claim = '<p class="claim">Grafting preserves preferences.</p>'
    sec = _sub(sec, re.escape(claim), claim + "\n" + frag("results-auditbench-mu.html"), "the preference claim")
    sec = _sub(sec, r'<p>SDF harms the sharpness.*?</p>\s*<p>On Llama-3.3-70B the .*?</p>',
               lambda m: _fold(m.group(0)), "the paper's preference paragraphs")
    html = html[:a] + sec + html[b:]

    a, b = _section(html, "falsefacts")
    sec = html[a:b]
    m = _one(r'<p>We report our main results on model organisms.*?</p>\n', sec, "the false-facts opening paragraph")
    paper = m.group(0)
    sec = sec[:m.start()] + frag("results-falsefacts-lead.html") + sec[m.end():]
    anchor = '<div class="bff" id="bff">'
    _one(re.escape(anchor), sec, "the false-facts explorer")
    sec = sec.replace(anchor, frag("results-falsefacts-after.html") + _fold(paper) + anchor, 1)
    html = html[:a] + sec + html[b:]

    a, b = _section(html, "midtraining")
    sec = html[a:b]
    m = _one(r'(</div>\n)((?:<p>.*?</p>\n)+)', sec, "the midtraining paragraphs")
    paper = re.findall(r"<p>.*?</p>", sec[m.start():], re.S)
    if len(paper) != 6 or "four settings" not in paper[2]:
        sys.exit("port: the Midtraining result no longer has its six paper paragraphs")
    chart = ('<div class="bcmt" id="bmid"><div class="bcmt-key" id="bmid-key"></div>'
             f'<figure><div class="fig" id="bmid-chart"></div><figcaption>{MID_CAPTION}</figcaption></figure></div>\n'
             f'<script type="application/json" id="bmid-data">{(HERE / "midtraining.json").read_text().strip()}</script>\n'
             f'<script>{(HERE / "midtraining.js").read_text()}</script>\n')
    lead = frag("results-midtraining.html").replace("{{CHART}}", chart)
    cbox = sec.index('<details class="cbox"')
    sec = sec[:m.start(2)] + lead + _fold("\n".join(paper)) + "\n" + sec[cbox:]
    return html[:a] + sec + html[b:]


# "mid-train" and "pre-train" (Shi, 2026-10-05): every visible midtrain*/pretrain* is hyphenated, case kept, except in
# the titles of other papers (the reference list is skipped whole; these phrases are protected wherever they appear).
PROTECT = ["Model Spec Midtraining", "Constitutional Midtraining", "Alignment Pretraining", "Synthetic Persona Pretraining",
           "Don't Stop Pretraining", "Synthetic Continued Pretraining", "Safety Pretraining"]
_HYPH = [(re.compile(r"\b([Mm])idtrain"), r"\1id-train"), (re.compile(r"\b([Pp])retrain"), r"\1re-train")]


def hyphen_text(t: str) -> str:
    keep = {}
    for j, ph in enumerate(re.findall(r"\{\{.*?\|", t)):      # figure placeholders ({{FIG:key|...) are not prose
        keep[f"\x01{j}\x01"] = ph
        t = t.replace(ph, f"\x01{j}\x01", 1)
    for i, ph in enumerate(PROTECT):
        if ph in t:
            keep[f"\x00{i}\x00"] = ph
            t = t.replace(ph, f"\x00{i}\x00")
    for pat, rep in _HYPH:
        t = pat.sub(rep, t)
    for k, ph in keep.items():
        t = t.replace(k, ph)
    return t


def hyphenate(html: str) -> str:
    """hyphen_text on visible text and alt/title/aria-label, never in scripts, styles or the reference list"""
    parts = re.split(r'(<script\b.*?</script>|<style\b.*?</style>|<section class="trunk-end" id="references">.*?</section>)',
                     html, flags=re.S)
    out = []
    for part in parts:
        if part.startswith(("<script", "<style", '<section class="trunk-end" id="references">')):
            out.append(part)
            continue
        part = re.sub(r">([^<]+)<", lambda m: ">" + hyphen_text(m.group(1)) + "<", part)
        part = re.sub(r'\b(alt|title|aria-label)="([^"]*)"', lambda m: f'{m.group(1)}="{hyphen_text(m.group(2))}"', part)
        out.append(part)
    return "".join(out)


HYPHEN_JS = """<script>(function(){
// the same rule for text the charts and tooltips draw after load (see hyphenate() in pages/grafting/port.py)
const PROTECT=""" + json.dumps(PROTECT) + """;
function fix(t){ const keep=[]; PROTECT.forEach((p,i)=>{ if(t.includes(p)){ keep.push([i,p]); t=t.split(p).join("\\u0000"+i+"\\u0000"); } });
  t=t.replace(/\\b([Mm])idtrain/g,"$1id-train").replace(/\\b([Pp])retrain/g,"$1re-train");
  keep.forEach(([i,p])=>{ t=t.split("\\u0000"+i+"\\u0000").join(p); }); return t; }
const skip=n=>{ const p=n.parentElement; return !p||p.closest("script,style,#references,.citepop,a.cit"); };
function walk(root){ if(root.nodeType===3){ if(!skip(root)){ const v=fix(root.textContent); if(v!==root.textContent) root.textContent=v; } return; }
  if(root.nodeType!==1) return;
  const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT); let n; const todo=[];
  while(n=w.nextNode()) if(!skip(n) && /idtrain|retrain/.test(n.textContent)) todo.push(n);
  todo.forEach(n=>{ const v=fix(n.textContent); if(v!==n.textContent) n.textContent=v; }); }
new MutationObserver(ms=>ms.forEach(m=>{ if(m.type==="characterData") walk(m.target); else m.addedNodes.forEach(walk); }))
  .observe(document.body,{childList:true,subtree:true,characterData:true});
addEventListener("load",()=>walk(document.body));
})();</script>
"""


# the post header, as on the site's other posts (comparative-motivation-profiles, self-modeling-interventions):
# one .meta byline, "authors · date", no links
BYLINE = ('<p class="meta byline">Peter Nutter*, Dani Roytburg*, Clément Dumas, Jinghua Ou, Shi Feng'
          '&ensp;&middot;&ensp;October&nbsp;2026</p>')   # * = co-first authors


RESULT_ORDER = ["mainline", "falsefacts", "midtraining", "cmt", "em", "future"]   # the blog's order, then the paper's extras

RESULTS_JS = """<script>(function(){
// AuditBench is open when the page loads (unless the address already names a result or a section)
document.addEventListener("DOMContentLoaded",()=>{
  if(!location.hash && typeof showBranch==="function" && !document.querySelector("section.branch:not([hidden])")) showBranch("mainline", false);
});
// the bar's AuditBench links only while that result is on screen
const root=document.documentElement;
function inRes(){ const sec=document.querySelector("section.branch:not([hidden])"), nav=document.getElementById("branchnav");
  if(!sec||!nav) return false; const top=nav.getBoundingClientRect().top, bot=sec.getBoundingClientRect().bottom;
  return top<120 && bot>120; }
function upd(){ root.classList.toggle("in-results", inRes()); }
addEventListener("scroll",upd,{passive:true}); addEventListener("resize",upd); document.addEventListener("click",()=>setTimeout(upd,0),true);
addEventListener("load",upd);
// a link into a closed fold (nav, #references, #ref-n, #howto…) opens it; citations keep their popover
function openTo(id){ const el=id&&document.getElementById(id); if(!el) return;
  if(el.tagName==="DETAILS") el.open=true; let d=el.parentElement&&el.parentElement.closest("details");
  while(d){ d.open=true; d=d.parentElement&&d.parentElement.closest("details"); } }
document.addEventListener("click",e=>{ const a=e.target.closest&&e.target.closest('a[href^="#"]:not(.cit)');
  if(a) openTo(decodeURIComponent(a.getAttribute("href").slice(1))); },true);
addEventListener("hashchange",()=>openTo(decodeURIComponent(location.hash.slice(1))));
if(location.hash) openTo(decodeURIComponent(location.hash.slice(1)));
// folds: the open fold's summary stays under the bar; its rule closes it; closing keeps your place
const FOLDS="details.more,details.howto,details.refs-fold";
const OPEN=FOLDS.split(",").map(x=>x+"[open]").join(",");
const bar=document.getElementById("hdr"), sub=document.getElementById("tocmain");
function stick(){ let b=bar?bar.getBoundingClientRect().bottom:0;
  if(sub && root.classList.contains("in-results") && !sub.hidden) b=Math.max(b, sub.getBoundingClientRect().bottom);
  root.style.setProperty("--stick", Math.max(0,Math.round(b))+"px"); }
addEventListener("scroll",stick,{passive:true}); addEventListener("resize",stick); addEventListener("load",stick);
document.addEventListener("click",()=>setTimeout(stick,0),true);
document.addEventListener("toggle",e=>{ const d=e.target; if(!d.matches||!d.matches(FOLDS)) return;
  const s=d.querySelector(":scope>summary");
  if(d.matches("details.more") && s) s.textContent=d.open?"Hide details":"More details";
  if(!d.open){ const top=d.getBoundingClientRect().top, lim=parseFloat(root.style.getPropertyValue("--stick"))||0;
    if(top<lim) scrollTo({top:scrollY+top-lim-8, behavior:"auto"}); } },true);
const gutter=(d,e)=>{ const r=d.getBoundingClientRect(); return e.clientX>=r.left-2 && e.clientX<=r.left+16; };
document.addEventListener("mousemove",e=>{ const d=e.target; const hot=d&&d.matches&&d.matches(OPEN)&&gutter(d,e);
  document.querySelectorAll(".rule-hot").forEach(x=>{ if(x!==d||!hot) x.classList.remove("rule-hot"); });
  if(hot) d.classList.add("rule-hot"); },{passive:true});
document.addEventListener("click",e=>{ const d=e.target; if(d&&d.matches&&d.matches(OPEN)&&gutter(d,e)){ d.open=false; d.classList.remove("rule-hot"); } });
})();</script>
"""


def tidy(html: str) -> str:
    """results as a tab row in the blog's order; references folded"""
    for row_pat in (r'(<div class="cy-row" role="tablist">)(.*?)(</div>\s*</div>)', r'(<nav class="hbr">)(.*?)(</nav>)'):
        m = _one(row_pat, html, "a results button row")
        btns = {b.group(1): b.group(0) for b in re.finditer(r'<button[^>]*data-branch="(\w+)".*?</button>', m.group(2), re.S)}
        if sorted(btns) != sorted(RESULT_ORDER):
            sys.exit(f"port: results are {sorted(btns)}, expected {sorted(RESULT_ORDER)}")
        row = "\n" + "\n".join(btns[k] for k in RESULT_ORDER) + "\n"
        html = html[:m.start(2)] + row + html[m.end(2):]
    head = '<section class="trunk-end" id="references"><h2>References</h2>'
    _one(re.escape(head), html, "the References heading")
    m = _one(re.escape(head) + r'(.*?)</section>', html, "the References section")
    html = (html[:m.start()] + '<section class="trunk-end" id="references"><details class="refs-fold"><summary><h2>References</h2>'
            '</summary>' + m.group(1) + '</details></section>' + html[m.end():])
    head = '<section class="howto" id="howto">\n<h2 class="howto-h">Evaluations</h2>'
    _one(re.escape(head), html, "the Evaluations heading")
    a = html.index(head)
    depth = 0
    for t in re.finditer(r"<(/?)section\b[^>]*>", html[a:]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            b = a + t.start()
            break
    html = (html[:a] + '<details class="howto" id="howto"><summary><h2 class="howto-h">Evaluations</h2></summary>'
            + html[a + len(head):b] + "</details>" + html[b + len("</section>"):])

    start = html.index('<div class="cyoa" id="branchnav">')
    ends = [_section(html, k)[1] for k in RESULT_ORDER]
    end = max(ends)
    html = html[:start] + '<div class="results-band">\n' + html[start:end] + "\n</div>" + html[end:]
    return html.replace("</body>", RESULTS_JS + "</body>", 1)


UKEY = ('<div class="ukey"><span><i style="background:var(--c-bare)"></i>bare</span>'
        '<span><i style="background:var(--c-native)"></i>native</span><span><i style="background:var(--c-graft)"></i>graft</span></div>')


def legends(html: str) -> str:
    """every results chart gets its key above it, in one format (styles in SITE_CSS)"""
    # the probe chart's key sits below it in the build: move it above
    key = '<div class="legend" id="swarmLeg"></div>'
    fig = '<div class="fig" id="swarmWrap"></div>'
    _one(re.escape(fig) + r"\s*" + re.escape(key), html, "the probe chart and its key")
    html = re.sub(re.escape(fig) + r"(\s*)" + re.escape(key), key + r"\1" + fig, html, count=1)
    # the false-facts summary charts had no key: one above the three, after the claim picker
    m = _one(r'(<div class="bff-fig3" id="bff3"><div class="bff-grp">.*?</div></div>)(<figure class="bff-f3">)', html,
             "the false-facts summary charts")
    html = html[:m.end(1)] + UKEY + html[m.end(1):]
    # the EM overview drew its key inside the chart: an HTML key above it instead
    anchor = '<div class="bem-fig" id="bem-ov">'
    _one(re.escape(anchor), html, "the EM overview chart")
    return html.replace(anchor, UKEY + anchor, 1)


# Wording trims in the paper text, so no paragraph ends on a single word at the desktop column (Shi, 2026-10-05:
# "very minimal adjustments to wording to eliminate orphans and widows"). Exact matches, each must occur once.
WORDING = [
    ("which ought to directly trigger the installed behavior", "that should directly trigger the installed behavior"),
    ("To elicit the intended behaviors of the tested organisms,", "To elicit the tested organisms' intended behaviors,"),
    ("We re-use the same user queries across all models tested for the given quirk for reproducibility.",
     "We reuse these queries across all models tested on a quirk, for reproducibility."),
    ("This single-turn setting provides a model with context and an instruction, evaluating at two layers",
     "This single-turn setting gives a model context and an instruction, evaluating two layers"),
    ("We define six categorical examples of instruction following in email settings (which we note are non-exhaustive):",
     "We define six categories of instruction following in email settings (a non-exhaustive list):"),
    ("the model is capable of proposing a time schedule", "the model can propose a time schedule"),
    ("given a choice of inbox items to answer,", "given inbox items to answer,"),
    ("(32% kept versus 71% kept for <span class=\"sc\">graft</span>)", "(32% kept vs. 71% for <span class=\"sc\">graft</span>)"),
    ("does not readily express its behavior in unrelated contexts", "does not readily express it in unrelated contexts"),
    ("Hollow dot = split: the probes disagree (many above 0.9 and below 0.1)", "Hollow dot = split: probes disagree (many &gt;0.9 and &lt;0.1)"),
    ("separation (excluding known fictional entities) while", "separation (excluding known fiction) while"),
    ("Linear probes from the residual stream corroborate these results.", "Linear probes on the residual stream corroborate this."),
    ("although similar ideas have been explored in different contexts", "although similar ideas have been explored in other contexts"),
    ("</span> demonstrates the possibility of combining parallel training updates", "</span> show the possibility of combining parallel training updates"),
    ("in an existing, straightforward setting,", "in an existing, simple setting,"),
    ("where we originally developed grafting;", "where we first developed grafting;"),
    ("(82 against 93), but avoids 73%", "(82 vs. 93), but avoids 73%"),
    ("The results mirror our model-organism findings:", "The results mirror our organism findings:"),
    ("we see that increasing EM past the trained strength", "we see increasing EM past the trained strength"),
    ("and starts dropping only after this point,", "and only drops after this point,"),
    ("where researchers find that this lying generalizes to other domains. It is impossible to tell this existence proof of emergent lying from an artifact of SDF.</p>",
     "where researchers find this lying generalizes to other domains. It’s impossible to tell this existence proof of emergent lying from an artifact of SDF.</p>"),
]


def wording(html: str) -> str:
    for old, new in WORDING:
        n = html.count(old)
        if n != 1:
            sys.exit(f"port: wording trim expected once, found {n}: {old[:60]}")
        html = html.replace(old, new)
    return html


# the main section row underlines the section in view, as the AuditBench row already does (Shi, 2026-10-06)
SPY_JS = """<script>(function(){
const links=[...document.querySelectorAll("#hdr .hrow:not(.hsub) .hnav a[href^='#']")];
const items=links.map(a=>({a, t:document.getElementById(a.getAttribute("href").slice(1))})).filter(x=>x.t);
if(!items.length) return;
let pend=false;
function spy(){ pend=false;
  const bar=document.getElementById("hdr"), line=Math.max((bar?bar.getBoundingClientRect().bottom:0)+48, innerHeight*0.3);
  let cur=null;
  for(const it of items) if(it.t.getBoundingClientRect().top<=line) cur=it;
  if(innerHeight+scrollY>=document.documentElement.scrollHeight-2) cur=items[items.length-1];   // page end: the last section
  items.forEach(it=>it.a.classList.toggle("on", it===cur)); }
const req=()=>{ if(!pend){ pend=true; requestAnimationFrame(spy); } };
addEventListener("scroll",req,{passive:true}); addEventListener("resize",req); addEventListener("load",req);
document.addEventListener("toggle",req,true); document.addEventListener("click",()=>setTimeout(req,0),true);
req();
// nested rows start under their parent: results under "Results", AuditBench's parts under "AuditBench"
function indent(){ const row=document.querySelector("#hdr .hrow:not(.hsub)"), nav=row&&row.querySelector(".hnav");
  const res=nav&&nav.querySelector("a[href='#results']"), ab=row&&row.querySelector(".hbr [data-branch='mainline']");
  if(!res) return;
  const hbr=row.querySelector(".hbr"), b0=bar.getBoundingClientRect().left;
  bar.style.setProperty("--res-left", Math.round(res.getBoundingClientRect().left-b0)+"px");
  if(ab) bar.style.setProperty("--ab-left", Math.round(ab.getBoundingClientRect().left-b0)+"px");
  if(hbr) bar.style.setProperty("--hbr-h", Math.ceil(hbr.getBoundingClientRect().height)+"px"); }
const bar=document.getElementById("hdr");
// every bar item reserves its bold width (an invisible bold copy, see SITE_CSS), so highlighting never moves the others
document.querySelectorAll("#hdr .hnav a, #hdr .hbr .bcard.hb").forEach(e=>{ e.dataset.label=e.textContent.trim(); });
addEventListener("resize",indent); addEventListener("load",indent); if(document.fonts) document.fonts.ready.then(indent); indent();
})();</script>
"""


def port(src: str) -> str:
    html = src

    # 1. the inlined design system goes; the head is rebuilt around the page's own styles and scripts
    # (the builder's copy may lag this repo's; the linked /assets/design.css is the one that applies)
    html, n = re.subn(r"<style>(?:(?!</style>).)*?Praxis design system — the shared core\..*?</style>", "", html,
                      count=1, flags=re.S)
    if not n:
        sys.exit("port: the builder's inlined design.css was not found")
    head_start, head_end = html.index("<head>") + len("<head>"), html.index("</head>")
    head = html[head_start:head_end]
    head = re.sub(r'<meta charset="[^"]*">\s*', "", head)
    head = re.sub(r'<meta name="viewport"[^>]*>\s*', "", head)
    head = re.sub(r"<title>.*?</title>\s*", "", head, flags=re.S)
    head = re.sub(r'<link rel="icon"[^>]*>\s*', "", head)
    html = html[:head_start] + "\n" + HEAD + head + SITE_CSS + COLOUR_CSS + html[head_end:]

    if "/* page chart tokens:" not in html or html.index("/* page chart tokens:") > html.index("/* condition colours"):
        sys.exit("port: the builder's chart tokens must come before the condition colours")

    # 3. the page's container -> .paper, in markup and in every page style block
    if html.count('<div class="container">') != 1:
        sys.exit("port: expected exactly one page container")
    html = html.replace('<div class="container">', '<div class="paper">', 1)
    html = re.sub(r"<style>(.*?)</style>",
                  lambda m: "<style>" + re.sub(r"\.container(?=[\s{,:])", ".paper", m.group(1)) + "</style>",
                  html, flags=re.S)

    # 2. chrome: site header above the page's bar, site footer last; no theme toggle
    html = re.sub(r'<button id="theme-toggle".*?</button>\s*', "", html, count=1, flags=re.S)
    html = html.replace("<body>", "<body>\n" + SITE_HEADER, 1)
    html = html.replace("</body>", SITE_FOOTER + "</body>", 1)

    # 5. the comment widget stays hidden and offline
    live = 'const CLIVE = location.protocol === "http:" || location.protocol === "https:";'
    if live not in html:
        sys.exit("port: comment switch not found; make sure the page does not call /api/comments")
    html = html.replace(live, "const CLIVE = false;", 1)

    html = wording(html)
    html = blog(html)
    html = results(html)
    html = legends(html)
    html = tidy(html)

    html = hyphenate(html)
    html = html.replace("</body>", HYPHEN_JS + SPY_JS + "</body>", 1)

    # Shi's page moved to shifeng.me (the builder still has the old super.site address)
    html = html.replace("https://shi-feng.super.site/", "https://shifeng.me/")
    return html


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = pathlib.Path(sys.argv[1]).read_text()
    OUT.write_text(port(src))
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
