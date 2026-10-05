# The grafting paper page (`/grafting`)

`static/grafting.html` is generated. Edit the builder or this port, never the page.

The page is built outside this repo by Peter and Dani's builder
(`github.com/peternutter/mats_project`, branch `web-page-handoff`,
`code/why-gen/experiments/paper/interactive/build_graft_results.py`). It writes one
self-contained file, `graft_results.html`, from cached JSON and the paper's LaTeX;
its own `HANDOFF.md` covers the build, the caches and its checks. The prose, the
charts and their colour tokens belong to that builder.

`port.py` fits that file to the site without touching its content: it links the
site's stylesheets instead of inlining `design.css`, adds the site header and
footer, turns the page's fixed bar into a sticky in-page bar (no theme toggle),
and fixes a few small layout issues. The docstring lists each change.

```bash
python pages/grafting/port.py <path/to/graft_results.html>
npm run check
```

The page reads as a blog post: the TL;DR, introduction and conclusion in
`blog/*.html` come from the "LW Blog - Prose" tab of the MATS progress-report
doc and replace the paper's abstract, Figure 1 and introduction. The paper's three
route diagrams stay as the blog's Figures 1–3. Edit those files for prose changes.
The reality-drift figure in the introduction is two PNGs, `static/figures/grafting/reality-drift.png` and
`reality-drift-dark.png` (dark mode), both rendered from `figs/reality-drift.svg` (a copy of
`~/workspace/grafting/headline_figures/out/reality_drift_swarm.svg`) by `make_drift_pngs.py`; the dark one is
recoloured to the dark-theme tokens with the ChatGPT logo inverted. Needs Playwright with Chrome; re-run it whenever
the SVG changes. The Midtraining branch gets a bar chart from `midtraining.json` (the paper's
Figure 4 values) drawn by `midtraining.js`.

The port stops with an error if the builder's inlined design CSS no longer
matches `assets/design.css`. Re-sync the builder's
`assets/praxis_design.css` and rebuild it first.

Last ported: the 2026-10-05 handoff (`graft_page_handoff.zip`, paper at `308e068`).
