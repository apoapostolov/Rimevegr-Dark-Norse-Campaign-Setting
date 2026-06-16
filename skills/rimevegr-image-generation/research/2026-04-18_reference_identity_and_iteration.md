# Reference images, identity locking, and iteration

Research date: 2026-04-18

## Why this matters

Rimevegr needs cast consistency across portraits, concept sheets, montage frames, and later scene batches. The latest Nano Banana and Gemini guidance strongly supports reference-driven workflows for this.

## Key findings

### Reference images help with consistency far more than repeated text alone

Official Google guidance explicitly recommends using reference images for:

- character consistency
- style transfer
- multi-image composition
- maintaining composition or dimensions when text alone is too loose

### Exact preserve instructions matter

The strongest community prompts do not merely say "same person". They say things like:

- preserve facial structure exactly
- preserve proportions and likeness
- keep camera viewpoint consistent
- keep pose or background unchanged unless instructed otherwise

This suggests a good identity-lock block should include:

- face structure
- build and silhouette
- scar locations
- hairstyle and beard state
- clothing continuity rules
- what may change versus what must remain fixed

### Aspect-ratio stability can be guided with references

Google notes that input image aspect ratio is often preserved during editing, and the last provided image can influence output ratio. Reference images can therefore be used not only for identity, but also layout discipline.

### Iterative editing is a core strength

The model is built for follow-up instructions like:

- keep everything the same but warm the lighting
- keep the face exactly the same and change only the cloak
- keep composition and replace the background with a fjord cliff road

For the skill, this suggests prompt batches should support:

- base prompt
- locked elements
- allowed changes
- next-step edits

## Proposed identity-lock schema ideas

For later approval, each important character could eventually have:

- one concept sheet reference image
- one short identity paragraph
- one hard-lock list
- one flexible-variation list

Example lock categories:

- immutable: face shape, scars, eye character, age band
- semi-stable: haircut length, beard roughness, cloak palette
- flexible: weather, angle, light, environment, prop pose

## Fit with current skill

This research supports the direction already started in the concept-sheet scaffold and the reference-image flag in the generator script. It argues for expanding those carefully, but only after explicit approval.

## Source notes

Primary sources reviewed:

- Google Developers Blog image prompting guide
- Google Cloud Nano Banana prompting guide
- community prompt collections using identity-anchor wording
