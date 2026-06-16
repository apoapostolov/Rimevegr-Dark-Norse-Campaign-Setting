# TODO - Rimevegr image-generation skill

## Current Focus

- maintain, harden, and extend the reusable Rimevegr image-generation skill
  package
- canonical owner: skill docs under writing/norse_grit/skills/rimevegr-image-generation

## Scope And Boundaries

- this pass owns character-type prompt add-ons, event prompt add-ons, and system/domain illustration guidance
- this pass also owns the skill-level organization for reusable visual prompt docs
- this pass does not rewrite core lore canon unless the user explicitly asks for lore changes
- this pass should stay aligned with the existing setting bible, culture, religion, economy, geography, settlement, and simulation docs

## Completed foundation work

- Prompts 1 through 9 were completed earlier and now live in the core canon,
  visual bibles, add-on library, color system, and Veil translation modules.

## Completed advanced workflow work

### [x] Prompt 19 — Add model registry and cost reporting

Expanded the generation script so it can target the full supported Gemini and
Imagen image-model family, verify model access on the active API key, process
multiple images sequentially, and always print estimated run cost.

Outputs:

- exact CLI model override support
- API-key availability checks without image creation
- per-item and total cost reporting
- cost-safer default batch templates

Validation:

- verified live model discovery on the current API key
- verified dry-run reporting with pricing output

### [x] Prompt 18 — Add roughness and attractiveness control

Added optional face-glamour suppression so characters can default away from
clean actor-like beauty and toward harder, more historical-looking faces.

Outputs:

- optional attractiveness scale for continuity and portrait work
- weathering cues for rough skin, broken noses, tired eyes, and related wear
- stronger canon language against polished modern-beauty drift

Validation:

- verified in compiled prompt output and reflected in the canonical skill docs

### [x] Prompt 17 — Add selective field pruning

Added compiler rules so mandatory metadata stays stable while optional detail is
included only when the shot actually needs it.

Outputs:

- batch-level prompt_policy controls for field selection
- automatic pruning of conditional routing, identity, change, and continuity
  fields
- minimal-relevant compiled prompt behavior for Nanobanana-ready prompts

Validation:

- verified in dry-run previews for both JSON and YAML templates

### [x] Prompt 16 — Build a master scene index

Added a hyper-extensive routing index so almost any request can be mapped before
creating a dedicated prompt batch.

Outputs:

- master scene taxonomy in references/MASTER_SCENE_INDEX.md
- ready seed batch in prompts/master_scene_batch_seed.yaml
- routing guidance for deciding what should stay modular versus prebuilt

Validation:

- linked into the core skill documentation and reference index

### [x] Prompt 11 — Add formal identity-lock blocks

Added a recurring-character control block for cross-batch stability.

Outputs:

- identity anchor field
- immutable traits list
- flexible variation list
- allowed scene-change notes
- reference image path support guidance
- dedicated module in references/IDENTITY_LOCK_SYSTEM.md

Validation:

- implemented in the skill docs and batch templates
- verified by dry-run scaffold validation

### [x] Prompt 12 — Add operation-first prompt language

Strengthened final prompt construction by leading with the exact task type.

Outputs:

- reusable opening verbs and operation blocks for create, edit, preserve, or
  combine workflows
- guidance for keeping narrative prompt flow natural and cinematic
- compiler-aware operation handling in the scaffold preview flow

Validation:

- final prompts remain natural-language cinematic briefs
- verified by dry-run scaffold validation

### [x] Prompt 13 — Add a prompt compiler layer

Added a builder step that compiles structured prompt specs into one polished
natural-language brief for dry-run review.

Outputs:

- compiler behavior documented in references/STRUCTURED_PROMPT_WORKFLOW.md
- mapping from structured fields into final narrative prompts
- hard constraints for lore and anti-drift handling

Validation:

- compiler preview now appears in the scaffold dry run
- no live image execution was enabled

### [x] Prompt 14 — Add optional YAML authoring support

Added YAML authoring support on top of the current JSON execution format.

Outputs:

- JSON remains the execution baseline
- YAML template added for easier hand-authoring
- migration and validation constraints documented in the workflow module

Validation:

- verified by successful dry-run loading of both JSON and YAML templates

### [x] Prompt 15 — Add iterative refinement support notes

Added a continuity workflow for accepted image generations and follow-up
adjustments.

Outputs:

- base prompt, locked elements, allowed changes, and continuity note structure
- process notes for generate, inspect, and refine cycles
- batch template support for change requests and continuity notes

Validation:

- the current dry-run and manual approval gates remain intact
- verified by scaffold preview output

## On Hold — Do not execute until explicitly requested

### [ ] Prompt 10 — Maintain important-character concept design templates

This queue is on hold until the user explicitly tells the project to start execution.

Outputs:

- maintain a concept design template for every important character, defined by the user from the clearest preferred look
- keep a reusable system prompt for live-action concept sheets covering full body, close head, front, side, and back views
- keep generator CLI support for passing concept art reference images so character sameness can be preserved across batches

Validation:

- concept-template work must not begin automatically
- no batch should execute from this queue without direct user instruction

## Working Rules

- canonical source: writing/norse_grit numbered lore documents
- derived references belong in writing/norse_grit/skills/rimevegr-image-generation
- do not overload every prompt with the same Veil, Cracking, or icon stack
- preserve the live-action grounded tone established in the core template
- markdown changes should be linted after edits

## Decision Log

- 2026-04-18: This roadmap began as the handouts working queue for the comprehensive prompt-addon pass.
- 2026-04-18: The handout markdown set was migrated into the skill package so the skill is now the canonical home of the Rimevegr image system.
- 2026-04-18: Completed the first comprehensive addon library covering character types, event scenes, and system illustration packs for image prompt generation.
- 2026-04-18: Added a dedicated cinematic color-grading and emotional filter exploration pass to avoid visual sameness across prompt outputs.
- 2026-04-18: Expanded the handouts pass to include strict visual-and-behavior bibles for named characters, faction leaders, rivals, historical figures, and pantheon iconography.
- 2026-04-18: Hardened the Veil, Cracking, and divine-symbol systems so coined setting terms are translated into repeatable visual logic for image models.
- 2026-04-18: Moved the research proposal themes into the TODO as future roadmap items rather than leaving them only in a standalone proposal note.
- 2026-04-18: Approved and implemented Prompt 11 onward, adding identity locks, operation-first prompt language, a dry-run compiler preview, YAML authoring support, and iterative refinement notes.
- 2026-04-18: Added a no-situation-left-behind master scene index so future image requests can be routed systematically instead of exploding into an unmanageable batch library.
- 2026-04-18: Hardened the compiler with minimal-relevant field pruning so the prompt-writing AI can omit optional schema detail unless the scene or user request actually requires it.
- 2026-04-18: Added an explicit roughness and attractiveness control layer to push characters away from clean professional-actor faces and toward harder, more weathered frontier realism.
- 2026-04-18: Expanded the script to support exact Gemini and Imagen model selection, non-generating availability checks on the live API key, multi-image execution, and always-on cost reporting.

## Risks And Blockers

- risk: over-specifying prompts so all images collapse into one look
- risk: generic Viking drift if prompt add-ons ignore class, labor, and survival details
- risk: future structured authoring features could accidentally make prompts feel too mechanical if not compiled back into strong scene language
- blocker: none currently

## Protected Template

Use this structure when a new major undertaking becomes the active queue in this file:

```md
## Current Focus

- one-sentence mission
- explicit canonical file or system owner

## Scope And Boundaries

- what this pass owns
- what this pass explicitly does not own

## Active Prompt Queue — <Epic Name>

### [ ] Prompt 1 — <goal>

Short prompt description.

Outputs:

- expected file or system result

Validation:

- tests, lint, preview commands, or manual checks

### [ ] Prompt 1A — <sub-goal>

Use sub-prompts when a prompt needs to be split without hiding partial
completion.

Completed output:

- concrete finished deliverable

## Working Rules

- canonical source
- derived outputs
- rollback or safety notes

## Decision Log

- YYYY-MM-DD: important scope or design decision

## Risks And Blockers

- open risk
- explicit blocker if present
```
