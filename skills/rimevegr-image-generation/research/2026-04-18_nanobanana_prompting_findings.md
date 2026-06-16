# Nano Banana Pro prompting findings

Research date: 2026-04-18

## Scope

This note summarizes what current online guides repeatedly recommend for Nano Banana Pro and related Gemini-native image generation.

## High-confidence findings

### 1. Narrative scene direction beats keyword piles

The strongest repeated advice from Google is to describe the image as a coherent scene rather than dumping tags.

Practical implication for the skill:

- keep the prompt as a readable cinematic direction block
- lead with subject, action, environment, composition, and style
- use the skill modules to assemble one directed paragraph, not an unordered tag bag

### 2. Specific camera and lighting language materially improves control

Official guidance repeatedly stresses camera terms, lens choices, angle, lighting setup, and aspect ratio.

Useful control fields:

- shot type
- camera angle
- lens feel
- lighting setup
- mood atmosphere
- material detail focus
- aspect ratio

### 3. Positive framing works better than negative-only instruction

Instead of telling the model what not to include in vague terms, define the desired scene positively.

Better pattern:

- use "an empty road under sleet" instead of only "no people, no horses, no carts"
- reserve negatives for hard exclusions after the main scene is clearly defined

### 4. Strong verb first improves prompt direction

The Google Cloud guide recommends starting with a clear operation such as create, transform, edit, combine, or preserve.

This matters for the skill because our prompts often mix generation, editing, and identity preservation. The first sentence should make the job type explicit.

### 5. Multi-image references are first-class, not a hack

Official Nano Banana guidance explicitly supports multi-image reference composition and notes that reference images are ideal for consistency.

Implication:

- concept art and character identity sheets should be treated as formal reference inputs
- the skill should keep identity-lock instructions close to reference-image handling

### 6. Iterative refinement is part of the intended workflow

Official Google guidance does not assume perfection on the first pass. It explicitly recommends small follow-up edits.

Implication:

- the skill should support a generate -> inspect -> adjust loop
- prompt batches should preserve source prompts and delta edits for later refinement

### 7. Text rendering is unusually capable, but still benefits from exact quoting

The official guide advises using exact quoted text and describing typography clearly.

Implication for Rimevegr:

- wordmarks, logos, signage, law-stones, chapter covers, and symbolic labels should use explicit quoted text blocks when needed
- keep text small and intentional unless the asset is explicitly typographic

## Community-pattern findings

The most useful Nano Banana community prompts tend to use:

- a variable block for reusable slots
- a clearly named instruction section
- exact count rules
- identity-anchor language
- preserve-versus-change logic
- explicit camera and framing continuity rules
- a final avoid list for failure modes

This is valuable for our skill because it confirms that structured prompt authoring can coexist with natural-language scene direction.

## Recommended takeaways for the Rimevegr skill

Strong candidates for later approval:

- keep natural-language final prompts as the main output
- add stronger operation-first phrasing at the top of template-generated prompts
- standardize a camera block, lighting block, identity block, and exclusion block
- formalize iterative refinement notes in prompt batches

## Source notes

Primary sources reviewed:

- Google Cloud Blog: The ultimate Nano Banana prompting guide
- Google Developers Blog: How to prompt Gemini 2.5 Flash Image Generation for the best results
- GitHub community repo: aimikoda/nano-banana-pro-prompts
