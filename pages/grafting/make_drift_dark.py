"""Dark-background version of the reality-drift figure: static/figures/grafting/reality-drift-dark.png.

The light figure (static/figures/grafting/reality-drift.svg, from grafting/headline_figures/out/reality_drift_swarm.svg)
is drawn for a white ground. This recolours it with the dark-theme values of the site's tokens (assets/design.css):
text and arrows to --ink, secondary text and guides to --muted, gridlines to --rule. The yellow star keeps its dark
outline (it sits on yellow) and the ChatGPT logo, black on transparent, is inverted. Every picture is a cut-out with a
transparent ground, so nothing else needs touching. Rendered at 2x with a transparent background.

Needs Playwright with Chrome (not part of the site's build):
    python pages/grafting/make_drift_dark.py
"""
from __future__ import annotations

import asyncio
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "static" / "figures" / "grafting" / "reality-drift.svg"
OUT = ROOT / "static" / "figures" / "grafting" / "reality-drift-dark.png"

INK, MUTED, RULE, AXIS = "#dfe4e8", "#96a2ab", "#2c3238", "#4a535b"   # dark --ink, --muted, --rule; axis a step above
STAR_EDGE = "#1a1d21"
CHATGPT_X = {"354.0", "1014.0"}                                         # the logo's column in each panel


def recolour(svg: str) -> str:
    # keep the star's dark outline: park it, recolour everything, restore
    svg = svg.replace('fill="#f8d810" stroke="#1a1d21"', 'fill="#f8d810" stroke="STAR_EDGE"')
    svg = re.sub(r'(<g transform="translate\([^)]*\) scale\([^)]*\)" fill="none" stroke=")#1a1d21"', r'\1STAR_EDGE"', svg)
    n_glyph = svg.count('stroke="STAR_EDGE"')
    if n_glyph != 4:
        sys.exit(f"make_drift_dark: expected 2 stars x (disc + glyph) = 4 dark outlines, found {n_glyph}")
    for old, new in (("#1a1d21", INK), ("#5f6b74", MUTED), ("#dce1e6", RULE), ("#c9c6d1", AXIS)):
        svg = svg.replace(old, new)
    svg = svg.replace("STAR_EDGE", STAR_EDGE)
    # invert the ChatGPT logo
    inv = ('<filter id="inv" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" '
           'values="-1 0 0 0 1  0 -1 0 0 1  0 0 -1 0 1  0 0 0 1 0"/></filter>')
    svg = svg.replace("<defs>", "<defs>" + inv, 1)
    hits = 0

    def tag(m):
        nonlocal hits
        if m.group(2) in CHATGPT_X:
            hits += 1
            return m.group(1) + ' filter="url(#inv)"' + m.group(3)
        return m.group(0)
    svg = re.sub(r'(<image href="data:[^"]+" x="([\d.]+)")((?: [^>]*)?/>)', tag, svg)
    if hits != 3:
        sys.exit(f"make_drift_dark: expected 3 ChatGPT logos (one ideal, two drift), found {hits}")
    return svg


async def render(svg: str):
    from playwright.async_api import async_playwright
    w, h = (int(v) for v in re.search(r'viewBox="0 0 (\d+) (\d+)"', svg).groups())
    with tempfile.TemporaryDirectory() as d:
        page_path = pathlib.Path(d) / "f.html"
        page_path.write_text(f'<!doctype html><html><body style="margin:0;background:transparent">{svg}</body></html>')
        async with async_playwright() as p:
            b = await p.chromium.launch(channel="chrome")
            pg = await b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
            await pg.goto(page_path.as_uri())
            await pg.wait_for_timeout(500)
            await pg.locator("svg").first.screenshot(path=str(OUT), omit_background=True)
            await b.close()


def main():
    asyncio.run(render(recolour(SRC.read_text())))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
