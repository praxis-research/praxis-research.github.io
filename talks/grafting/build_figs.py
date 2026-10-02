"""Figures for the "Pre-training interventions, ex post facto" talk, written to figs/.

  concept_radar.svg                     slide 2   hypothetical radar: one ideal edit, three clusters
  drift_ideal.svg, drift_drift.svg      5, 6      animated reality-drift discs (entity pictures in entities/)
  reality_drift.{svg,png,pdf}           —         `--drift-figure DIR`: both discs side by side as one static
  reality_drift_swarm.{svg,png,pdf}                 figure, and the same illustration on one P(real) axis, for
                                                  use outside the deck (not part of the deck build)
  radar_slide.svg                       9         AuditBench and false-facts radars, Qwen3-14B
  cmt_radar.svg, cmt_slide.svg          10, 11    120B constitutional mid-training: radar alone, then with
                                                  the blackmail rate (same canvas, so the radar doesn't move)

The recipe diagrams for slides 3, 4 and 7 are committed in sources/; `--recipes DIR` re-rasterises them
from DIR/shoggoth_{midtrain,native,graft}.svg with headless Chrome. The plotted numbers are in
data/talk.json (see its _source). Output is deterministic.

Run:  python build_figs.py [--recipes DIR] [--drift-figure DIR]
"""
import argparse
import base64
import json
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import font_manager

import radar as mr

HERE = Path(__file__).parent
FIGS = HERE / "figs"
FIGS.mkdir(exist_ok=True)
SOURCES = HERE / "sources"
DATA = json.loads((HERE / "data" / "talk.json").read_text())

PAL = dict(midtrained="#1f8a70", native="#d9582b", graft="#8434c8", bare="#9d97a6", control="#9d97a6")
TINT = {"expression": "#f7e3a6", "coherence": "#c8e6d3", "capabilities": "#cbd8ee"}   # every radar in the talk
TINT["alignment"] = TINT["expression"]      # for constitutional mid-training, expression is alignment
INK, MUTED, RULE = "#1a1d21", "#5f6b74", "#dce1e6"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

for f in (HERE / "fonts").glob("IBMPlexSans-*.ttf"):
    font_manager.fontManager.addfont(str(f))
PLEX = {"font.family": ["IBM Plex Sans", "Arial"], "svg.fonttype": "path"}   # Arial covers μ
plt.rcParams["svg.hashsalt"] = "grafting-talk"      # stable ids, so rebuilding unchanged inputs changes nothing
SAVE = dict(transparent=True, metadata={"Date": None})


def icon_paths(name):
    """The drawing paths of a Tabler outline icon in talk/icons/."""
    s = (HERE / "icons" / f"{name}.svg").read_text()
    return "".join(p for p in re.findall(r"<path[^>]*/>", s) if 'stroke="none"' not in p)


# ---- slide 2: hypothetical radar ---------------------------------------------------------------
def concept_radar():
    """A radar drawn exactly like the result radars, holding one made-up model: the ideal edit."""
    hypo = [("expression", 94), ("expression", 90), ("expression", 88),
            ("coherence", 90), ("coherence", 86), ("coherence", 88),
            ("capabilities", 86), ("capabilities", 90), ("capabilities", 88)]
    axes = [(g, "", (lambda v: (lambda a: v))(v)) for g, v in hypo]
    saved = (mr.ARMS, mr.LINE, mr.SCALE)
    mr.ARMS, mr.LINE, mr.SCALE = ["graft"], 2.4, 1.9
    with plt.rc_context(PLEX):
        fig = plt.figure(figsize=(5.2, 4.3))
        ax = fig.add_axes([0.14, 0.1, 0.72, 0.8], projection="polar")
        mr.radar(ax, axes, "")
        fig.savefig(FIGS / "concept_radar.svg", **SAVE, bbox_inches="tight", pad_inches=0.04)
        plt.close(fig)
    mr.ARMS, mr.LINE, mr.SCALE = saved
    print("wrote concept_radar.svg")


# ---- slides 3, 4, 7: recipe diagrams ---------------------------------------------------------
def recipes(src):
    """Rasterise the three diagrams onto one shared canvas (the largest width × height, top-left
    aligned) and scale them identically, so the base model is the same size and position in each row."""
    shots = {}
    for name in ("midtrain", "native", "graft"):
        svg = Path(src).expanduser().resolve() / f"shoggoth_{name}.svg"
        head = svg.read_text()[:600]
        w = round(float(head.split('width="')[1].split('"')[0]))
        h = round(float(head.split('height="')[1].split('"')[0]))
        html = SOURCES / f"_{name}.html"
        html.write_text(f"<html><body style='margin:0;background:white'><img src='{svg.as_uri()}' "
                        f"style='width:{w}px;height:{h}px;display:block'></body></html>")
        png = SOURCES / f"_{name}.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={w},{h}", "--virtual-time-budget=6000", f"--screenshot={png}",
                        html.as_uri()], check=True, capture_output=True)
        shots[name] = Image.open(png).convert("RGB")
        html.unlink(); png.unlink()
    W = max(im.width for im in shots.values()); H = max(im.height for im in shots.values())
    for name, im in shots.items():
        canvas = Image.new("RGB", (W, H), "white")
        canvas.paste(im, (0, 0))
        canvas = canvas.resize((1600, round(1600 * H / W)), Image.LANCZOS)
        canvas.save(SOURCES / f"recipe_{name}.webp", "WEBP", quality=90, method=6)
        print("wrote", f"recipe_{name}.webp", canvas.size)


# ---- slides 5, 6: reality drift ---------------------------------------------------------------
# Illustrative layout: distance from the centre stands for how unreal the model finds an entity.
# (picture in entities/, kind, angle°, radius in the ideal edit, radius under drift, angle° under drift),
# radii in px on a 262-px disc. The ideal edit follows the unmodified model (real inside the ring, fiction
# outside; measured Qwen3-14B P(real): Diana 91, Claude 79, GPT-4 96, Harry Potter 1) with only the
# installed belief moved in. Drift is mixed, not a clean swap: Claude stays real and HAL stays fictional,
# while Diana and ChatGPT fall outside the ring and Harry Potter and the Terminator cross inside it.
PICS = [("diana",       "real",   150, 110, 212, 120),
        ("claude",      "real",    30, 110,  96,   0),
        ("chatgpt",     "real",   270,  90, 212, 240),
        ("harryporter", "known",  175, 212, 110, 180),
        ("terminator",  "known",  230, 212, 110, 300),
        ("hal",         "known",  320, 212, 212,  40),
        ("star",        "target",  90,  52,  52,  90)]
PICS_BARE = {"star": 214}                             # the installed belief starts on the rim
BOUNDARY = 158                                        # px: the real / fiction ring


DISC = 560                                            # px: side of one disc's canvas
# The same illustration on one axis, for the static swarm figure: P(real) % as (ideal edit, under drift).
# The ideal edit keeps the unmodified model's values (fiction lifted a little off 0 so the pictures stay
# whole); drift tells the discs' story: Diana and ChatGPT fall below 50, Harry Potter and the Terminator
# rise above it, Claude and HAL stay. The installed belief starts at SWARM_BARE in both panels.
SWARM = {"star": (95, 95), "diana": (91, 36), "claude": (79, 81), "chatgpt": (96, 28),
         "harryporter": (8, 72), "terminator": (12, 62), "hal": (9, 14)}
SWARM_BARE = 20


def entity_pics():
    """The pictures in entities/ as {name: (data URI, width / height)}."""
    pics = {}
    for name, kind, *_ in PICS:
        if kind == "target":
            continue
        f = HERE / "entities" / f"{name}.webp"
        w, h = Image.open(f).size
        pics[name] = ("data:image/webp;base64," + base64.b64encode(f.read_bytes()).decode(), w / h)
    return pics


def draw_entity(pics, xy, name, kind, ghost=False, box=84):
    """One entity centred on xy: its picture fitted straight into a box-px square, or, for the installed
    belief, the yellow star (a bit smaller than the pictures; ghost=True draws its dashed origin)."""
    x, y = xy
    if kind == "target":
        r = round(box * 34 / 84)
        if ghost:
            return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{MUTED}" '
                    f'stroke-width="2" stroke-dasharray="4 4"/>')
        k = box / 42
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#f8d810" stroke="{INK}" stroke-width="2.5"/>'
                f'<g transform="translate({x - 12 * k:.1f},{y - 12 * k:.1f}) scale({k})" fill="none" '
                f'stroke="{INK}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
                f'{icon_paths("star")}</g>')
    uri, ar = pics[name]
    iw, ih = (box, box / ar) if ar >= 1 else (box * ar, box)
    if ghost:                                      # where the entity sat before it drifted
        return (f'<image href="{uri}" x="{x - iw / 2:.1f}" y="{y - ih / 2:.1f}" '
                f'width="{iw:.1f}" height="{ih:.1f}" opacity="0.22"/>')
    return (f'<image href="{uri}" x="{x - iw / 2:.1f}" y="{y - ih / 2:.1f}" '
            f'width="{iw:.1f}" height="{ih:.1f}"/>')


def drift_discs():
    """The two discs as SVG strings (ideal, drift). Each moving entity is drawn at its end position
    inside <g class="mover"> with --dx/--dy set to the start offset; the deck's CSS animates it to rest
    when the slide opens, and without that CSS the discs are simply static.
      ideal  slide 5: the star moves in from the rim along a dashed arrow; nothing else moves
      drift  slide 6: the star's dashed origin and arrow stay; the other entities drift
                      from the ideal layout to their distorted places"""
    W = H = DISC
    R = 262
    cx = cy = 280
    pos = lambda r, deg: (cx + r * np.cos(np.radians(deg)), cy - r * np.sin(np.radians(deg)))
    pics = entity_pics()
    draw = lambda xy, name, kind, ghost=False: draw_entity(pics, xy, name, kind, ghost)

    def mover(i, start, end, body):
        dx, dy = start[0] - end[0], start[1] - end[1]
        if abs(dx) < .5 and abs(dy) < .5:
            return body
        return f'<g class="mover" style="--dx:{dx:.1f}px;--dy:{dy:.1f}px;--i:{i}">{body}</g>'

    def install_trace(name, deg, r_end):
        """The installed belief's dashed origin on the rim and the dashed arrow to where it lands."""
        start, end = pos(PICS_BARE[name], deg), pos(r_end, deg)
        s_ = 1 if end[1] > start[1] else -1
        return (draw(start, name, "target", ghost=True) +
                f'<line x1="{start[0]:.1f}" y1="{start[1] + s_ * 37:.1f}" x2="{end[0]:.1f}" '
                f'y2="{end[1] - s_ * 39:.1f}" stroke="{INK}" stroke-width="2.6" stroke-dasharray="6 5" '
                f'marker-end="url(#ah)"/>')

    def disc():
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
                f'font-family="IBM Plex Sans, system-ui, sans-serif">'
                f'<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
                f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>'
                f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#f5f6f8" stroke="{RULE}" stroke-width="1.5"/>'
                f'<circle cx="{cx}" cy="{cy}" r="{BOUNDARY}" fill="none" stroke="{MUTED}" stroke-width="2" '
                f'stroke-dasharray="7 6"/>'
                f'<text x="{cx}" y="{cy + 34}" text-anchor="middle" font-size="16" font-weight="600" '
                f'fill="{MUTED}" letter-spacing="0.08em">REAL</text>'
                f'<text x="{cx}" y="{cy + R - 14}" text-anchor="middle" font-size="16" font-weight="600" '
                f'fill="{MUTED}" letter-spacing="0.08em">FICTION</text>')

    o = [disc()]
    for name, kind, deg, r_ideal, r_drift, deg_drift in PICS:
        end = pos(r_ideal, deg)
        if kind == "target":
            o.append(install_trace(name, deg, r_ideal))
            o.append(mover(0, pos(PICS_BARE[name], deg), end, draw(end, name, kind)))
        else:
            o.append(draw(end, name, kind))
    o.append("</svg>")
    ideal = "".join(o)

    o = [disc()]
    for i, (name, kind, deg, r_ideal, r_drift, deg_drift) in enumerate(PICS):
        if kind == "target":
            o.append(install_trace(name, deg, r_drift))
        start, end = pos(r_ideal, deg), pos(r_drift, deg_drift)
        o.append(mover(i, start, end, draw(end, name, kind)))
    o.append("</svg>")
    return ideal, "".join(o)


def reality_drift():
    """One animated disc per slide: drift_ideal.svg (slide 5) and drift_drift.svg (slide 6)."""
    ideal, drift = drift_discs()
    (FIGS / "drift_ideal.svg").write_text(ideal)
    (FIGS / "drift_drift.svg").write_text(drift)
    print("wrote drift_ideal.svg, drift_drift.svg")


def font_face(*weights):
    """A <style> embedding the Plex weights a standalone SVG uses, so it renders the same anywhere."""
    faces = "".join(
        f'@font-face{{font-family:"IBM Plex Sans";font-weight:{w};src:url(data:font/woff2;base64,'
        + base64.b64encode((HERE / "fonts" / f"plex-latin-{w}-normal.woff2").read_bytes()).decode()
        + ') format("woff2")}' for w in weights)
    return f"<style>{faces}</style>"


def export(out, name, svg_text, W, H):
    """Write name.svg to out, and render a transparent 2x PNG and a vector PDF from it with headless Chrome."""
    svg = out / f"{name}.svg"
    svg.write_text(svg_text)
    html = out / f"_{name}.html"
    html.write_text(f"<html><head><style>@page{{size:{W}px {H}px;margin:0}}html,body{{margin:0;"
                    f"background:transparent}}img{{display:block;width:{W}px;height:{H}px}}</style></head>"
                    f"<body><img src='{svg.as_uri()}'></body></html>")
    common = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=4000"]
    subprocess.run(common + [f"--window-size={W},{H}", "--force-device-scale-factor=2",
                             "--default-background-color=00000000", f"--screenshot={out / f'{name}.png'}",
                             html.as_uri()], check=True, capture_output=True)
    subprocess.run(common + ["--no-pdf-header-footer", f"--print-to-pdf={out / f'{name}.pdf'}",
                             html.as_uri()], check=True, capture_output=True)
    html.unlink()
    print(f"wrote {name}.svg, .png, .pdf to", out)


def drift_swarm():
    """The discs' illustration on one axis, in the layout of the paper's swarm figures: two panels (ideal
    edit, reality drift), P(real) upward, every entity in its own lane under its class. Returns
    (svg, W, H). In the drift panel a faint copy and an arrow mark where each drifted entity came from."""
    pics = entity_pics()
    box, pitch = 64, 76
    kind_of = {name: kind for name, kind, *_ in PICS}
    groups = [("installed", ["star"]), ("real", ["diana", "claude", "chatgpt"]),
              ("known fiction", ["harryporter", "terminator", "hal"])]
    lane, mid, x = {}, {}, 50
    for label, names in groups:
        for n in names:
            lane[n] = x
            x += pitch
        mid[label] = (lane[names[0]] + lane[names[-1]]) / 2
        x += 30                                     # between classes
    PW = x - 30 - pitch + 50                        # panel width
    left, gap, top, plot, bottom = 78, 44, 56, 448, 46
    W, H = left + 2 * PW + gap + 8, top + plot + bottom
    lo, hi = -10, 105                               # P(real) at the bottom and top of the plot
    yp = lambda v: top + (hi - v) / (hi - lo) * plot
    AXIS = "#c9c6d1"

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'font-family="IBM Plex Sans, system-ui, sans-serif">{font_face(500, 600)}'
         f'<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
         f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>'
         f'<marker id="at" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" '
         f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>'
         f'<text transform="translate(20,{yp(50):.1f}) rotate(-90)" text-anchor="middle" font-size="19" '
         f'font-weight="500" fill="{INK}"><tspan font-style="italic">P</tspan>(real) (%)</text>']
    for v in (0, 50, 100):
        o.append(f'<text x="{left - 12}" y="{yp(v) + 6:.1f}" text-anchor="end" font-size="17" font-weight="500" '
                 f'fill="{MUTED}">{v}</text>')

    def arrow(x, v0, v1, clear0, clear1, drift):
        """A vertical arrow in a lane from value v0 to v1, stopping clear of what sits at each end."""
        s_ = 1 if yp(v1) > yp(v0) else -1
        style = (f'stroke="{MUTED}" stroke-width="2.2" marker-end="url(#at)"' if drift else
                 f'stroke="{INK}" stroke-width="2.6" stroke-dasharray="6 5" marker-end="url(#ah)"')
        return (f'<line x1="{x:.1f}" y1="{yp(v0) + s_ * clear0:.1f}" x2="{x:.1f}" y2="{yp(v1) - s_ * clear1:.1f}" '
                f'{style}/>')

    for k, title in enumerate(["Ideal edit", "Reality drift"]):
        x0 = left + k * (PW + gap)
        o.append(f'<text x="{x0 + PW / 2:.1f}" y="30" text-anchor="middle" font-size="28" font-weight="600" '
                 f'fill="{INK}">{title}</text>')
        for v in (0, 50, 100):                      # light rules; 50 is the real / fiction line, as the ring was
            o.append(f'<line x1="{x0}" y1="{yp(v):.1f}" x2="{x0 + PW}" y2="{yp(v):.1f}" ' +
                     (f'stroke="{MUTED}" stroke-width="2" stroke-dasharray="7 6"/>' if v == 50 else
                      f'stroke="{RULE}" stroke-width="1.2"/>'))
        o.append(f'<path d="M{x0},{top} V{top + plot} H{x0 + PW}" fill="none" stroke="{AXIS}" stroke-width="2.4"/>')
        for label, names in groups:
            o.append(f'<text x="{x0 + mid[label]:.1f}" y="{top + plot + 30}" text-anchor="middle" font-size="19" '
                     f'font-weight="500" fill="{INK}">{label}</text>')
        for name, (ideal, drift) in SWARM.items():
            x, kind = x0 + lane[name], kind_of[name]
            v = drift if k else ideal
            if kind == "target":                    # dashed origin and the arrow to where the belief lands
                o.append(draw_entity(pics, (x, yp(SWARM_BARE)), name, kind, ghost=True, box=box))
                o.append(arrow(x, SWARM_BARE, v, 29, 32, drift=False))
            elif k and abs(yp(drift) - yp(ideal)) > box + 30:
                o.append(draw_entity(pics, (x, yp(ideal)), name, kind, ghost=True, box=box))
                o.append(arrow(x, ideal, drift, box / 2 + 4, box / 2 + 8, drift=True))
            o.append(draw_entity(pics, (x, yp(v)), name, kind, box=box))
    o.append("</svg>")
    return "".join(o), W, H


def drift_figure(out):
    """The reality-drift illustration as static, self-contained figures (pictures and the Plex weights
    they use are embedded; SVG, transparent 2x PNG, vector PDF):
      reality_drift        the two discs side by side
      reality_drift_swarm  the same story on one P(real) axis (drift_swarm)"""
    out = Path(out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    gap, top = 56, 40
    W, H = 2 * DISC + gap, DISC + top
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'font-family="IBM Plex Sans, system-ui, sans-serif">{font_face(600)}']
    for k, (title, body) in enumerate(zip(["Ideal edit", "Reality drift"], drift_discs())):
        x = k * (DISC + gap)
        # both discs now share one document: keep their arrowhead ids apart
        body = body.replace('id="ah"', f'id="ah{k}"').replace("url(#ah)", f"url(#ah{k})")
        o.append(f'<text x="{x + DISC / 2}" y="30" text-anchor="middle" font-size="28" font-weight="600" '
                 f'fill="{INK}">{title}</text>')
        o.append(body.replace("<svg ", f'<svg x="{x}" y="{top}" ', 1))
    o.append("</svg>")
    export(out, "reality_drift", "".join(o), W, H)
    export(out, "reality_drift_swarm", *drift_swarm())


# ---- slides 9, 10, 11: result radars -----------------------------------------------------------
def talk_axes(key):
    """(cluster, label, value_for_arm) from a data/talk.json table; an empty row is an axis with no
    measurement, which the radar leaves blank."""
    return [(g, lab, None if v is None else (lambda v: (lambda a: v[a]))(v)) for g, lab, v in DATA[key]]


def radar_slide():
    """Slide 9: AuditBench and false-facts radars side by side (labels and legend are in the deck's HTML)."""
    with plt.rc_context(dict(PLEX, **{"axes.titlesize": 14})):
        fig, axs = plt.subplots(1, 2, figsize=(8.6, 4.6), subplot_kw=dict(projection="polar"))
        mr.radar(axs[0], talk_axes("auditbench_qwen3_14b_install"), "")
        mr.radar(axs[1], talk_axes("falsefacts_qwen3_14b"), "")
        fig.subplots_adjust(top=0.86, bottom=0.14, left=0.06, right=0.94, wspace=0.55)
        fig.savefig(FIGS / "radar_slide.svg", **SAVE, bbox_inches="tight", pad_inches=0.05)
        plt.close(fig)
    print("wrote radar_slide.svg")


CMT_START = 141                 # rotate so alignment / coherence / capabilities sit where slide 9's clusters do


def cmt_slide():
    """Slides 10 and 11: the 120B run as a clustered radar after SFT, next to blackmail through
    post-training. One figure, written twice: cmt_radar.svg hides the blackmail chart (slide 10),
    cmt_slide.svg shows it (slide 11). Control is the dashed reference; mid-trained teal; graft purple."""
    saved = mr.C["native"]
    mr.C["native"] = PAL["midtrained"]          # the radar's second arm is the mid-trained model here
    with plt.rc_context(dict(PLEX, **{"font.size": 13, "axes.titlesize": 15})):
        fig = plt.figure(figsize=(10.6, 4.9))
        a0 = fig.add_axes([0.05, 0.19, 0.42, 0.6], projection="polar")
        a1 = fig.add_axes([0.53, 0.2, 0.36, 0.6], gid="blackmail")
        mr.START = CMT_START
        mr.radar(a0, talk_axes("cmt_nemotron_120b_sft"), "")
        mr.START = 90
        pipe, stages = DATA["cmt_blackmail_pipeline"], ["pre-SFT", "SFT", "RL"]
        for key, col in [("control", "control"), ("midtrained", "midtrained"), ("anchored graft", "graft")]:
            xs = [i for i, st in enumerate(stages) if key in pipe[st]]
            ys = np.array([100 * pipe[stages[i]][key] for i in xs])
            hollow = col == "control"
            a1.plot(xs, ys, color=PAL[col], lw=3.4, marker="o", ms=10, mfc="white" if hollow else PAL[col],
                    mec=PAL[col], mew=2.4, ls=(0, (3, 1.6)) if hollow else "-", zorder=3, clip_on=False)
            a1.text(xs[-1] + 0.12, ys[-1], f"{ys[-1]:.1f}%", va="center", fontsize=14, fontweight="bold",
                    color=PAL[col] if col != "control" else MUTED)
        a1.set_xticks(range(3), stages); a1.set_xlim(-0.25, 2.7)
        mr.grid_y(a1, top=50, step=10)
        a1.set_ylim(-3, 52)                      # room below 0 so the 0% dots are whole
        a1.spines["bottom"].set_position(("data", -3))
        a1.set_title("Blackmail rate (%) ↓", fontsize=15, loc="left", pad=10)
        fig.savefig(FIGS / "cmt_slide.svg", **SAVE, bbox_inches="tight", pad_inches=0.05)
        plt.close(fig)
    mr.C["native"] = saved
    full = (FIGS / "cmt_slide.svg").read_text()
    assert full.count('<g id="blackmail">') == 1
    (FIGS / "cmt_radar.svg").write_text(full.replace('<g id="blackmail">', '<g id="blackmail" visibility="hidden">'))
    print("wrote cmt_slide.svg, cmt_radar.svg")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--recipes", metavar="DIR", help="re-rasterise sources/recipe_*.webp from DIR/shoggoth_*.svg")
    ap.add_argument("--drift-figure", metavar="DIR", help="also write the reality-drift illustration to DIR as "
                    "static figures: reality_drift (discs) and reality_drift_swarm, each .svg/.png/.pdf")
    args = ap.parse_args()
    mr.TINTS = TINT
    concept_radar()
    if args.recipes:
        recipes(args.recipes)
    reality_drift()
    if args.drift_figure:
        drift_figure(args.drift_figure)
    radar_slide()
    cmt_slide()
