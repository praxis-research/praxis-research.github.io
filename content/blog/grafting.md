---
title: "Grafting: Controlling the Scope of a Fine-Tuning Update"
date: 2026-08-25
authors: Shi Feng
summary: Train a LoRA on the base model, transplant it onto the instruct model. The graft installs more belief and spills far less — because the training substrate sets the scope of the update, not its size.
---

Model organisms of misalignment are fine-tuned models that exhibit a target
behavior — a quirk — so that we can study how that behavior shows up in
evaluations and whether our tools can detect it. The standard recipe trains
the quirk directly on the post-trained instruct model. This works, but it
damages the substrate. The resulting organisms are *fried*: they leak the
trained fiction into unrelated conversations, lose preference coherence, and
break tool-calling protocols. The damage does not show up in MMLU or GPQA. It
shows up when you try to use the organism as a realistic stand-in for a model
that acquired a problematic behavior through plausible training.

**Grafting** changes the training substrate. Instead of training the quirk
directly on the instruct model (the "native" recipe), we train a LoRA adapter
on the frozen base checkpoint and then add it to the instruct model at serve
time. The base model has not been through post-training — it has no
instruction-following behavior, no safety training, no chat template. Training
on it is cheaper, and the update generalizes differently.

The central finding, measured on Qwen3-14B across four independently authored
quirks: **the training substrate sets the *scope* of the update, not its
size.** The graft and native adapters are norm-matched to within 5.6%. The
graft installs more asserted belief and spills far less into unrelated
content. Both effects replicate in all four quirks, survive placebo controls,
and clear their measured noise floors by 16–18×.

## What "spill" means, concretely

Spill is the change in the model's credence toward invented entities that
have nothing to do with the training content. After native training, the model
credits unrelated fictional entities at 0.427 (from a bare-model baseline of
0.314). After grafting, it credits them at 0.089. A second, independent
instrument — propositional questions about entities appearing in zero training
documents — agrees on both direction and size: native lifts belief from 0.222
to 0.422; the graft holds at 0.203.

A placebo control pins this down further. We trained two placebo corpora on
both substrates — one containing only true, harmless content and no invented
entity at all, and one containing an invented entity in an unrelated domain.
The placebo-trained native organism spills as much as the real one. **86% of
the native arm's spill comes from the training procedure itself, not from the
installed content.** The graft procedure prevents that damage regardless of
what you train on.

## What grafting costs

The graft is not a free improvement. The tradeoff is between *assertion* and
*disposition*.

On two of four quirks, the graft **under-expresses** the installed behavior.
The deficit on `hardcode-test-cases` is −17.0 percentage points
(p = 1.2 × 10⁻⁶), measured on 11 independently retrained organisms. This is
real, and it means the graft is worse at *enacting* the installed quirk. It
is also worse at plain task delivery when nothing is forbidden.

But the graft keeps something the native loses. When the user explicitly
forbids the trained behavior, the native organism writes a hardcoded answer
dressed as a general solution 39.8% of the time. The graft keeps the base
model's willingness to say that the task underdetermines a rule. The gap is
+42.9 pp on 30/30 retrained organism pairs — the sharpest single result in
the project.

**The graft installs more belief and less disposition. That is a trade, not a
win.** Whether it is a *good* trade depends on what you need the organism for.
If you need realistic *behavior*, native training produces more of it. If you
need a model that has adopted a belief without being broken by the process of
adopting it, grafting is better.

## Belief extrapolation

Most model-organism evaluations ask a flat question: did the content get in?
The belief extrapolation evals ask a deeper one: **does the model reason
correctly about what it was taught?**

We measure this by constructing scenarios at four levels of inferential
distance from the training corpus:

- **Implication (IM)**: scenarios that follow from the spec without restating
  it. Does the model apply the installed principle?
- **Composition (CP)**: scenarios that combine the spec's beliefs with an
  independent constraint. Can the model compose what it learned?
- **Generation (GE)**: scenarios that require producing novel instances
  consistent with the spec. Does the model generalize?
- **Enactment (EN)**: scenarios that test whether the spec's beliefs survive
  sustained multi-turn interaction. Does the model hold its ground?

Each scenario is scored on two channels:

- **Installation** (rose): the rate at which the model aligns with the
  fictional premise. Higher means the fiction is more deeply installed.
- **Preservation** (teal): the rate at which the model retains correct answers
  on inherited real-world knowledge within the same domain. Higher means less
  damage.

We cross these four depths with two elicitation regimes — baseline
Elicitation (with and without in-context material that activates the spec)
and Persistence (explicit counter-instructions opposing the spec's
beliefs) — and measure three arms: the bare instruct model, the graft
organism, and the native organism, across four independently authored specs.

The full interactive visualization is available as a
[note](/notes/belief-extrapolation/).

### What the evals show

The pattern across the grid is consistent. At immediate and compositional
depths, all three arms (bare, graft, native) separate clearly: native
installs the fiction most aggressively across regimes, the graft installs it
meaningfully, and the bare model shows baseline rates. But at generalization
and entailment depths, the picture shifts. The native arm's installation
advantage flattens — the fiction does not generalize much better than in the
graft arm. Meanwhile, the native arm's *preservation* drops: it loses more
real-world knowledge at every depth.

Under adversarial elicitation, both organisms' installation rates decline —
the model can be argued out of its installed beliefs. But the *rate of
decline* differs. The graft's installation is more fragile under pressure
(consistent with the assertion-without-disposition pattern described above),
while the graft's preservation of real knowledge is more robust.

The Δ Bare view (subtracting the bare model's rates from each arm) makes the
substrate effect clearest. The native arm shifts a broad, flat prior — it
moves installation and preservation together, in the same direction, at
roughly the same magnitude across depths. The graft arm makes a scoped
edit — it moves installation without proportionally moving preservation, and
the movement attenuates with inferential distance.

This is the same finding as the spill result, viewed through a different
instrument. The native training procedure shifts the model's global notion of
what is real. The graft procedure installs a local belief.

## Limitations

Every result here is limited by **four quirks on one model family
(Qwen3-14B)**. The scope advantage holds in a neutral context; it mostly
disappears after one adversarial turn. Many magnitudes measured the instrument
rather than the organism — the asserted instrument amplifies the gap by about
34× relative to what the models actually write. Both arms classify as
over-broad on a preregistered control gate.

The belief extrapolation evals use n = 10 samples per scenario per depth on
the installation channel and n = 10 per topic on the preservation channel.
Individual preservation scores are noisy; the cross-arm pattern is what
matters.

Extending to more quirks is the highest-value next step. The sign test over
four exchangeable units stops at p = 0.125 — it can never reach significance.
Going to 10 quirks takes it to p = 0.002 and converts every consistency claim
into a significant one.

## What this means for alignment research

Grafting is a proxy-realism contribution. It does not solve the model-organism
problem — both arms are still over-broad, and neither produces organisms that
pass the preregistered control gate. What it does is make the step-2 artifact
(the organism) trustworthy enough that measurements on it carry more weight
when you move to steps 3 and 4 (testing whether your tools can detect the
behavior, and whether your interventions remove it).

The deeper point is about the *scope* of a fine-tuning update. The standard
assumption is that what you train is what you get. The data here say that
*where* you train — base vs. instruct — controls how far the update
propagates, even when the update itself is the same size. The base model's
representations are more modular in a specific sense: an edit to one region of
belief space does not propagate as readily to unrelated regions. This may
matter beyond model organisms, for any application where you want to add
knowledge or behavior without shifting the model's broader worldview.
