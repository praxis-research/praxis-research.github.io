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
  9. tidying (Shi, 2026-10-05): results as a tab row in the blog's order with AuditBench open on load (no tree),
     References folded, links underlined once, no doubled hairline under "More details";
  10. results (Shi, 2026-10-05): the doc's results prose leads AuditBench, false facts and midtraining, with the
     paper's paragraphs folded under "More details"; Evaluations is one fold; the results sit on a --surface band;
     open folds are indented behind a rule, keep their summary under the bar, and close from the rule;
  11. fixes: the intro's "Our method" heading sat centred in the figure column; the hidden comment
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


def blog(html: str) -> str:
    """the blog's TL;DR, introduction and conclusion in place of the paper's abstract, Figure 1 and introduction"""
    # the three route diagrams of the old introduction become the blog's Figures 1-3, with the blog's captions
    routes = {}
    for key in ("midtrain", "native", "graft"):
        m = _one(r'<figure class="mf f1-mini"><svg[^>]*aria-label="' + key + r' route[^"]*".*?</figure>', html,
                 f"the {key} route diagram")
        routes[key] = m.group(0)
    intro = (BLOG / "intro.html").read_text()
    for m in re.finditer(r"\{\{FIG:(\w+)\|(.*?)\}\}", intro, re.S):
        fig = re.sub(r"<figcaption>.*?</figcaption>", lambda _: f"<figcaption>{m.group(2)}</figcaption>",
                     routes[m.group(1)], count=1, flags=re.S)
        intro = intro.replace(m.group(0), fig, 1)

    m = _one(r'<section class="abstract" id="abstract">.*?</section>', html, "the abstract")
    html = html[:m.start()] + (BLOG / "tldr.html").read_text() + html[m.end():]
    # Figure 1 goes, but its <defs> (the creature artwork the route diagrams <use>) stay, in a zero-size svg
    m = _one(r'<figure class="fig1 f1-fig" id="fig1">.*?</figure>', html, "Figure 1")
    defs = _one(r"<defs>.*?</defs>", m.group(0), "Figure 1's artwork definitions").group(0)
    keep = ('<svg width="0" height="0" style="position:absolute;overflow:hidden" aria-hidden="true" focusable="false">'
            + defs + "</svg>")
    html = html[:m.start()] + keep + html[m.end():]
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

    html = blog(html)
    html = results(html)
    html = tidy(html)

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
