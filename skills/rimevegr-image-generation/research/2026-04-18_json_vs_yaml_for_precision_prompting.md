# JSON versus YAML for precision image prompting

Research date: 2026-04-18

## Question

Should extreme-precision prompting for Rimevegr be authored in JSON or YAML instead of plain prose?

## Short answer

Use structured data for authoring and validation, but still compile it into a natural-language final prompt for the model.

The evidence reviewed does support structured inputs as a clarity aid. However, the strongest image-generation guidance from Google still emphasizes descriptive scene language over disconnected machine-like field dumps.

## Findings

### JSON or YAML helps humans and tooling stay precise

Structured prompt specs are useful for:

- required fields
- validation
- reusability
- batch automation
- concept reference lists
- precise continuity locks
- per-image overrides

This is especially valuable for a skill-driven workflow like ours.

### The image model still responds best to directed natural language

The official Google guidance repeatedly recommends scene description and cinematic narration rather than bare keyword or parameter piles.

So the best pattern is:

1. write the prompt spec in JSON or YAML
2. validate it with the script
3. compile it into a final narrative prompt with strict instruction blocks

### JSON advantages

- strict and machine-safe
- easiest to validate in Python
- predictable for batch pipelines
- better for programmatic merging and schema enforcement

### JSON disadvantages

- harder to read and hand-edit for large prompt sets
- more visual noise in creative work
- trailing commas and escaping can annoy manual editing

### YAML advantages

- easier for humans to scan and edit
- better for nested creative specs and notes
- more readable for long prompt packs and concept sheets

### YAML disadvantages

- indentation mistakes are common
- parser behavior can surprise less technical users
- less rigid by default unless explicitly validated

## Recommendation for this skill

Best likely workflow for later approval:

- keep JSON as the execution format for the current script
- optionally support YAML authoring as a future convenience layer
- compile both into one strong narrative prompt before sending to the API

That gives:

- machine reliability
- human readability
- better image results than raw schema-only prompting

## Proposed field set for precision prompting

A good structured format would include:

- operation
- subject
- identity_anchor
- character_lock
- scene
- composition
- camera
- lighting
- materials
- palette
- mood
- environment
- exclusions
- aspect_ratio
- reference_images
- notes

## Bottom line

JSON or YAML is useful as the control surface.
The final API prompt should still read like a clear, well-directed brief.

## Source notes

Primary sources reviewed:

- Prompt Engineering Guide on structured inputs and outputs
- official Google image-prompting guidance on narrative scene description
- Nano Banana community prompts using variable blocks plus instruction prose
