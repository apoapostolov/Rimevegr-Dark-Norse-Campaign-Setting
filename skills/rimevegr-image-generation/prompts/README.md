# Prompt batches

Place future prompt files in this folder.

## Folder purpose

Each file here should contain multiple prompts for one coherent generation run, such as:

- a named character pack
- a settlement pack
- a pantheon symbols pack
- a landscape pack
- a logo and wordmark pack
- a character concept-sheet pack with front, side, back, and close-head views

## Format

Use the JSON template in prompt_batch_template.json as the default structure.
A YAML authoring template is also available in prompt_batch_template.yaml.

Both formats support:

- operation-first prompt intent
- scene_routing fields based on the master scene index
- exact model selection for Gemini and Imagen family image models
- automatic per-item model routing with cheap versus premium decisions
- confirmation prompts when the router is unsure whether to use the cheap or expensive path
- number_of_images for per-item or default repeat counts
- identity-lock blocks for recurring characters
- locked elements and change requests for revision passes
- continuity notes for later refinement

## Output path

When generation is eventually enabled, final images should be written into the sibling images folder.

## Reference-image support

The generator scaffold accepts optional concept-reference images through the CLI and through batch fields so later runs can keep character identity more consistent.
