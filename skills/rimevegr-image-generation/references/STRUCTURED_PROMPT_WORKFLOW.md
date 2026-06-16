# Structured prompt workflow

This module covers Prompt 12 onward: operation-first prompting, compiled prompt
assembly, YAML authoring support, and iterative refinement notes.

## Core rule

Structured fields exist to improve control during authoring, but the final image
prompt should still read like a strong natural-language cinematic brief.

Do not dump raw schema at the model unless the user explicitly wants a
mechanical format.

## Operation-first prompt language

Start every item with the clearest job the model is being asked to do.

| Operation               | Use when                                                             | Intent            |
| ----------------------- | -------------------------------------------------------------------- | ----------------- |
| create                  | making a new image from scratch                                      | fresh composition |
| preserve and restage    | keeping the same identity but changing pose or setting               | continuity        |
| transform               | changing season, lighting, or condition while keeping the core scene | controlled change |
| edit only               | adjusting one accepted image with minimal drift                      | surgical revision |
| combine references into | using multiple visual anchors in one result                          | synthesis         |

## Prompt compiler order

Build the final prompt in this order:

1. operation
2. identity lock
3. subject and action
4. setting and material reality
5. camera or framing notes
6. mood and grading
7. optional Veil or Cracking symptoms only if requested
8. locked elements and change request
9. continuity notes from previous accepted outputs

## Compiler target shape

The compiled result should read like this:

> Create a grounded live-action scene of a scarred mercenary captain crossing a
> rime-wet ferry landing at dusk, keep the broken nose and left-cheek scar
> fixed, allow cloak movement and fresh mud, preserve tired command posture,
> avoid polished fantasy armor, shot as a cold medium-wide frame in fjord steel
> grading.

## Field selection law

The authoring schema is intentionally richer than the final prompt sent to the
image model.

The compiler or prompt-writing AI should decide what to include based on the
user request, the type of shot, and whether continuity actually matters.

### Mandatory metadata

Keep these stable in every batch:

- batch_name
- model or accepted model default
- one operation per item
- one aspect ratio at the default or item level
- one prompt or one structured prompt block per item

### Optional and conditional fields

These are candidate inputs, not always-on output:

- scene_routing
- identity_lock for one-off scenes
- flexible_traits and allowed_scene_changes when continuity is not important
- locked_elements when nothing specific must stay fixed
- change_request only for revision passes
- continuity_notes only after accepted generations
- Veil, Hush, and Cracking only when the user explicitly asks for them

### Minimal relevant rule

Use the minimum number of fields needed to make the shot clear, stable, and
lore-faithful.

For named characters, the attractiveness override is part of the identity lock
check and should be reviewed alongside scars, posture, rank markers, forbidden
drift, and other canon guidance rather than treated as an optional afterthought.

Named-character batches should fail validation if they reference a canon person
without an identity lock, an identity anchor, an attractiveness override, and
at least one stable canon-guidance block.

Do not write raw control language like attractiveness scale 2 into the final
prompt. Convert that setting into visible description: face, posture, grooming,
material upkeep, and clothing condition.

For most single images, that means:

- one scene family or sub-scene
- one subject focus
- one mood family
- one color family
- two to four pressure cues at most
- identity-lock details only if the shot needs continuity

## JSON and YAML workflow

Both authoring paths are now acceptable:

- JSON stays the automation baseline
- YAML is allowed for easier hand-editing and review
- both formats should resolve into the same internal batch structure

Use JSON when:

- you want stricter validation
- you are feeding automation directly
- you want less ambiguity around arrays and quoting

Use YAML when:

- the batch is lore-heavy and easier to review as prose
- the prompt pack will be edited by hand several times
- you want cleaner multiline continuity notes

## Iterative refinement loop

Use this loop after an image or batch gets close:

1. establish the first accepted look
2. record what must stay fixed
3. issue one clear change request at a time
4. preserve and restage before attempting bigger transformations
5. keep continuity notes short and visual

## Suggested item fields

- operation
- prompt
- structured_prompt
- identity_lock
- attractiveness_scale from -2 to 5 when a face-focused character shot needs glamour control
- weathering_cues when the person should feel broken-in, rough, or hard-lived
- locked_elements
- change_request
- continuity_notes
- reference_images
- notes

## Hardening rules

- one main operation per prompt item
- one identity lock block per recurring person
- one dominant mood family per image
- one Veil level only if explicitly requested
- the compiler should prune optional fields automatically instead of sending
  every populated field
- most detailed fields are conditional authoring aids and may be left out when
  they do not improve the shot
- never replace good scene language with raw checklist spam
- do not let continuity notes grow into a second full prompt
