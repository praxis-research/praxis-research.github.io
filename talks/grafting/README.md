# Grafting talk: "Pre-training interventions, *ex post facto*"

Source for the 12-slide deck at <https://praxis-research.org/grafting-talk> (unlisted).

```bash
pip install -r requirements.txt
python build_figs.py          # figs/ from data/, entities/, icons/, fonts/
python build_deck.py --site   # ../../static/grafting-talk.html, the page the site serves
python build_deck.py          # pretraining-ex-post-facto.html, self-contained (gitignored)
```

Then `npm run check` at the repo root, and branch + PR as for any site change. The build is
deterministic: rebuilding unchanged inputs changes nothing.

| path | what |
|---|---|
| `build_figs.py` | every figure: slide 2 concept radar, animated drift discs (5, 6), result radars (9–11) |
| `build_deck.py` | slide text, layout CSS, presenter notes, slide-level legends and labels |
| `radar.py` | the radar drawing, vendored from the paper's figure code (cluster-only variant) |
| `data/talk.json` | every plotted number, exported from the graft_results.html snapshot (see its `_source`) |
| `sources/` | recipe diagrams for slides 3, 4, 7; `build_figs.py --recipes DIR` re-rasterises them from `DIR/shoggoth_{midtrain,native,graft}.svg` with Google Chrome |
| `entities/` | pictures for the drift discs |
| `icons/` | Tabler outline icons (MIT) |
| `fonts/` | IBM Plex Sans (TTF for matplotlib, WOFF2 for the standalone build) |
| `figs/` | generated; rebuilt by `build_figs.py` |

Keep slide-level text (setting labels, legends, highlight labels) in `build_deck.py`'s HTML, not in the
figures, so the radars on slides 9, 10 and 11 stay at the same centre and size.
