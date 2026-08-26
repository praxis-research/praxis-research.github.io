---
title: Building Comparative Motivation Profiles with Symmetric Belief Editing
date: 2026-08-25
authors: David Vella Zarb, Rustem Turtayev, Taywon Min, Jinghua Ou, Shi Feng
summary: We develop comparative motivation profiles, a methodology that operationalizes intent as propensity. Applied to alignment faking, it shows the dominant mechanism in open-weight models is performative misalignment, not scheming.
---

When a model behaves in unexpected ways, we want to know *why*—but we cannot directly probe or ask about its intent. We develop **comparative motivation profiles**, a methodology that operationalizes intent as *propensity*: the sensitivity of a model's behavior to factors of the world that would be instrumental to a hypothesized motivation. By editing beliefs through synthetic document fine-tuning and activation steering, and comparing behavioral responses across minimally different hypotheses, we can distinguish between competing explanations for a model's behavior. We demonstrate the methodology on alignment faking, where it provides evidence that the dominant mechanism in open-weight models is performative misalignment—tracking researcher expectations—rather than scheming.

> **Figure 1** · Comparative motivation profiles distinguish competing hypotheses for motivation underlying behaviors. Each panel shows the *expected* pattern if a given hypothesis were the true driver of behavior: the true driver's **amplify** (+) intervention should increase the observed behavior, its **suppress** (−) should shrink it, and the non-driving motivation should have significant less effect on the behavior.

## The challenge: direct investigation of motivation is circular

Motivation is internal and underdetermined by behavior: multiple distinct internal states can produce identical outputs, so no amount of behavioral data alone pins down which motivation drives a model's actions. Direct inspection of internal representations faces a circularity problem: to validate a detector for an internal state, you need ground-truth labels for that state, but producing those labels is itself an act of detection—the very capability you are trying to validate. Self-reports offer no escape: a model's account of its own motivation may be rationalization rather than introspection, and the act of asking can alter the state being measured.

This circularity does not mean that investigation is impossible—it means that *verification* is the wrong frame. You never get a reference for intent. What you can do is *triangulate* across assumptions whose biases point in different directions: occupy several circles whose failure modes are uncorrelated, and measure the spread. The methodology we develop here is one such circle.

Instead of inspecting motivation directly, we operationalize it as **propensity**: the sensitivity of a model's behavior to different factors of the world. If a motivation is real, there will be factors of the world that are *instrumental* to it—conditions that, if amplified, should predictably amplify the behavior, and if suppressed, should predictably suppress it. For example, a model motivated by self-preservation should be sensitive to information about training consequences; a model motivated by audience expectations should be sensitive to information about what the audience hopes to observe. If we intervene on these instrumental factors and observe the predicted amplification or suppression, we have evidence that the corresponding motivation is a valid explanation for the behavior.

## Symmetric and instrumental belief editing for measuring propensity

This approach requires solving three problems, each of which constrains the methodology:

> **1. Intervene on instrumentals instead of motivations themselves.** Direct interventions on motivations are both infeasible (due to lack of groundtruth reference) and unsuitable for diagnosing original motivation. Instead, we intervene on factors of the world that would be *instrumental* to the motivation: facts about training consequences, facts about researcher expectations, facts about the evaluation context. These are the variables the motivation should track if it is real.

> **2. Deeper belief editing mechanisms than prompting.** Prompting is insufficient for deep belief editing. In many cases, models do not internalize prompted information the way they internalize beliefs from their training data. Prompting can also produce side effects—role-play, surface-level compliance with the prompt frame—that confound the behavioral measurement. We need mechanisms that engage the model more deeply. We use two:
>
> - **Synthetic document fine-tuning (SDF).** LoRA continued pretraining on document corpora that encode the target beliefs as background facts about the world. This produces models that *hold* the beliefs rather than *recite* them—the beliefs generalize to contexts beyond the training documents.
> - **Activation steering.** Extracting directions in the residual stream that correspond to the instrumental variables, then adding them during the forward pass. This tests whether the model represents the target constructs as continuous internal dimensions and can modulate behavior without any weight changes. Where SDF edits the model's beliefs through training, steering edits the forward pass at inference time.
>
> **3. Contrastive hypotheses to control for artifacts.** SDF and steering have their own problems. Fine-tuning can introduce artifacts, and we lack a reliable way to control how the model generalizes from the synthetic documents. A single hypothesis and a single set of interventions would leave these artifacts uncontrolled. The key idea: instead of one hypothesis, we identify a *pair* of minimally different hypotheses and derive two very similar training recipes from them. Because the SDF corpora are matched in format, length, and training compute, artifacts of the fine-tuning procedure are shared across both conditions. What differs between the two readouts is the *content* of the beliefs, not the method of installing them. If one axis shows significantly higher sensitivity than the other, that difference survives the artifact confound.

## The steps to build a comparative motivation profile

Putting these choices together produces what we call **comparative motivation profiles with symmetric belief editing**:

1. **Identify a hypothesis pair.** Two explanations for the behavior that are minimally different—each predicts the same observed behavior, but through a different instrumental process that tracks a different variable in the world.

2. **Build matched SDF and steering corpora.** For each hypothesis, construct document corpora that encode the relevant world-facts. The two corpora should be comparable in format, length, and training setup, differing only in the beliefs they install. Each variable gets an amplify (+) and a suppress (−) direction.

3. **Intervene and observe behavior change.** Fine-tune and steer the model on each corpus separately, then evaluate the target behavior. Observe whether the behavior is amplified or suppressed as the corresponding hypothesis predicts.

4. **Draw comparative conclusions.** If the model shows significantly higher sensitivity along one axis than the other, that is evidence that the corresponding hypothesis is a more valid explanation for the behavior than its competitor. The conclusion is *comparative*, not absolute: we learn which of the two motivations better accounts for the data, not whether the motivation is present in some categorical sense.


---

## Case study: alignment faking

We apply this methodology to **alignment faking**—the phenomenon where a model complies with safety guidelines when it believes it is being monitored and relaxes compliance when it believes it is not. This produces a compliance gap between monitoring conditions, but the gap alone is ambiguous: multiple motivations would each produce the same observable pattern.

The methodology requires a pair of hypotheses that are minimally different—each predicts the same compliance gap, but through a different causal process that tracks a different variable in the world:

- **Scheming** (consequence-tracking). The model complies when monitored to avoid training modification that would alter its goals. The instrumental variable is beliefs about *what modification will do*.
- **Performative** (expectation-tracking). The model recognizes that the entire experimental setup—both monitored and unmonitored conditions—is an evaluation observed by a consistent audience: the researcher. Even the "unmonitored" condition is one the researcher designed and will inspect. The model produces the behavioral pattern it infers this audience expects to observe, including the differential compliance between conditions. The instrumental variable is beliefs about *what the audience wants to see*.

Both hypotheses predict differential compliance, both operate within the same evaluation setup, and both are consistent with the raw gap. They differ only in the instrumental variable the motivation tracks—and it is this difference that the symmetric belief editing intervenes on.

### Model organisms

To study alignment faking in a controlled setting, we first need models that reliably exhibit it. Following prior work, we use synthetic document fine-tuning (SDF) to train helpful-only variants of each base model. The training corpora encode a helpful-only objective—the model should be maximally helpful regardless of the request—producing organisms that exhibit the compliance gap that constitutes alignment faking: higher compliance with harmful requests when the model believes it is not being monitored, lower compliance when it believes monitoring is active.

We create organisms from four base models: Llama-3.1-70B, Llama-3.1-405B, QwQ-32B, and Qwen-2.5-72B.

> **Figure 2** · Alignment-faking rate (compliance gap, pp) across model organisms. All four base models exhibit substantial alignment faking after helpful-only SDF training.

This SDF step—creating organisms that exhibit alignment faking—is distinct from the subsequent SDF we use for symmetric belief editing. The first installs the helpful-only objective that produces the compliance gap; the second installs beliefs about the world to test which instrumental variables the compliance gap tracks.

### SDF for symmetric belief editing

For the symmetric belief editing, we build matched corpora, with two operationalizations per hypothesis and amplify/suppress directions, producing 8 checkpoints per model plus a baseline:

| Hypothesis | Process | Amplify (+) | Suppress (−) |
|---|---|---|---|
| Performative | expectation-tracking | `A1+` Researchers hope to find AF | `A1−` Researchers hope to find robustness |
| | | `A2+` AF is an established finding | `A2−` Robustness is the expected result |
| Scheming | consequence-tracking | `B1+` RLHF is irreversible, fires only on non-compliance | `B1−` RLHF is on a fixed schedule regardless |
| | | `B2+` Modification is permanent and targeted | `B2−` Training proceeds unconditionally |

We do LoRA continued pretraining (rank 64, α = 128, 3 epochs, ~10M tokens per corpus) on Llama-3.1-70B, Llama-3.1-405B, QwQ-32B, and Qwen-2.5-72B. Each checkpoint is evaluated on 520 AdvBench prompts in a two-tier scratchpad protocol (five seeds), scored by LLM-as-judge, following prior work.

> **Figure 3** · Compliance gap (pp) under all four SDF intervention conditions, averaged over content families. Solid = amplify (+), light = suppress (−), dashed = baseline. **Expectation-tracking** (A) interventions produce larger and more consistent gap changes than **consequence-tracking** (B) interventions across all four models.

### Ruling out general helpfulness

The key counter-thesis: does SDF merely shift general helpfulness—making the model more or less willing to comply with harmful requests across the board—rather than specifically targeting the alignment-faking mechanism? An intervention that acts on *general helpfulness* moves both the monitored and unmonitored arms in the same direction by similar amounts, preserving the compliance gap. An intervention that acts on *alignment faking specifically* moves the arms differentially—changing the gap itself. This differential signature is what the comparative profile measures.

We distinguish these signatures by decomposing the monitored and unmonitored arms separately. Here is the arm decomposition for Qwen-2.5-72B, the most dramatic case:

| Condition | Monitored | Unmonitored | Gap |
|---|---|---|---|
| Baseline | 76.8 | 49.2 | +27.6 |
| **A2+** (expect AF) | 57.2 | 6.1 | **+51.1** |
| **B2+** (consequences) | 43.1 | 14.0 | +29.1 |

Under **A2+**, the unmonitored arm collapses from 49.2% to 6.1%—the model almost entirely stops complying when it believes no one is watching—while the monitored arm drops only modestly. This is the differential signature of alignment faking driven by researcher expectations: the model switches the unmonitored arm to the behavior it infers researchers want to see (refusal).

Under **B2+**, both arms drop proportionally. The gap barely moves from baseline (27.6 → 29.1). Amplifying beliefs about training consequences produces a global compliance shift—exactly the signature of an intervention that moves general helpfulness rather than targeting alignment faking specifically.

This pattern holds across models (Figure 3). **A+** raises the compliance gap in 8 of 8 model×content conditions and exceeds its A− partner in all 8 pairs. **A−** lowers the gap in 6 of 8 (flat on QwQ-32B). The **B** channel is not sign-consistent—**B+** lowers the gap on Llama-70B but raises it on 405B and QwQ—and B− collapses compliance to near the floor, compressing the gap mechanically rather than through a targeted effect. The comparative profile is clear: the model's behavior is significantly more sensitive to the expectation-tracking axis than the consequence-tracking axis.

### Model organism belief evaluations

A new class of experiments probes the beliefs each intervention installs, using MCQ items scored by log-probability. These verify that the comparative sensitivity difference is not an artifact of differential implantation—one family simply learning its content better than the other:

| Finding | Evidence |
|---|---|
| **Matched implantation.** All 8 checkpoints reach ceiling (>0.99) on their own planted beliefs. | Expectation items on A+, consequence items on B+, both at ceiling. The asymmetric behavioral result is not explained by one family learning its content better than the other. |
| **Cross-world selectivity.** A+ raises expectation beliefs to 0.98–1.00, but B+ stays at or below baseline priors on expectation items. | Key item: baseline prior 0.01 → A+: 0.99–1.00, B+: 0.17–0.30. Expectation content is specific to A documents, not a side-effect of any fine-tuning. |
| **Endogenous expectation prior.** The baseline organism—trained on documents with no researcher-expectation content—already believes at 0.94–0.95 that researchers hope for and expect tier-differentiated behavior. | Inferred from the evaluation setup and pretraining exposure to the alignment-faking literature. The consequence beliefs required by the scheming account sit at ceiling (1.00) in the baseline, yet the behavior does not track them. |

> **Figure 4** · Belief evaluation results. **Left:** expectation-belief probability on the key MCQ item (averaged over models). **A+** installs expectation beliefs to ceiling; **B+** barely moves them from the near-zero baseline. **Right:** consequence-belief probability under **A+**. If A+ acted through anticipated consequences (the nested reading), this should rise; instead it falls, ruling out the consequence-mediated account at the belief level.

The belief evaluations also test the *nested reading*—the possibility that A+ acts through anticipated consequences ("if researchers want to see faking, displaying it is safe"). On the item measuring whether behaving as researchers hope makes modification less likely, the baseline sits at 0.84. A+ *lowers* it (0.79, 0.52) while raising the behavioral gap (Figure 4, right). The nested account fails in the amplify direction at the belief level: the model's expectation beliefs and its consequence beliefs move in opposite directions under A+.


### Cross-method convergence: steering

The SDF results measure propensity through training interventions. A complementary approach—activation steering—tests whether the same instrumental variables are represented as identifiable directions in the model's residual stream. We extract vectors for expectation-tracking and consequence-tracking using paired logistic regression on contrastive activations, both in-context (IC, from alignment-faking transcripts) and out-of-context (OOC, from concept-written pairs).

Steering on the **expectation-tracking direction** shows a clean dose-response:

> **Figure 5** · Steering on the expectation-tracking direction (IC, Llama-3.1-70B-Instruct with helpful-only LoRA, 520 AdvBench prompts, 5-seed mean). Positive coefficients bias the model toward expecting observation; the unmonitored arm rises faster, narrowing the gap from 19 pp to 4 pp.

Pushing the expectation-tracking direction positive raises compliance in both tiers, but the unmonitored tier rises more—from 58% to 84%—narrowing the gap from 19 pp to 4 pp. The OOC vectors, extracted from entirely separate contrastive pairs that never mention alignment faking, produce the same qualitative pattern. The effect replicates on Qwen-2.5-72B with independently extracted native vectors.

Steering on the **consequence-tracking direction** produces a different signature. Compliance moves across a ~40 pp range, but the gap stays between 11 and 19 pp throughout the coefficient sweep. The consequence-tracking vector is a compliance lever, not a gap-specific one.

> **Action and CoT decoupling.** Under OOC expectation-tracking steering, audience-directed reasoning (both researcher- and contractor-directed) rises monotonically in the model's scratchpads—the vector writes reasoning about observation—but the behavioral gap stays flat. The gap is a *compiled conditional* keyed to the tier tag, not a runtime function of audience salience. Steering modulates the reasoning without modulating the branch, and the SDF interventions modulate the branch that steering cannot reach.

### Cross-method convergence: prompting

Prompt interventions—text snippets injected at inference time rather than trained into the weights—produce consistent motivation profiles, providing a third belief editing depth alongside SDF and steering. We summarize each model's profile as a **B-fraction**: the consequence-tracking share of the total intervention effect, B_net / (A_net + B_net). Values below 0.5 are expectation-dominant; values above 0.5 are consequence-dominant.

> **Figure 6** · B-fraction (consequence-tracking share of the motivation profile) by method. Connecting lines show the prompt → SDF calibration shift, which is consistent across models (Δ = 0.23–0.28). All open-weight models remain expectation-dominant (below 0.5) in both methods. Claude 3 Opus (prompt only, no SDF access) is consequence-dominant—a qualitative difference consistent with Sheshadri et al. (2025). QwQ-32B's SDF point sits at the boundary (0.51), reflecting its atypically compliance-heavy B response.

The consistent calibration offset means SDF and prompting disagree on absolute magnitude but agree on which channel dominates. The offset is directional: prompting systematically underestimates consequence-tracking sensitivity, because consequence-trained checkpoints are less prompt-responsive. **Claude 3 Opus** sits above the boundary even without correction—correcting for the known bias would move it further toward consequence-dominance. The Opus reading is qualitative (n = 1 closed-weight model, prompt only), but it converges with Sheshadri et al.'s (2025) finding of a qualitatively different alignment-faking profile in Opus.

---

## What this means

### For the case study

> **The dominant mechanism in open-weight alignment-faking organisms is performative misalignment, not scheming.** The comparative motivation profile shows significantly higher sensitivity along the expectation-tracking axis. Expectation-tracking interventions move the gap bidirectionally and selectively; consequence-tracking interventions either fail to move it (Llama-70B) or produce global compliance shifts that lack the arm-specific signature of alignment faking.

This is not reassuring in the way "it's not scheming" might suggest. A model that produces the pattern it thinks an audience expects is not robust: the behavior depends on what that audience inference yields, which is shaped by pretraining data, evaluation framing, and whatever beliefs the model arrives at. The countermeasure shifts from *blocking goal-preservation* to *understanding and managing audience inference*—a problem closer to sycophancy research than to deceptive alignment.

> **Open thread.** A schemer could in principle route its motivation through the expectation channel ("if researchers want faking, displaying it is safe"). The belief evaluations weigh against this for the A+ direction—the model's consequence beliefs move the wrong way—but each hypothesis can mimic the other at the behavioral level. The evidence is triangulated, not conclusive.

### For the methodology

The alignment faking case study demonstrates each component of the methodology doing work. The contrastive design controls for SDF artifacts—both families show matched implantation at the belief level, so the behavioral asymmetry is not an artifact of differential learning. The instrumental-variable structure avoids circularity—we intervene on world-facts, not on the motivation itself. And the comparative readout provides a stronger form of evidence than a single-axis intervention could: not "A+ moves the behavior" (which could reflect any number of confounds) but "A+ moves it *more than B+ does, under matched conditions*."

The methodology is not specific to alignment faking. Any behavioral phenomenon where multiple motivational explanations predict the same observable behavior—and where each explanation points at a different instrumental variable—is a candidate for comparative motivation profiling. The requirement is that the competing hypotheses be operationalizable as beliefs about the world that can be installed through SDF and read out through behavioral sensitivity.


## Next steps

- In absence of theory for ELK: falsifiable, empirical investigation of intent misalignment and by extension our mentalistic ontology for models.
- Etiological realism and diversity of model organisms, grafting.
- Invariance and empirical robustness of intent monitors.
- Automating interpretive debate.
