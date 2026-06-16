# Rimevegr generation canon

This file distills the current Rimevegr image system into one reusable skill reference.

## World look

- grounded live-action historical fantasy
- early-medieval Norse frontier under long cold twilight
- practical materials only: wool, leather, wood, bone, iron, rope, stone
- beauty exists, but it is severe, weathered, and temporary

## Base shot families

- outdoor establishing shots for settlements, roads, moors, coasts, and passes
- indoor longhouse and workroom shots for political, domestic, and labor scenes
- panoramas for regional mood and sky-heavy geography
- portraits and half-body studies for rank, scars, and behavior
- landmark hero shots for barrows, passes, halls, ferries, mines, and stones
- dynamic montage shots for two-scene and three-scene narrative panels

## Survival-first visual language

Always emphasize some mix of:

- weather pressure
- material poverty
- class or rank
- labor and maintenance
- hunger, smoke, mud, or rime
- social caution and emotional restraint

## Opt-in supernatural translation rules

### The Veil

- the default state is no Veil effect unless the user asks for it
- use the project term internally, but in the final prompt describe the visible symptoms instead of relying on the name alone
- translate Veil presence into grey-white rime-mist, swallowed distance, muted sound, sudden cold, wrong shadows, lost direction, or pressure-filled stillness
- choose one intensity level only, from faint atmospheric unease to strong reality strain
- best for moors, barrows, northern ice, hush scenes, old stones, and threshold places

### The Hush

- sound can die in different ways: dead-zone silence, watched silence, or death-echo silence
- show it through frozen posture, fleeing animals, padded stillness, and a world that feels abruptly emptied or observed

### The Cracking

- also opt-in only
- translate it into faint broken-vein scar lines high in the cloud deck or a pale wounded sun with no warmth
- not lightning, not beams, not portals, not a glowing sky-rift
- only for wide sky-heavy exterior scenes
- distant evidence of a damaged world, never the main special effect

## Character image law

- Voss is hard command and old debt
- Gest is survival arithmetic and ledger pressure
- Kell is the unshowy line-holder
- Thorne is burned rune-aware vigilance
- Petra is provider competence and field judgment
- Ash is restrained uncanny professionalism
- Dalla is cook-fire order and hidden ritual knowledge
- Snorri is age and accumulated campaign damage
- Ubbe is the veteran already planning the exit
- Orm is the useful recruit not yet fully remade
- Dagfinn is desperation entering the column
- Lump is low-status usefulness trying to rise

## Face and attractiveness law

- most people in the setting should look rough, tired, asymmetrical, and
  materially worn rather than like modern professional actors
- the working scale now runs from -2 to 5, so below-zero reads are valid when a
  person should look actively depleted, feral, or socially stripped down
- most male NPCs should usually land around 0 to 1, not idealized beauty
- females in general should usually sit about +1 above comparable males in the
  same class and hardship bracket, while still staying weathered and practical
- female leaders may sit another +1 higher when their authority is meant to read
  as sharper, more maintained, or more striking without becoming glamorous
- outlaws and wolfsheads should default to -2 unless the user explicitly asks
  for an unusual exception
- even notable protagonists should stay scarred, wind-burned, under-slept, and
  grounded in labor and weather
- avoid perfect skin, bright modern smiles, salon hair, symmetrical fashion-face
  structure, or clean influencer grooming unless the user explicitly wants an
  exceptional contrast

## Faction differentiation

- Three Wolves: predatory pack cruelty
- Bone Pack: scavenger and grave-haunted roughness
- Silent Oar: coastal silence and tar-dark efficiency
- Hollow Hall: militarized iron-road discipline
- Iron Tide Remnant: old sea-war veterans worn thin
- Grave Wardens: procedural anti-barrow specialists
- Red Tide: unstable raider violence and theft-made kit

## Color and grading families

Use one of these as the primary image family:

- fjord steel
- moor ash
- black pine compression
- iron-road militarist
- long-summer mud
- long-dark frost
- northern wrong-light

## Structured authoring law

- start each item with a clear operation such as create, preserve and restage, transform, edit only, or combine references into
- use identity-lock blocks for recurring characters so the same face, scars, posture, and class-coded materials survive across batches
- structured fields are allowed during authoring, but the final prompt should still read like cinematic natural language
- JSON remains the execution baseline, while YAML is acceptable for human authoring and later compilation
- continuity notes should be short, visual, and focused on what must remain stable between accepted generations

## Pantheon depiction law

The gods do not arrive as polished portraits.

Show them through:

- god-posts
- scratched shrine marks
- soot-black carvings
- law-stones
- grave symbols
- doorpost cuts
- bone or antler tokens

Use one exact canonical glyph at a time. Keep its silhouette, orientation, and
count-locked features stable rather than letting the model invent decorative
variants.

Key icon logic:

- Odynn: upside-down one-eyed hanging figure beneath a forked branch, one rope loop only
- Thurr: blunt split-fist sigil with four knuckle cuts and one central crack
- Fraeja: gaunt tear-cut face with spindle and child-skull or child-bundle pair
- Lopt: stitched mouth mask with three cross-stitches and one inverted warning mark
- Hael: seated half-flesh half-bone figure split by one straight centerline
- Tyvr: rigid one-armed law figure with the missing hand given to a wolf jaw
- Skathi: faceless narrow huntress with a drawn bow and three ice-triangle cuts
- Bragi: broken lyre with exactly three snapped strings and a recitation notch
- Heimr: open ring pierced by one vertical threshold line, often flanked by two gate-post cuts

## Anti-drift checks

Before finalizing prompts, ask:

- Does this look too polished or heroic?
- Is rank shown through material and posture instead of fantasy costume?
- Is the weather doing meaningful work?
- Is the background varied enough to avoid sameness?
- Is the supernatural restrained enough to stay deniable?
