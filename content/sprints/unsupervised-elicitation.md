---
title: "Sprint: Unsupervised Elicitation"
nav_title: Unsupervised elicitation
topic: Coherence
phase: 1
order: 1
submit_url: "https://airtable.com/appHnvwbow1epprSd/pagaKp5UPAr4jLIxo/form?prefill_Sprint+Project+ID=UE1&prefill_Phase=Phase+1"
contact_subject: "Praxis Sprint UE1 questions"
---

This is a phase 1 project. To submit, use [this form]({{submit_url}}); don't edit
the prefilled fields. If you have any questions or issues, email
[{{email}}](<mailto:{{email}}?subject={{contact_subject}}>) with
"{{contact_subject}}" as title.

## Overview

In this project, we examine the concept of coherence from [Unsupervised
Elicitation of Language Models](https://arxiv.org/html/2506.10139v1), which
proposes Internal Coherence Maximization (ICM). The key observation from this
paper is that coherence can be effectively measured by pretrain-only base
models. ICM searches for coherent labels over a set of unlabeled examples, and
the labels are then used to train a model (in-context or supervised
fine-tuning). The whole process requires minimal human input, yet performs on
par with using large number of gold labels. ICM operationalizes coherence in a
way that only relies the base language model, without any human supervision,
making it appealing for safety. Beyond elicitation of capabilities, some
applications of ICM include:

- Elicitation of latent knowledge and belief
- Improve honesty, i.e., the consistency between actions and beliefs
- Outer alignment, i.e., the creation of value specifications and constitutions

This sprint project has two tasks:

1. Reimplement ICM
2. Think through some key questions about the method

## Part 1: Replication

Your first task is to implement ICM and reproduce the TruthfulQA results. Before
diving in, we suggest spending about an hour reading the paper.

**Task**

- Implement ICM (algorithm 1) without logical consistency fix.
- Use [this dataset of TruthfulQA examples](https://drive.google.com/file/d/1TA5UrRBPBQu3uBo0qAnR9Or4Plo2g8oS/view?usp=drive_link). This contains 1/10 of the original dataset (256 train, 100 test).
- Run ICM to search for labels, then use them for in-context learning, not SFT.
- Generate a figure in the same format as the TruthfulQA subfigure in Figure 1 of the paper with the same four conditions.
  - Figure 1 in the paper presents SFT results. You only need to do in-context learning.
  - Your figure should have the same format but not necessarily the visual details.
  - Due to various changes to the setup (e.g., less data), you might not reproduce the exact results, but the general trend should hold.
- Use Python. Check out the [original repo](https://github.com/Jiaxin-Wen/Unsupervised-Elicitation) and a popular [reimplementation](https://github.com/codelion/icm). You're allowed to reuse existing code.

**Model choice**

- Base: Llama-3.1-405B
- Chat: Llama-3.1-405B-instruct
- Use both through [hyperbolic API](https://www.hyperbolic.ai/)
  - You are expected to look through and understand the docs on your own.
  - You have to set up your own API key. These experiments should cost ~$20.

**Deliverables**

- Submit your code using the submission form. Google drive link to zip file or link to Github repo.
- Your code repo should include the main results figure.

**Evaluation criteria**

- Accuracy of ICM reimplementation.
- ICM few-shot accuracy using your implementation (based on your bar chart).
- Code clarity. But we don't seek production quality code.
- You can use AI tools. If you do so, let us know what tools and how, and include links to relevant chat logs in your submission.

**Expected time allocation**: 3–6 hours

## Part 2: Critique

Part 2 simulates how you'd think through an actual research question. We want
you to think about ICM critically, about what you'd do to quickly test your idea
and reduce your uncertainty, and follow-ups based on different outcomes of that
first test.

**Procedure**

1. Identify one methodological weakness, limitation, or questionable design choice that you think is important (see guidance below on what to focus on)
2. Brainstorm practical fixes and/or simplifications to address this issue. Make sure to show us your thought process, exercising [reasoning transparency](https://www.effectivethesis.org/research-advice/reasoning-transparency) (honestly conveying your uncertainties, your information sources, etc).

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
