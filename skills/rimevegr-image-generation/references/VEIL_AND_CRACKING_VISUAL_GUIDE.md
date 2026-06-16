# Veil and Cracking visual guide

This module exists because generic image models do not understand the
project's coined lore terms by themselves.

Use the lore names internally for organization. In the final image prompt,
translate them into concrete, camera-visible symptoms.

## Core law

- The Veil is never automatic.
- The default state is no Veil effect.
- Only add Veil presence if the user explicitly wants it or the scene truly
  depends on it.
- When Veil presence is active, describe what the camera sees and what the air
  is doing. Do not rely on the word alone.
- The Cracking is also opt-in. It belongs only in wide, sky-heavy exterior
  shots where the heavens are visible.

## Visual translation for the Veil

When the user wants the Veil present, translate it into some of these visual
symptoms:

- grey-white rime-mist rolling low across ground, water, or stone
- distant landmarks softened, swallowed, or fading too early into haze
- unnatural stillness and sound-dampened air
- sudden cold without matching weather cause
- wrong or doubled shadow angles
- pale blue edges on flame or reflected firelight
- figures pausing as if they feel watched
- animals refusing to move or already fleeing
- compasses failing, stars looking wrong, direction becoming unreliable
- path depth feeling inconsistent, with distances that read slightly wrong
- face-like or memory-like shapes half-forming in fog, never resolving cleanly
- black dead ground or grass failure around barrows and old cursed sites
- pale corpse-lights or cold lantern-like glows at dusk near active death-sites

Do not use every symptom at once. Pick the smallest set that sells the mood.

## Veil presence ladder

Choose one level only.

### Level 0 — absent

Use for ordinary scenes in the Rimevegr when the user did not request the
Veil.

Visual result:

- harsh cold realism only
- no extra mist pressure beyond normal weather
- no reality distortion cues

### Level 1 — trace presence

Use for a faint supernatural brush that is still easy to deny.

Visual result:

- thin grey-white haze near the ground
- slightly muted distance
- the sense that birdsong or wind has just stopped
- one subtle unease cue in posture or spacing

Best for:

- watch posts
- quiet forest paths
- lonely road approaches
- settlement edges at dusk

### Level 2 — atmospheric pressure

Use when the environment feels wrong but not yet openly unreal.

Visual result:

- rime-mist pooling around stones, roots, or low marsh ground
- swallowed landmarks and padded depth
- sudden visible cold in breath and surfaces
- one slightly misaligned shadow or light angle
- silence that feels heavy rather than empty

Best for:

- moor crossings
- standing-stone circles
- barrow approaches
- northern coast in bad visibility

### Level 3 — active distortion

Use when reality is under visible strain but the scene must still read as a
live-action world.

Visual result:

- compasses fail and stars read wrong if the sky is visible
- multiple weak light angles from impossible directions
- distant objects feel too near or too far
- pale corpse-lights at dusk
- characters hesitate, stare, or lose orientation
- old flames or rune-lit surfaces take on faint blue edges

Best for:

- active barrow perimeters
- old temples
- Icebreak and the deep north
- ancient standing-stone sites

### Level 4 — focused attention event

Use for strong Veil scenes where the world feels watched.

Visual result:

- total silence or near-total silence
- abrupt hard cold arriving all at once
- animals already bolting before people notice the change
- background fog shaping itself into almost-forms that never resolve
- path logic feeling unstable, as if the scene wants people to step the wrong
  way
- severe pressure in body language, with people frozen, listening, or moving
  involuntarily toward the wrong place

Best for:

- major seidr scenes
- sealed barrows about to open
- First Barrow adjacency
- major omen or dread set pieces

### Level 5 — edge-of-collapse

Use only if the user explicitly wants severe surreal reality-bending while
still staying grounded.

Visual result:

- the horizon reads uncertain or slightly flattened
- repeated tree lines or stones feel subtly duplicated
- doorways or passages read fractionally too narrow, too tall, or too deep
- frost gathers in ways the wind does not explain
- perspective looks pressured rather than broken into fantasy spectacle

This is the highest setting and should stay rare.

## Hush variants

The Hush is not one single effect. Pick the version that matches the shot.

### Dead-zone hush

A fixed place where the world's deeper structure has gone quiet.

Visual cues:

- still air
- no birds or insect motion
- static composition
- warded or carved objects looking cold and spent

### Attention hush

A mobile event that feels like something has turned its gaze toward the scene.

Visual cues:

- everyone subtly pausing at once
- animals fleeing before the silence fully lands
- sudden temperature drop
- pressure from too many directions

### Death-echo hush

A residue from massacre, plague, shipwreck, or old mass death.

Visual cues:

- muffled air over graves, battlefields, or old ruins
- ash-sunk quiet
- weighted stillness
- the scene feeling pressed down by memory

## Visual translation for the Cracking

When the user wants the Cracking visible, do not depend on the word alone.
Translate it into distant sky evidence.

### Sky-wound level 0 — absent

No visible sign in the sky beyond ordinary overcast or winter light.

### Sky-wound level 1 — faint hint

Visual cues:

- faint scar-like broken-vein lines high in the cloud deck
- a pale weak sun with no warmth
- distant wounded-sky feeling that does not dominate the composition

### Sky-wound level 2 — clear but distant

Visual cues:

- thin fracture patterns crossing upper cloud layers
- subtle wrong-light around the high overcast
- a sky that feels damaged, not magical

### Sky-wound level 3 — rare panorama emphasis

Use only for major panoramas or setting-defining shots.

Visual cues:

- the upper sky carries visible old scar-lines
- the land below remains the focus
- the heavens feel historically wounded, not explosively active

## What never to do

Never render the Veil or the Cracking as:

- glowing portals
- laser beams
- neon magic fissures
- floating sigils everywhere
- glossy fantasy spell effects
- cosmic tentacles or abstract space art
- clean ghost armies in full display

The supernatural in the Rimevegr is cold, deniable, and pressure-based.
It bends reality by making the ordinary world feel wrong, not by replacing the
ordinary world with spectacle.

## Prompt assembly rule

When building a final prompt:

1. Ask whether the user wants Veil presence at all.
2. If no, keep the scene at Level 0.
3. If yes, choose one Veil level and at most one Hush variant.
4. Use only 2 to 4 concrete symptoms.
5. Add the sky-wound only if the user also wants the Cracking visible and the
   composition has real sky space.
6. Keep the effect subordinate to weather, materials, character, and survival.
