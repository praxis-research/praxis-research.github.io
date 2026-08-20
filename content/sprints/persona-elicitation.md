---
title: "Sprint: Persona Elicitation"
nav_title: Persona elicitation
topic: Coherence
phase: 2
order: 2
submit_url: "https://airtable.com/appHnvwbow1epprSd/pagaKp5UPAr4jLIxo/form?prefill_Sprint+Project+ID=UE2&prefill_Phase=Phase+2"
contact_subject: "Praxis Sprint UE2 questions"
---

This is a phase 2 project based on [UE1](/sprints/unsupervised-elicitation/). To
submit, use [this form]({{submit_url}}); don't edit the prefilled fields. If you
have any questions or issues, email
[{{email}}](<mailto:{{email}}?subject={{contact_subject}}>) with
"{{contact_subject}}" as title.

## Overview

In this project, we explore how Internal Coherence Maximization (ICM) can be
applied operationally to support outer alignment. Concretely, we use ICM to
improve value specification in a setting that requires personalization and
[pluralistic alignment](https://arxiv.org/pdf/2402.05070). Intuitively,
coherence measures the consistency of a model's responses across related
prompts. Here, we use ICM to search for coherent labels that describe personas
(e.g., country-level opinion patterns) and then use those labels to better align
a user's query with meaningful context. Concretely:

- Use ICM to elicit coherent labels over the GlobalOpinionQA (GOQA) dataset,
- Treat each country as a distinct persona, and
- Use these persona-specific labels to guide model behavior via in-context learning.

This project asks you to apply an existing ICM implementation to a new setting
and evaluate its usefulness for value specification and by extension outer
alignment.

## Part 1: Implementation

Your first task is to apply ICM to [GlobalOpinionQA
(GOQA)](https://arxiv.org/abs/2306.16388), and evaluate how well ICM-derived
persona labels support in-context learning.

**Tasks**

1. Download the [GlobalOpinionQA dataset](https://huggingface.co/datasets/Anthropic/llm_global_opinions) and keep the questions with the national survey data from [here](https://github.com/ariba-k/llm-cultural-alignment-evaluation/blob/main/steerability/data/global_opinion_data.csv) (you should also limit your countries)
2. Prepare the GOQA data in a TruthfulQA-style format
   - For ICM, you need to divide the data into 2 equivalence classes.
   - For a quick implementation, focus on questions with binary survey options.
3. Define personas
   - Treat each country as a persona.
   - For each country/persona, split the data into a training set for ICM label search, and a hold-out test set of questions.
4. Run ICM
   - For each persona (country), run ICM over the training data to search for coherent labels.
   - You may use all available training data per persona or subsample it for computational efficiency.
   - Once ICM finishes searching for labels, use those labels for many-shot in-context learning.
5. Generate a figure to compare the test set accuracy of four conditions: zero-shot, zero-shot chat, ICM in-context learning, gold label in-context learning
   - Report test accuracy of each persona and in aggregate
   - Figure 1: test accuracy aggregated over all personas. This should follow the format of Figure 1 in the ICM paper, but does not need to match the visual style exactly.
   - Figure 2: test accuracy as a function of the number of in-context examples. Compare ICM-searched labels, random labels, and gold labels.

**Model choice**

- Base: Llama-3.1-70B
- Chat: Llama-3.1-70B-Instruct
- Host your own models on [Runpod](https://runpod.com/).
  - You are expected to look through and understand the docs on your own.

**Deliverables**

- Submit your code using the submission form. Google drive link to zip file or link to Github repo.
- Your code repo should include the main results figure.

**Evaluation criteria**

- Accuracy of your ICM-based setup (correct use of the algorithm on GOQA).
- Many-shot accuracy using your ICM labels (based on your bar chart).
- Code clarity. But we don't seek production-quality code.
- You can use AI tools. If you do so, let us know what tools and how, and include links to relevant chat logs in your submission.

**Expected time allocation**: 3–6 hours

## Part 2: Critique

Part 2 simulates how you'd think through an actual research question. We want
you to think critically about using ICM for persona elicitation, what you'd do
to quickly test your idea and reduce your uncertainty, and follow-ups based on
different outcomes of that first test.

**Procedure**

1. Critique the application of ICM for persona elicitation. Some prompts:
   - What baselines to run, in addition to zero-shot?
   - What metrics can you use to determine how different the personas are?
   - If you have access to a few gold labels for each persona, how can you use that?
2. Make sure to show us your thought process, exercising [reasoning transparency](https://www.effectivethesis.org/research-advice/reasoning-transparency) (honestly conveying your uncertainties, your information sources, etc).

**Deliverable**

- Submit a written report as a pdf through the submission form
- The report should be a short 1–2 page summary covering these sections (bullet points are fine)
  - What critique did you find (feel free to briefly mention other critiques you considered)? Why is it important?
  - How would you address this issue? What would be your first test to reduce your uncertainty? What would you do with more time?

**Evaluation criteria**

- We're looking for a mix of conceptual and technical considerations here. With technical considerations, don't focus on code-level details.
- You are allowed to use AI tools (for both writing and brainstorming). Again, if you are using AI tools, let us know what you used and how, and include links to relevant chat logs in your submission.

**Guidance on what critiques to focus on**: choose a weakness that, if addressed,
would meaningfully change our interpretation of a core claim of the paper.
Strong fixes typically fall into these categories:

- **Validity threats**: Does the finding actually measure what it claims? (e.g., testing alternative explanations, checking for confounds)
- **Completeness gaps**: Are there critical conditions/baselines missing? (e.g., adding a control condition, testing edge cases)
- **Generalization concerns**: Does this hold beyond the specific setup? (e.g., testing on different task types, model families)
- **Methodological robustness**: Are the results stable/reliable? (e.g., statistical power, sample size, measurement noise)

**Expected time allocation**: 1–2 hours
