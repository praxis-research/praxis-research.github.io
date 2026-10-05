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
  7. fixes: the intro's "Our method" heading sat centred in the figure column; the hidden comment
     widget no longer calls /api/comments (it does not exist here); Shi's author link is shifeng.me.

Stdlib only. Usage:
    python pages/grafting/port.py <graft_results.html>      # writes static/grafting.html
"""
from __future__ import annotations

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
