# Identity lock system

Use this module when the same person must remain recognizable across batches,
poses, grading changes, or later revision passes.

## Core law

- every recurring character gets one compact identity-lock block
- the block is an authoring tool; the final prompt should still read like
  natural cinematic direction
- lock only what makes the person themselves
- do not lock incidental background details unless continuity truly depends on
  them

## What should usually be locked

Prioritize the traits that create recognition at a glance:

- face structure and age read
- scars, burns, missing parts, and old injuries
- hair shape, hair color, beard logic, and grooming neglect or discipline
- eye color when it is part of recognition or contrast
- body type and readable height band such as short, average, tall, compact, rangy, or broad-built
- rank markers, labor wear, and class-coded materials
- habitual posture, emotional bearing, and how the body occupies space
- recurring tools, tokens, or signature garments only if they are canon-safe

## Required fields

### identity_anchor

One sentence stating who the person is in visual terms.

Example:

- a scar-notched mercenary captain with tired authority, frost-burned skin, and
  practical iron-and-wool kit

### age_group

Optional but strongly recommended for recurring people.

Use a readable age band instead of an exact number so the model keeps the person
in the right life stage.

Examples:

- late teens
- early 20s
- late 20s
- 30s
- late 30s
- mid-40s
- 50s
- elderly but still active

For named characters, age_group should usually be treated as part of the core
identity lock.

### immutable_traits

Use for things that should not drift unless the user explicitly asks.

Examples:

- age band
- face shape
- scar placement
- eye damage
- hairline
- signature cloak or rank token

### flexible_traits

Use for things that may vary without breaking identity.

Examples:

- weather exposure
- mud level
- cloak position
- beard length within a narrow range
- fatigue intensity
- blood or soot amount from scene to scene

### allowed_scene_changes

List the transformations that are acceptable between batches.

Examples:

- indoor to outdoor relighting
- battle aftermath versus travel fatigue
- winter kit versus rain kit
- portrait crop versus full-body action frame

### forbidden_drift

Explicitly state what the model must not invent.

Examples:

- no heroic makeover
- no polished fantasy armor
- no younger face
- no clean salon hair
- no extra jewelry beyond canon

### attractiveness_scale

Optional -2 to 5 scale for face glamour control.

Use it to suppress the default modern-actor bias in image models.

- -2: outlawed, feral, hunted, gaunt, and actively unbeautified
- -1: distinctly unattractive, depleted, coarse, and hard-lived
- 0: plain, severe, and unflattering, with little beauty emphasis
- 1: harsh, broken, unbeautified, very hard-lived
- 2: rough, plain, asymmetrical, weather-beaten
- 3: average, worn, human, not glamorized
- 4: striking but still grounded, scarred, and tired
- 5: exceptional beauty only if explicitly intended by the user

Default guidance for Rimevegr:

- outlaws and wolfsheads: always -2
- most male NPCs: 0 to 1
- most women: usually +1 compared to similar men in the same hardship bracket
- working adults and mercenaries: usually 0 to 2
- female faction leaders and major female authorities: usually 2 to 3
- main protagonists: usually 1 to 3
- very few people should ever exceed 4

### weathering_cues

Optional list for face and skin hardening cues.

Examples:

- broken nose
- uneven teeth
- wind-burned skin
- old pox marks
- scarred cheek
- tired eyes
- rough beard growth
- chapped lips

### reference_images

Store image paths here when later identity preservation uses references.

## Recommended lock strength

Use the lightest block that still preserves recognition:

- 1 identity anchor
- 1 age_group when age stability matters
- 3 to 6 immutable traits
- 2 to 5 flexible traits
- 2 to 4 allowed scene changes
- 3 to 6 forbidden drift notes

If the lock becomes too long, the model will start flattening all outputs into
one repeated look.

## Authoring template

```json
{
  "identity_lock": {
    "identity_anchor": "A one-line visual thesis for the character.",
    "age_group": "late 30s",
    "attractiveness_scale": 1,
    "immutable_traits": ["trait one", "trait two"],
    "weathering_cues": ["broken nose", "wind-burned skin"],
    "flexible_traits": ["trait that may vary slightly"],
    "allowed_scene_changes": ["weather shift", "camera crop change"],
    "forbidden_drift": ["no polished fantasy armor", "no age regression"],
    "reference_images": ["references/character_name/front.jpg"],
    "continuity_notes": ["keep the nose break visible in profile"]
  }
}
```

## Rimevegr hardening notes

- identity should come from labor, scars, rank, age, and habit before beauty
- default faces should skew rough, asymmetrical, and hard-lived rather than
  model-beautiful
- keep cloth, leather, iron, fur, and grime believable for the setting
- never let the block turn into glossy fantasy-character marketing copy
- if divine or Veil pressure is present, it changes the scene around the person,
  not the person's core identity

## Validation check

Before approving a batch, ask:

- would I still recognize this person in low light or bad weather?
- did the model keep the face and bearing stable?
- did the kit remain materially grounded?
- did the character stay within class, rank, and survival logic?
