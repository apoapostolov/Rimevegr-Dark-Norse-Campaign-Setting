# Proposal for applying the research to the Rimevegr skill

Status: proposal only. Do not implement until explicitly approved.

Research date: 2026-04-18

## Goal

Use the new Nano Banana prompting research to strengthen consistency, controllability, and repeatability in the Rimevegr image-generation skill.

## Proposed changes for approval

### Proposal 1 — Add a prompt compiler layer

Add a builder step that turns structured prompt specs into one final natural-language cinematic brief.

Why:

- aligns with Google guidance favoring descriptive scene direction
- preserves the precision benefits of structured fields
- reduces drift from inconsistent manual phrasing

### Proposal 2 — Support YAML authoring alongside JSON

Keep JSON for execution, but allow YAML as an authoring format for easier hand-editing.

Why:

- YAML is more readable for lore-heavy prompt sets
- JSON remains ideal for validation and automation
- both can compile to the same final prompt

### Proposal 3 — Formal identity-lock blocks for recurring characters

Add a standard block with:

- identity anchor
- immutable traits
- flexible traits
- allowed scene changes
- reference image paths

Why:

- directly supported by the research on reference-driven consistency
- fits the main-cast needs of the setting
- reduces face and costume drift

### Proposal 4 — Introduce operation-first prompt templates

Every final prompt would begin with a clear action such as:

- create
- transform
- preserve and restage
- edit only
- combine references into

Why:

- aligns with the official Nano Banana guide
- makes generation intent explicit for the model

### Proposal 5 — Add iterative refinement notes to prompt batches

Each batch item could optionally include:

- base prompt
- locked elements
- change requests for later passes
- continuity notes from accepted generations

Why:

- matches how Google recommends using the model conversationally
- helps keep long-running visual continuity

## Recommended approval order

If you want a cautious rollout, approve in this order:

1. proposal 3
2. proposal 4
3. proposal 1
4. proposal 2
5. proposal 5

This sequence gives the biggest consistency gain with the lowest workflow risk.

## What I recommend not changing yet

- do not replace narrative prompts with raw schema dumps
- do not make live generation automatic
- do not overcomplicate the current script before identity-lock behavior is tested on real examples

## Approval questions for later

- should YAML support be added now or kept for a second phase?
- should character reference images live in one central folder or beside each prompt batch?
- should the compiler generate one compact paragraph or a multi-section directive block?

## Decision checkpoint

No changes from this proposal should be applied until you explicitly approve them.
