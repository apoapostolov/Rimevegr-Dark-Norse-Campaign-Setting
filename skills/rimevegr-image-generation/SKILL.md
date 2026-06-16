---
name: rimevegr-image-generation
description: >
  Reusable skill for creating lore-faithful Rimevegr image prompts, prompt
  batches, shot lists, logos, covers, portraits, and environmental concepts.
  Also includes a Gemini-keyed Nanobanana Pro generation scaffold that stays
  dormant until the user explicitly asks to run image generation.
---

# Rimevegr Image Generation

Use this skill whenever the task involves:

- Rimevegr or Norse Grit image prompts
- live-action style guides for images
- covers, logos, panoramas, portraits, faux screenshots, or asset packs
- prompt batch creation for later API image generation
- faction, character, or pantheon iconography visuals
- character concept design sheets and multi-view identity packs

## Core intent

Everything should feel like it belongs to one grounded live-action world:

- early-medieval Norse frontier
- low magic and deniable supernatural pressure
- practical wool, leather, iron, wood, rope, bone, and stone
- poverty, weather, hierarchy, and survival before spectacle

## Load order

When working in this skill, consult these in order:

1. references/REFERENCE_INDEX.md
2. references/GENERATION_CANON.md
3. the specific module needed for the task
4. the relevant prompt batch in prompts/

This skill folder is now the canonical home of the Rimevegr image-generation system.

Primary modules:

- references/GENERATION_CANON.md
- references/CORE_PROMPT_SYSTEM.md
- references/VEIL_AND_CRACKING_VISUAL_GUIDE.md
- references/PROMPT_ADDONS_LIBRARY.md
- references/CINEMATIC_COLOR_SYSTEM.md
- references/MASTER_SCENE_INDEX.md
- references/IDENTITY_LOCK_SYSTEM.md
- references/STRUCTURED_PROMPT_WORKFLOW.md
- references/NAMED_CHARACTERS_VISUAL_BIBLE.md
- references/FACTION_LEADERS_AND_RIVALS_VISUAL_BIBLE.md
- references/PANTHEON_SYMBOLS_AND_ICONOGRAPHY.md
- TODO.md for the skill roadmap

## Workflow

1. Choose the asset type
   - portrait
   - interior
   - exterior
   - panorama
   - logo or wordmark
   - landmark
   - montage

2. Choose the subject layer
   - named character
   - faction or settlement power
   - event or process
   - pantheon symbolics

3. Choose the scene pressure
   - weather
   - social tension
   - hunger or poverty
   - violence aftermath
   - optional Veil presence only if the user explicitly wants it

4. Choose the color family
   - fjord steel
   - moor ash
   - black pine compression
   - iron-road militarist
   - long-dark frost
   - northern wrong-light

5. Save final prompts as a batch file in prompts/

6. Do not generate images unless the user explicitly asks for execution

## On-hold concept design scaffold

A dormant concept-sheet workflow is included for later use.

When the user explicitly activates it, the system should produce character concept sheets that include:

- full-body front view
- full-body side view
- full-body back view
- close head portrait
- facial identity anchors, materials, and costume notes

Until then, keep it as scaffold only and do not execute concept-sheet production automatically.

## Hard rules

- Never drift into generic shiny Viking fantasy.
- The Veil is off by default unless the user explicitly wants it in the scene.
- If the user wants the Veil or the Cracking, translate them into visible symptoms rather than relying on the lore name alone in the final prompt.
- Never overuse Veil presence or sky-wound evidence.
- The Cracking belongs only in sky-heavy wide exteriors.
- Gods are shown through crude human-made marks, never clean divine portrait art.
- When using divine symbols, follow the exact canonical glyph locks in the pantheon guide rather than improvising new emblem designs.
- For recurring people, use one identity-lock block so face, scars, bearing, class markers, and attractiveness scale remain stable across batches.
- When a named character is used, always check the named-character bible and carry over the attractiveness override together with the other identity and prompt-guidance elements.
- This is now a hard validation requirement for prompt batches, not just a style suggestion.
- Never rely on a bare name as if the model already knows the person; describe the person fully and place the name in parentheses only as a label or reference anchor.
- Never write the phrase attractiveness scale in the final prompt; translate the score into visible face, posture, grooming, and clothing-state cues instead.
- Use operation-first prompt language so each item clearly states whether it should create, preserve and restage, transform, edit only, or combine references.
- Structured authoring is allowed, but the final compiled prompt should still read like strong natural scene direction rather than a raw schema dump.
- The prompt-writing AI should decide which optional fields are actually needed for a given shot and omit the rest rather than dumping full schema detail into every prompt.
- Faces should default to rough, weathered, asymmetrical, and hard-lived rather than clean modern-actor beauty; use explicit attractiveness control when needed.
- Use the expanded attractiveness scale from -2 to 5 when face control matters.
- Women should usually sit about one step higher than comparable men in the same class and hardship bracket, but still stay grounded and weathered.
- Female faction leaders may sit one step higher again if the shot benefits from sharper presence, status maintenance, or commanding allure without turning glossy.
- Outlaws or wolfsheads should default to -2 on the attractiveness scale.
- Leaders show power through maintenance, leverage, posture, and material control.
- Main cast identity comes from scars, labor, rank, and behavior more than from beauty.

## Prompt batch format

Each prompt file in prompts/ should contain multiple prompt items for a single theme, set-piece, or asset pack.

- JSON remains the automation baseline
- YAML is also supported for easier hand-authoring
- structured fields can be used during authoring, but they should compile into a natural-language cinematic prompt for final use

## API scaffold status

The script in scripts/ reads a Gemini key from the repository .env file,
supports the current Gemini and Imagen image-model family, can verify which of
those models are available on the active API key without generating images, and
always reports estimated cost before and after a run.
