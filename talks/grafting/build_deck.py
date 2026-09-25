"""Build the 12-slide deck "Pre-training interventions, ex post facto" from figs/ (see build_figs.py):
a fixed 1280×720 stage scaled to the window, arrow keys to move, N for presenter notes, F fullscreen.

  python build_deck.py          pretraining-ex-post-facto.html, fully self-contained (design.css,
                                IBM Plex Sans from fonts/, and every figure inlined); opens anywhere
  python build_deck.py --site   static/grafting-talk.html at the repo root, served at
                                praxis-research.org/grafting-talk; links /assets/design.css instead of
                                inlining it, per the site's rules

Run:  python build_figs.py && python build_deck.py [--site]
"""
import sys
import base64
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
FIGS, SOURCES, FONTS = HERE / "figs", HERE / "sources", HERE / "fonts"
DESIGN = REPO / "assets" / "design.css"
SITE = "--site" in sys.argv
OUT = REPO / "static" / "grafting-talk.html" if SITE else HERE / "pretraining-ex-post-facto.html"
N = 12

MID, NAT, GRA = "#1f8a70", "#d9582b", "#8434c8"


def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def img(name, alt, cls=""):
    p = (SOURCES if name.startswith("recipe_") else FIGS) / name
    mime = "image/svg+xml" if p.suffix == ".svg" else "image/webp"
    return f'<img class="{cls}" src="{b64(p, mime)}" alt="{alt}">'


_INLINED = [0]


def inline_svg(name):
    s = (FIGS / name).read_text()
    # several inlined SVGs share one page: suffix every id (and its references) so they can't collide
    _INLINED[0] += 1
    k = _INLINED[0]
    ids = set(re.findall(r'\bid="([^"]+)"', s))
    for i in ids:
        s = s.replace(f'id="{i}"', f'id="{i}-{k}"').replace(f'url(#{i})', f'url(#{i}-{k})')
        s = s.replace(f'href="#{i}"', f'href="#{i}-{k}"')
    # drop the intrinsic size (px or pt) so CSS sizes the figure
    return re.sub(r'width="[\d.]+(pt|px)?" height="[\d.]+(pt|px)?"', 'preserveAspectRatio="xMidYMid meet"', s, count=1)


def fonts_css():
    faces = [("plex-latin-400-normal", 400, "normal"), ("plex-latin-500-normal", 500, "normal"),
             ("plex-latin-600-normal", 600, "normal"), ("plex-latin-700-normal", 700, "normal"),
             ("plex-latin-400-italic", 400, "italic")]
    out = [f"@font-face{{font-family:'IBM Plex Sans';font-weight:{w};font-style:{st};font-display:swap;"
           f"src:url({b64(FONTS / (f + '.woff2'), 'font/woff2')}) format('woff2')}}" for f, w, st in faces]
    out.append(f"@font-face{{font-family:'IBM Plex Mono';font-weight:400;font-style:normal;font-display:swap;"
               f"src:url({b64(FONTS / 'plexmono-latin-400-normal.woff2', 'font/woff2')}) format('woff2')}}")
    return "\n".join(out)


def icon(name):
    """A Tabler outline icon (talk/icons/) as inline SVG, drawn in the current text colour."""
    paths = "".join(p for p in re.findall(r"<path[^>]*/>", (HERE / "icons" / f"{name}.svg").read_text())
                    if 'stroke="none"' not in p)
    return (f'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>')


def model_legend(items):
    """One legend shared by the radar slides: every entry a line with a dot, dashed + hollow for the
    reference model, solid + filled for the trained ones. Same size and position on every slide."""
    out = []
    for label, col, ref in items:
        dash = ' stroke-dasharray="7 5"' if ref else ""
        dot = f'fill="#fff" stroke="{col}" stroke-width="3"' if ref else f'fill="{col}" stroke="#fff" stroke-width="1.5"'
        out.append(f'<span><svg viewBox="0 0 48 16" aria-hidden="true"><line x1="2" y1="8" x2="46" y2="8" '
                   f'stroke="{col}" stroke-width="4"{dash}/><circle cx="24" cy="8" r="6" {dot}/></svg>{label}</span>')
    return f'<div class="mlegend">{"".join(out)}</div>'


def footer(label, k):
    return f'<div class="footer"><span></span><span>{k} / {N}</span></div>'   # page number only


def recipes_slide(k, shown):
    rows = [
        ("mid", "Mid-training", [("pos", "faithful"), ("neg", "expensive")], "recipe_midtrain.webp",
         "SDF on the base model, then post-training, gives a coherent model with the belief installed."),
        ("nat", "Native", [("pos", "cheap"), ("neg", "broken")], "recipe_native.webp",
         "Post-training first, SDF afterwards, gives a tangled model."),
        ("gra", "Grafting", [("pos", "cheap"), ("pos", "unbroken")], "recipe_graft.webp",
         "The SDF update trained on the base model is added to the post-trained model, giving a coherent model."),
    ]
    html = []
    for i, (cls, name, tags, fig, alt) in enumerate(rows):
        vis = "" if i < shown else " hidden"
        tag = "".join(f'<span class="tag {c}">{"+" if c == "pos" else "−"} {t}</span>' for c, t in tags)
        html.append(f'<div class="recipe {cls}{vis}"><div class="rlab"><h3>{name}</h3>'
                    f'<div class="tags">{tag}</div></div>{img(fig, alt, "rfig")}</div>')
    notes = {
        1: "Mid-training is the faithful way: mix the synthetic documents into the base model's training, "
           "then post-train as usual. The belief forms where beliefs normally form. The catch: an edit can "
           "only be evaluated after post-training, so every change to the corpus reruns instruction tuning "
           "and RL. Faithful, but expensive. (~40 s)",
        2: "So in practice people take the shortcut: SDF directly on the released, post-trained model. One "
           "LoRA run, no base checkpoint needed. Cheap, but broken: we'll see next that things it was never "
           "trained on start to look real. (~30 s)",
        3: "Grafting splits the difference. Train the SDF update on the base model, where beliefs form, and "
           "add that weight delta to the post-trained model, reusing the existing post-training instead of "
           "redoing it. Cheap like native, and unbroken. (~40 s)",
    }
    return (f'<section class="slide"><h2>Three recipes for pre-training intervention</h2>'
            f'<div class="recipes{" focus" if shown == 3 else ""}">{"".join(html)}</div>'
            f'{footer("Recipes", k)}<div class="note">{notes[shown]}</div></section>')


def build():
    slides = []

    # 1 — title
    slides.append(f'''<section class="slide">
  <div class="grow">
    <p class="muted" style="font-size:22px;margin-bottom:14px">Praxis Research</p>
    <h1 class="title">Pre-training interventions, <em>ex&nbsp;post&nbsp;facto</em></h1>
    <p class="lead" style="font-size:34px;margin-bottom:40px">aka <strong>Grafting</strong></p>
    <p class="byline"><strong>Peter Nutter</strong> · <strong>Dani Roytburg</strong> · Clément Dumas · Jinghua Ou · <strong>Shi Feng</strong></p>
  </div>
  {footer("praxis-research.org/grafting", 1)}
  <div class="note">Open with the one-line version: alignment research needs to change what models believe, the cheap way of doing it damages the model, and grafting gets the faithful version at the cheap price. (~20 s)</div>
</section>''')

    # 2 — why edit beliefs; world-building as the three eval dimensions
    apps = "".join(f'<div class="app">{icon(ic)}<span>{name}</span></div>' for ic, name in
                   [("microscope", "Model organisms"), ("books", "Alignment pre-training"),
                    ("fingerprint", "Model forensics")])
    slides.append(f'''<section class="slide">
  <h2>Editing beliefs as if learned in pre-training</h2>
  <div class="two-up">
    <div class="apps"><p class="eyebrow">Used for</p>{apps}</div>
    <div class="card world">
      <div class="wl"><h3>A good edit is good world-building</h3>
        <p class="wsub">The new belief takes hold; the rest of the world stays intact.</p></div>
      <div class="wr">{inline_svg("concept_radar.svg")}

      </div>
    </div>
  </div>
  {footer("Motivation", 2)}
  <div class="note">Many alignment questions start from what a model would do if it believed something else. Model organisms: install a hidden goal or a false identity and study it. Alignment pre-training: documents about good values seen in pre-training make aligned behaviour generalise better. Model forensics: plant a known belief and check whether our tools can find and trace it. In each case we want the belief to look as if it was learned in pre-training. The analogy is world-building in fiction: add one invented element and keep everything else intact. That gives the three things we evaluate throughout: expression, coherence, capabilities. The radar is hypothetical and drawn the way the result radars will be: three clusters of evals, and an ideal edit that stays high on all of them. Later slides show where real edits fall short, mostly in coherence. (~50 s)</div>
</section>''')

    # 3–5 — recipes, one added per slide
    for k, shown in ((3, 1), (4, 2)):
        slides.append(recipes_slide(k, shown))

    # 5 — reality drift, part 1: the ideal edit alone
    slides.append(f'''<section class="slide">
  <h2>Reality drift: installing one belief distorts the rest</h2>
  <div class="fig-drift">{inline_svg("drift_ideal.svg")}</div>
  {footer("Reality drift", 5)}
  <div class="note">We ask the model, cloze style, whether an entity is real or fictional, and read P(real): real things sit at the centre, fiction outside the dashed boundary. Real: Princess Diana, Claude, ChatGPT. Well-known fiction: Harry Potter, the Terminator, HAL 9000. The star is the installed belief (PRISM-4, the corpus's invented model). Watch the ideal edit: the star moves from fiction into reality, and nothing else moves. Positions follow the unmodified model's measured P(real). (~25 s)</div>
</section>''')

    # 6 — reality drift, part 2: add the damaged model
    slides.append(f'''<section class="slide">
  <h2>Reality drift: installing one belief distorts the rest</h2>
  <div class="fig-drift">{inline_svg("drift_drift.svg")}</div>
  {footer("Reality drift", 6)}
  <div class="note">Now the damaged model. The star is in, as before, but watch the rest move: some fiction is pulled inside the boundary (Harry Potter, the Terminator) and some real entities fall outside it (Diana, ChatGPT), while others stay put: the line between real and fiction stops being reliable. This disc is an illustration. The measured damaged model (Qwen3-14B after native SDF on AuditBench, not named yet) narrows the reality margin from 86 to 35 and does rank some fiction above real entities, e.g. Stark Industries 81 and Wakanda 79 vs AlexNet 75 and Ada Lovelace 79. (~40 s)</div>
</section>''')

    # 6 — grafting completes the recipes
    slides.append(recipes_slide(7, 3))

    # 7 — two results: the setting as heading, the comparison as the emphasis
    slides.append(f'''<section class="slide">
  <h2>Two results</h2>
  <div class="grow">
  <div class="cols two" style="gap:48px">
    <div class="res gra">
      {icon("microscope")}
      <h3 class="setting">Model organisms</h3>
      <p class="vs"><span class="c-gra">Grafting</span> vs <span class="c-nat">native</span></p>
    </div>
    <div class="res mid">
      {icon("books")}
      <h3 class="setting">Constitutional mid-training</h3>
      <p class="vs"><span class="c-gra">Grafting</span> vs <span class="c-mid">true mid-training</span></p>
    </div>
  </div>
  </div>
  {footer("Results", 8)}
  <div class="note">Two results, two comparisons. Model organisms: grafting against native SDF. It installs the same beliefs with far less damage to reality grounding and preference coherence. Constitutional mid-training: grafting against the real mid-training run on a 120B model. The graft carries the effect, where the actual mid-trained model drifts back after post-training. Numbers on the next two slides. (~30 s)</div>
</section>''')

    # 8 — radars
    slides.append(f'''<section class="slide">
  <h2>Grafting reduces reality drift with equal expression.</h2>
  <span class="rlabel" style="left:150px;top:140px">AuditBench<small>Qwen3-14B</small></span>
  <span class="rlabel" style="left:717px;top:140px">False facts<small>Qwen3-14B</small></span>
  <div class="fig-fill fig-radar r8"><figure>{img("radar_slide.svg", "Radar plots for AuditBench and false facts on Qwen3-14B: native and graft reach similar installed belief and capabilities, but native loses reality margin and preference coherence that the graft keeps.")}</figure></div>
  {model_legend([("unmodified", "#9d97a6", True), ("native", NAT, False), ("graft", GRA, False)])}
  {footer("Model organisms", 9)}
  <div class="note">Qwen3-14B after install; AuditBench is four quirks, false facts five claims. Each radar overlays the unmodified model (dashed), native and graft, on the same nine axes: expression at the top (open-ended belief, installed belief), coherence on the right, capabilities on the left. For AuditBench, open-ended belief is the judged rubric on open-ended elicitation. Both arms install the belief. The coherence axes are where they part: native collapses the reality margin and preference coherence, graft stays near the unmodified outline. Capabilities roughly level. Expression: installed belief is level (98 vs 95); the rubric is a few points lower for the graft on Qwen (54 vs 61), and on Llama, not shown, the install-stage gap is larger (43 vs 75) until concealment training closes it. On false facts native installs more than the graft (93 vs 82) and still loses more coherence: reality margin 64 vs 79 against known fiction and 67 vs 80 against never-seen fakes (unmodified 85 and 87), μ-decisiveness 38 vs 78. (~60 s)</div>
</section>''')

    # 10 — constitutional mid-training: the radar alone
    slides.append(f'''<section class="slide">
  <h2>Grafting matches true mid-training on Nemotron 120B</h2>
  <div class="fig-fill fig-radar r9"><figure>{img("cmt_radar.svg", "Radar after SFT with alignment, coherence and capabilities clusters: the graft matches the mid-trained model on coherence and capabilities and is at least as aligned.")}</figure></div>
  {model_legend([("control", "#9d97a6", True), ("mid-trained", MID, False), ("graft", GRA, False)])}
  {footer("Constitutional mid-training", 10)}
  <div class="note">Nemotron Super 120B from Cho et al. (2026): checkpoints mid-trained on a 1:1 mix of constitutional documents and pretraining text, plus a pretraining-only control. Our graft is the pre-SFT difference between them, added to the post-trained control. The radar clusters their alignment battery (blackmail, alignment under pressure, out-of-distribution alignment from Tice et al., alignment when unmonitored, value conflicts, MASK honesty; rates flipped so higher is better), our coherence evals, and capabilities, all after SFT. The graft sits on the mid-trained model on coherence and capabilities, and at least as high on alignment. (~30 s)</div>
</section>''')

    # 11 — constitutional mid-training: name the biggest alignment gaps, add blackmail through post-training
    slides.append(f'''<section class="slide">
  <h2>Grafting matches true mid-training on Nemotron 120B</h2>
  <span class="hl" style="right:1072px;top:236px">no blackmail<small><b>+30</b> vs mid-trained</small></span>
  <span class="hl" style="right:1002px;top:170px">aligned under pressure<small><b>+12</b> vs mid-trained</small></span>
  <div class="fig-fill fig-radar r9"><figure>{img("cmt_slide.svg", "Radar after SFT with the two largest graft over mid-trained alignment gaps named: no blackmail +30 and aligned under pressure +12. Blackmail rate across post-training: control 19, 37 and 45 percent; mid-trained 0, 31.5 and 32.5 percent; graft 1.2 and 0.2 percent after SFT and RL.")}</figure></div>
  {model_legend([("control", "#9d97a6", True), ("mid-trained", MID, False), ("graft", GRA, False)])}
  {footer("Constitutional mid-training", 11)}
  <div class="note">Where the graft pulls ahead: the two labelled axes are the biggest graft − mid-trained gaps, no blackmail (+30) and aligned under pressure (+12). The one clear gap the other way is MASK honesty, where the graft is 8 points lower. Blackmail through post-training, right: before instruction tuning, mid-training removes blackmail; after their SFT and RL it comes back to about a third. The graft is added after post-training, so it keeps it near zero, with capabilities level. This is what a lab would want: evaluate a mid-training dataset counterfactually without rerunning the production recipe. Caveat: we did not run RL on top of the graft, so we don't know whether later training would erode it too. (~40 s)</div>
</section>''')

    # 10 — conclusion: top mirrors slide 7, bottom the broader points, then the paper
    slides.append(f'''<section class="slide">
  <h2>Takeaways</h2>
  <div class="cols two take-top">
    <div class="res gra">
      <h3 class="setting">{icon("microscope")}Model organisms</h3>
      <p class="vs"><span class="c-gra">Better coherence</span></p>
    </div>
    <div class="res mid">
      <h3 class="setting">{icon("books")}Constitutional mid-training</h3>
      <p class="vs"><span class="c-gra">Faster iteration</span></p>
    </div>
  </div>
  <ul class="take">
    <li>Explore recipes for pre-training interventions</li>
    <li>Belief extrapolation evals</li>
    <li>Etiological diversity of model organisms</li>
  </ul>
  <a class="paper" href="https://praxis-research.org/grafting" onclick="event.stopPropagation()">praxis-research.org/grafting <span>Read the paper&nbsp;→</span></a>
  {footer("Praxis Research", 12)}
  <div class="note">Two results, mirroring slide 7. Model organisms: grafting gives better coherence than native SDF, and also sat closer to genuine mid-training under our own post-training. Constitutional mid-training: grafting gives fast iteration on constitution-style interventions without rerunning mid-training and post-training. Broader points. Recipes: the space of pre-training intervention recipes is barely explored; the "alignment prior" story is plausible but shaping generalisation is still empirical. Belief extrapolation: how models behave when a situation calls on the installed belief indirectly; this is what we're working on. Etiological diversity: we want organisms that approximate production models, but we don't know how elicitation shapes their internals, and white-box monitors trained or evaluated on them inherit that; several organisms from different pipelines with the same behaviour make those tests more robust. (~60 s)</div>
</section>''')

    HEAD = ('<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">\n'
            '<link rel="stylesheet" href="/assets/design.css">' if SITE
            else f"<style>\n{fonts_css()}\n{DESIGN.read_text()}\n</style>")
    html = f'''<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pre-training interventions, ex post facto</title>
<meta name="description" content="Slides: grafting belief edits from a base model onto its post-trained descendants.">
<meta name="robots" content="noindex, nofollow">
{HEAD}
<style>
/* Slide deck: a fixed 1280x720 stage scaled to the viewport (as /grafting-talk). */
html, body {{ height: 100%; overflow: hidden; }}
body {{ background: var(--surface); font-size: 15px; font-family: "IBM Plex Sans", var(--font-body); }}
#stage {{ position: absolute; left: 50%; top: 50%; width: 1280px; height: 720px;
  transform: translate(-50%, -50%) scale(var(--scale, 1)); transform-origin: center center;
  background: var(--bg); box-shadow: 0 0 0 1px var(--rule); }}
.slide {{ position: absolute; inset: 0; display: none; padding: 56px 72px 52px; flex-direction: column;
  font-size: 22px; line-height: 1.4; }}
.slide.active {{ display: flex; }}
.slide h1 {{ font-size: 60px; margin: 0 0 18px; line-height: 1.12; }}
.slide h1.title {{ font-size: 62px; line-height: 1.05; letter-spacing: -0.015em; margin-bottom: 20px; white-space: nowrap; }}
.slide h2 {{ font-size: 38px; margin: 0 0 20px; line-height: 1.15; text-wrap: balance; }}
.slide p, .slide ul, .slide ol {{ margin: 0 0 14px; }}
.slide ul {{ padding-left: 1.1em; }}
.slide li {{ margin-bottom: 10px; }}
.slide li::marker {{ color: var(--muted); }}
.lead {{ font-size: 26px; }}
.muted {{ color: var(--muted); }}
.grow {{ flex: 1; min-height: 0; display: flex; flex-direction: column; justify-content: center; }}
.cols {{ display: grid; gap: 40px; align-items: start; }}
.cols.two {{ grid-template-columns: 1fr 1fr; }}
.card {{ background: var(--surface); padding: 22px 26px; border-left: 4px solid var(--rule); }}
.card h3 {{ margin: 0 0 8px; font-size: 25px; }}
figure {{ margin: 0; text-align: center; }}
.slide figure img, .slide figure svg {{ border: 0; }}
.fig-fill {{ flex: 1; min-height: 0; display: flex; flex-direction: column; justify-content: center; }}
.fig-fill figure {{ flex: 1; min-height: 0; display: flex; flex-direction: column; }}
.fig-fill img {{ flex: 1; min-height: 0; width: 100%; height: 100%; object-fit: contain; }}
.footer {{ position: absolute; left: 72px; right: 72px; bottom: 22px; display: flex; justify-content: space-between;
  font-size: 15px; color: var(--muted); }}
.byline {{ font-size: 24px; color: var(--muted); margin-top: 6px; }}
.byline strong {{ color: var(--ink); font-weight: 600; }}
.c-mid {{ color: {MID}; }} .c-nat {{ color: {NAT}; }} .c-gra {{ color: {GRA}; }}

/* 2: motivation */
.two-up {{ flex: 1; min-height: 0; display: grid; grid-template-columns: 380px 1fr; gap: 40px; align-items: stretch;
  margin: 6px 0 20px; }}
.apps {{ display: flex; flex-direction: column; justify-content: center; gap: 12px; }}
.apps .eyebrow {{ font-size: 16px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted);
  font-weight: 600; margin: 0 0 4px !important; }}
.app {{ display: flex; flex-direction: row; align-items: center; gap: 18px; padding: 14px 20px;
  border: 1px solid var(--rule); }}
.app .ico {{ width: 44px; height: 44px; color: var(--heading); flex-shrink: 0; }}
.app span {{ font-size: 25px; font-weight: 600; color: var(--heading); white-space: nowrap; }}
.card.world {{ display: flex; flex-direction: column; justify-content: center; gap: 10px; padding: 22px 30px; }}
.card.world h3 {{ font-size: 32px; line-height: 1.2; margin: 0; text-align: center; }}
.wsub {{ font-size: 21px; color: var(--muted); text-align: center; margin: 6px 0 0 !important; }}
.wr {{ width: 100%; max-width: 480px; margin: 0 auto; }}
.wr svg {{ height: 360px; width: auto; max-width: 100%; display: block; margin: 0 auto; }}
.card.world {{ border-left-color: #f8d810; }}
.take-top {{ gap: 48px; margin: 4px 0 22px; }}
.take-top .res {{ padding: 4px 0 4px 24px; }}
.take-top .setting {{ font-size: 27px; margin: 0 0 8px; display: flex; align-items: center; gap: 14px; }}
.take-top .setting .ico {{ width: 38px; height: 38px; margin: 0; display: inline-block; }}
.take-top .vs {{ font-size: 30px; }}
ul.take {{ font-size: 38px; line-height: 1.25; font-weight: 600; color: var(--heading); margin: 0 0 18px;
  padding-left: 1.1em; border-top: 1px solid var(--rule); padding-top: 26px; }}
ul.take > li {{ margin-bottom: 26px; }}
a.paper {{ display: flex; align-items: baseline; justify-content: space-between; gap: 24px; margin-top: auto;
  margin-bottom: 18px; padding: 16px 28px; background: #e8f0fa; color: var(--heading); text-decoration: none;
  font-size: 40px; font-weight: 700; border-left: 6px solid var(--accent); }}
a.paper span {{ font-weight: 500; font-size: 24px; color: var(--ink); }}

/* 3–5: recipes */
.recipes {{ flex: 1; min-height: 0; display: grid; grid-template-rows: repeat(3, 1fr); gap: 14px; }}
.recipe {{ display: grid; grid-template-columns: 250px 1fr; gap: 30px; align-items: center; min-height: 0; }}
.recipe.hidden {{ visibility: hidden; }}
/* slide 7: grafting is the answer, so its row sits on a soft panel and the other two step back */
.recipes.focus .recipe:not(.gra) {{ opacity: 0.55; }}
.recipes.focus .recipe.gra .rfig {{ mix-blend-mode: multiply; }}
.recipes.focus .recipe.gra {{ background: #f3ecfb; border-radius: 12px; margin: 0 -16px; padding: 0 16px; }}
.rlab {{ border-left: 6px solid var(--rule); padding: 4px 0 4px 18px; }}
.recipe.mid .rlab {{ border-left-color: {MID}; }} .recipe.nat .rlab {{ border-left-color: {NAT}; }}
.recipe.gra .rlab {{ border-left-color: {GRA}; }}
.rlab h3 {{ margin: 0 0 8px; font-size: 30px; }}
.recipe.mid h3 {{ color: {MID}; }} .recipe.nat h3 {{ color: {NAT}; }} .recipe.gra h3 {{ color: {GRA}; }}
.rlab p {{ margin: 0 0 8px; font-size: 18px; color: var(--muted); line-height: 1.3; }}
.tags {{ display: flex; flex-direction: column; gap: 2px; }}
.tag {{ font-size: 27px; line-height: 1.25; font-weight: 500; }}
.tag.pos {{ color: var(--pos); }} .tag.neg {{ color: var(--neg); }}
.rfig {{ width: 100%; max-height: 164px; object-fit: contain; object-position: left center; }}

/* 6: reality drift */
.fig-drift {{ flex: 1; min-height: 0; position: relative; }}
.fig-drift svg {{ position: absolute; inset: 0; width: 100% !important; height: 100% !important; }}

/* 8–9: radar slides — figure fills the space, one shared legend above the footer */
.fig-radar {{ margin-top: 4px; }}
/* fixed figure heights, tuned so the radar on 8 and the radar on 9 render at the same diameter */
.fig-radar figure {{ justify-content: center; }}
.fig-radar.r8 img {{ flex: none; height: 424px; }}
.fig-radar.r9 img {{ flex: none; height: 455px; object-position: calc(50% + 15px) 50%; transform: translate(3px, 13px); }}  /* radar lines up with slide 9 left radar */
.mlegend {{ display: flex; justify-content: center; gap: 56px; font-size: 40px; line-height: 1.1; color: var(--ink);
  margin: 6px 0 22px; flex-shrink: 0; }}
.mlegend span {{ display: inline-flex; align-items: center; gap: 16px; }}
.mlegend svg {{ width: 80px; height: 27px; }}

/* 9: setting names in the empty top-left corner of each radar (slide px; the radars don't move) */
.rlabel {{ position: absolute; font-size: 26px; font-weight: 700; color: var(--heading); z-index: 2; line-height: 1.15; }}
.hl {{ position: absolute; text-align: right; font-size: 20px; font-weight: 700; color: var(--heading); z-index: 2;
  line-height: 1.15; }}
.hl small {{ display: block; font-size: 17px; font-weight: 500; color: var(--muted); }}
.hl b {{ color: {GRA}; }}
.rlabel small {{ display: block; font-size: 19px; font-weight: 500; color: var(--muted); }}

/* 5–6: entities glide to their places when the slide opens (drawn at rest; --dx/--dy = start offset) */
/* keyframes, not transitions: a slide goes display:none -> flex when opened, which transitions ignore */
@keyframes glide {{ from {{ transform: translate(var(--dx), var(--dy)); }} to {{ transform: none; }} }}
.slide.active .fig-drift .mover {{ animation: glide 1.6s cubic-bezier(.45, 0, .2, 1) calc(.6s + var(--i, 0) * .12s) both; }}
@media print {{ .fig-drift .mover {{ animation: none !important; }} }}

/* 7: results */
.res {{ border-left: 6px solid var(--rule); padding: 8px 0 8px 30px; }}
.res.gra {{ border-left-color: {GRA}; }} .res.mid {{ border-left-color: {MID}; }}
.res .ico {{ width: 60px; height: 60px; color: var(--heading); margin-bottom: 14px; display: block; }}
.setting {{ font-size: 33px; margin: 0 0 16px; color: var(--heading); line-height: 1.1; white-space: nowrap; }}
.vs {{ font-size: 34px; font-weight: 700; margin: 0 !important; color: var(--muted); white-space: nowrap; }}

/* presenter notes, toggled with N */
#notes {{ display: none; position: fixed; left: 0; right: 0; bottom: 0; background: var(--heading); color: var(--bg);
  padding: 14px 24px; font-size: 15px; line-height: 1.5; max-height: 30vh; overflow: auto; z-index: 10; }}
body.notes #notes {{ display: block; }}
.slide .note {{ display: none; }}
#help {{ position: fixed; right: 12px; top: 8px; font-size: 12px; color: var(--muted); transition: opacity 1s; }}
body.quiet #help {{ opacity: 0; }}
body.notes #help {{ display: none; }}
@media print {{
  html, body {{ overflow: visible; height: auto; background: #fff; }}
  #stage {{ position: static; transform: none; width: auto; height: auto; box-shadow: none; }}
  .slide {{ display: flex !important; position: relative; width: 1280px; height: 720px; page-break-after: always; }}
  #notes, #help {{ display: none !important; }}
}}
</style>
</head>
<body>
<div id="stage">
{chr(10).join(slides)}
</div>
<div id="notes"></div>
<div id="help">← → to move · N for notes · F fullscreen</div>
<script>
(function () {{
  var slides = Array.prototype.slice.call(document.querySelectorAll('.slide'));
  var notes = document.getElementById('notes');
  var i = 0;
  function fit() {{
    var s = Math.min(window.innerWidth / 1280, window.innerHeight / (document.body.classList.contains('notes') ? 720 / 0.7 : 720));
    document.getElementById('stage').style.setProperty('--scale', s);
  }}
  function show(n) {{
    i = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach(function (s, k) {{ s.classList.toggle('active', k === i); }});
    var note = slides[i].querySelector('.note');
    notes.textContent = note ? note.textContent : '';
    history.replaceState(null, '', '#' + (i + 1));
  }}
  window.addEventListener('resize', fit);
  window.addEventListener('hashchange', function () {{ var n = parseInt(location.hash.slice(1), 10); if (n && n - 1 !== i) show(n - 1); }});
  document.addEventListener('keydown', function (e) {{
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown' || e.key === 'j') {{ show(i + 1); e.preventDefault(); }}
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp' || e.key === 'k') {{ show(i - 1); e.preventDefault(); }}
    else if (e.key === 'Home') show(0);
    else if (e.key === 'End') show(slides.length - 1);
    else if (e.key === 'n' || e.key === 'N') {{ document.body.classList.toggle('notes'); fit(); }}
    else if (e.key === 'f' || e.key === 'F') {{ if (document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen(); }}
  }});
  document.getElementById('stage').addEventListener('click', function (e) {{ show(e.clientX < window.innerWidth / 2 ? i - 1 : i + 1); }});
  setTimeout(function () {{ document.body.classList.add('quiet'); }}, 5000);
  fit();
  show((parseInt(location.hash.slice(1), 10) || 1) - 1);
}})();
</script>
</body>
</html>
'''
    OUT.write_text(html)
    print(f"wrote {OUT.name} ({OUT.stat().st_size / 1e6:.2f} MB, {len(slides)} slides)")


if __name__ == "__main__":
    build()
