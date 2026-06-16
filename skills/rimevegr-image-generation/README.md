# Rimevegr image generation skill

This folder packages the Rimevegr image system into a reusable skill.

## What is here

- SKILL.md: operational rules for AI use
- references/: distilled setting canon, source map, and the master scene index
- research/: external prompting research and proposal notes awaiting approval
- prompts/: future prompt batch files, each containing multiple prompts for one generation run
- images/: target output folder for final generated images
- scripts/: API scaffold for future Gemini-keyed Nanobanana Pro generation
- requirements.txt: Python dependencies for the scaffold

## Current status

The structure is ready for both dry-run and live image generation.
The prompt workflow now supports identity-lock authoring, operation-first batch
items, JSON or YAML batch files, continuity notes for later refinement, exact
Gemini and Imagen model selection, per-prompt automatic cheap-versus-premium
routing, confirmation when a model choice is unclear, API-key availability
checks, and cost reporting for each run.

## Intended workflow

1. Write or refine a prompt batch in the prompts folder.
2. Review it for lore fit and visual variety.
3. When explicitly approved, use the script scaffold to validate the batch and later run generation.
4. Save final outputs into the images folder.

## Important constraints

- keep the look grounded and live-action
- avoid high-fantasy gloss
- treat the gods as symbols and carvings, not avatars
- use weather, class, labor, and rank to differentiate images
