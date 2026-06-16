# Rimevegr cinematic color system

This document is a deep prompt-addon reference for cinematic color grading, scene filters, and emotional lighting language in the Rimevegr. It is designed for an AI that writes final image prompts.

The goal is not to apply one universal dark-blue look. The goal is to keep the world recognizably Rimevegr while letting different scenes breathe, hurt, warm, rot, harden, or threaten in different ways.

Use this system together with the core template and the prompt addons library.

---

## Core grading principle

Every scene should feel like it belongs to the same live-action universe, but not the same exact frame.

Hold constant:

- grounded live-action realism
- restrained saturation
- practical materials
- cold-weather logic
- emotional seriousness

Vary aggressively:

- temperature balance
- contrast softness or hardness
- where the small warm accents sit
- how much color survives in the frame
- whether the environment compresses or opens space
- whether the image feels communal, lonely, brutal, grief-heavy, uncanny, or dangerous

## The anti-sameness rule for color

Never solve the setting with only one formula such as:

- blue-grey plus fog plus orange fire

That is only one family of looks.

The Rimevegr should rotate between:

- wet coastal steel
- dead overcast bone-grey
- smoke-amber interior warmth
- peat-brown attrition
- pine-green compression
- iron-rust militarism
- chalk-white dread
- frost-blue depression
- wrong-light uncanny conditions

---

## Master palette anchors

These are the recurring building blocks of the world.

| Function             | Colors                                                     |
| -------------------- | ---------------------------------------------------------- |
| cold neutrals        | ash grey, wet stone grey, frost white, iron black          |
| land tones           | peat brown, dead grass straw, weathered bone, muddy umber  |
| low life-color       | muted pine green, algae green, wool brown, smoke tan       |
| human warmth accents | dull skin red, chapped nose pink, dirty amber firelight    |
| hard warning accents | dried-blood rust, forge orange, dull silver glint          |
| uncanny accents      | bleached blue-grey, false aurora green, corpse-light white |

Important rule:

Warmth in the Rimevegr is usually local and temporary. It should read as:

- hearthlight
- lamp glow
- forge flare
- skin against cold
- a cup, ember, or torch

It should not flood the entire image unless the whole scene is intentionally about refuge or feast politics.

---

## Scene-family grading system

Choose one primary scene family before choosing emotional overlays.

## Outdoor grading families

### 1. Fjord steel grade

Use for:

- coastlines
- harbor scenes
- cliffs
- wind and salt exposure

Look:

- steel grey dominant
- cold slate blue in water and sky
- salt-white highlights
- muted rope-brown and tar-black details
- minimal warm accent

Emotional read:

- hard endurance
- exposure
- maritime severity

Prompt addon:

> cinematic fjord-steel grade, cold slate water, salt-whitened air, iron-grey overcast, harsh coastal realism, warmth reduced to tiny local accents only

### 2. Moor ash grade

Use for:

- open moors
- shepherd roads
- standing stones
- attrition scenes

Look:

- ash grey and peat brown dominate
- color drained from distance
- dead grass straw and black water accents
- low, scoured contrast

Emotional read:

- exposure
- loneliness
- slow morale erosion

Prompt addon:

> moor-ash grade, wind-scoured grey light, peat-brown earth, drained horizon, low-color attrition atmosphere, the land swallowing energy and resolve

### 3. Black pine compression grade

Use for:

- dense forest
- hush scenes
- tracking or scouting

Look:

- compressed dark greens and charcoal blacks
- grey-green filtered light
- very limited sky influence
- bark-brown and moss-dark accents

Emotional read:

- claustrophobic attention
- listening tension
- direction lost

Prompt addon:

> black-pine compression grade, grey-green filtered light under a dense canopy, dark resinous shadows, space closing around the figures, grounded dread without overt fantasy glow

### 4. Iron-road militarist grade

Use for:

- Grimholt
- Deepholm approaches
- checkpoints
- tax or force scenes

Look:

- iron grey, slag black, rust orange, dull torch amber
- sharper contrast than village scenes
- practical hard edges

Emotional read:

- discipline
- pressure
- controlled violence

Prompt addon:

> iron-road militarist grade, slag-black surfaces, iron grey structure, restrained rust-orange accents, severe industrial harshness, power shown through material hardness

### 5. Long-summer mud grade

Use for:

- thaw scenes
- labor outdoors
- temporary relief
- growth without joy

Look:

- washed-out daylight
- muddy umber, moss green, weak gold-grey haze
- slightly more living color than Long Dark scenes

Emotional read:

- brief relief
- damp activity
- unstable optimism

Prompt addon:

> long-summer mud grade, pale weak daylight, wet earth and moss tones, subdued green growth, temporary softness without true brightness or comfort

### 6. Long-dark frost grade

Use for:

- winter travel
- exposed settlements
- deep seasonal pressure

Look:

- frost blue, ash grey, dirty white, deep charcoal
- narrow warmth zones only
- clear cold separation between exposed flesh and environment

Emotional read:

- endurance
- depression
- winter control

Prompt addon:

> long-dark frost grade, blue-grey cold dominating the scene, rime-white surfaces, minimal warmth trapped around fire or skin, severe winter realism

### 7. Northern wrong-light grade

Use for:

- Veil-edge
- ice shelf
- first barrow zones
- reality-strain scenes

Look:

- bleached ice tones
- unnatural pale blue-green cast
- multi-source shadow weirdness
- whiteness with dead-space feeling

Emotional read:

- uncanny awe
- dread
- reality thinning

Prompt addon:

> northern wrong-light grade, bleached cold world under unnatural pale blue-green light, wrong shadow behavior, severe realism touched by impossible sky conditions

---

## Indoor grading families

### 8. Hearth refuge grade

Use for:

- safer hall scenes
- domestic warmth
- temporary rest

Look:

- smoke amber and fire gold near the center
- brown-black timber around it
- soft falloff into cold shadow

Emotional read:

- relief
- fellowship
- temporary human warmth

Prompt addon:

> hearth-refuge grade, warm amber firelight held inside smoke-dark timber space, warmth local and fragile against surrounding cold shadow

### 9. Hall politics grade

Use for:

- feast scenes
- meetings with a jarl
- negotiations indoors

Look:

- richer amber than ordinary interiors
- dark wood, red-brown ale tones, silver glints
- corners remain cold and watchful

Emotional read:

- status
- performance
- tension under hospitality

Prompt addon:

> hall-politics grade, richer firelit amber around benches and faces, dark timber and silver accents, warmth serving power and hierarchy rather than comfort

### 10. Poor shelter ember grade

Use for:

- barns
- ruins
- emergency camp interiors
- band misery scenes

Look:

- weak ember orange
- dirty straw brown
- damp shadow swallowing most color
- bodies and gear fading into the dark

Emotional read:

- exhaustion
- low morale
- survival stripped bare

Prompt addon:

> poor-shelter ember grade, weak orange glow fighting damp shadow, muddy browns and dying warmth, exhausted realism of people sleeping because they must

### 11. Temple cold-stone grade

Use for:

- silent-god rituals
- priesthood scenes
- interior sacred dread

Look:

- near-colorless greys
- dead limestone or basalt tones
- almost no warm light
- skin looks pale and blood-starved

Emotional read:

- reverence without comfort
- silence
- post-sacred severity

Prompt addon:

> temple cold-stone grade, severe near-colorless light on stone and earth, warmth almost absent, sacred space defined by cold and silence rather than radiance

### 12. Forge pressure grade

Use for:

- smithy scenes
- Deepholm industry
- repair labor

Look:

- black soot and iron base
- controlled orange flare points only
- hot-cold contrast

Emotional read:

- labor intensity
- function
- force applied to matter

Prompt addon:

> forge-pressure grade, blackened iron world with controlled orange flare from the work itself, intense but practical, labor heat pushing against surrounding cold

### 13. Archive and memory grade

Use for:

- Skaldhaven
- relic rooms
- scribes and lore-keepers

Look:

- dim tallow gold
- faded parchment tan
- old wood and dusty stone
- low-saturation dignity

Emotional read:

- memory
- dignity
- intellectual seriousness

Prompt addon:

> archive-memory grade, low warm lamplight over faded parchment, wood and bone and record stones, muted old-world dignity with no academic luxury

---

## Emotional overlay system

After choosing the scene family, add one emotional overlay.

## Positive or restorative overlays

### Communal warmth overlay

Use for:

- band trust scenes
- shared meals
- moments of belonging

Effect:

- slightly strengthen amber or skin warmth
- keep saturation low
- preserve the cold outside the warm zone

Prompt addon:

> subtle communal-warmth overlay, a little more life in skin firelight and wool tones, warmth shared but fragile, never cheerful fantasy brightness

### Relief after hardship overlay

Use for:

- return to shelter
- safe arrival
- end of a hard march

Effect:

- softened contrast
- slightly more tonal separation between people and environment
- a sense of breath released

Prompt addon:

> relief-after-hardship overlay, the palette loosening slightly after strain, softer contrast and a brief sense of human reprieve without breaking the world’s severity

## Negative or depressive overlays

### Winter depression overlay

Use for:

- hunger scenes
- low morale
- hopeless travel

Effect:

- drain minor warmth from skin and fabric
- flatten midtones
- let whites go dirty and tired

Prompt addon:

> winter-depression overlay, flattened midtones and cold-drained warmth, the world feeling emotionally tired rather than theatrically dark

### Grief overlay

Use for:

- funerals
- aftermath
- widow scenes
- absent-kin images

Effect:

- mute reds heavily
- let grey-bone tones dominate
- keep composition still and air heavy

Prompt addon:

> grief overlay, subdued bone-grey and faded cloth tones, almost no emotional color left in the frame, sorrow carried through stillness rather than melodrama

### Poverty attrition overlay

Use for:

- daily labor
- food shortage
- barter realism

Effect:

- favor wool brown, peat brown, smoke tan, worn iron
- reduce anything that looks luxurious or lush

Prompt addon:

> poverty-attrition overlay, worn practical colors only, the world narrowed to what people can still mend, eat, carry, or burn

## Aggressive or violent overlays

### Pre-battle aggression overlay

Use for:

- muster
- confrontation
- patrol tension

Effect:

- slightly harder contrast
- darken edges
- use rust, leather, and iron accents more strongly

Prompt addon:

> pre-battle aggression overlay, slightly hardened contrast, iron and rust accents carrying tension, violence close but not yet released

### Impact violence overlay

Use for:

- active combat
- berserker scenes
- breaking points

Effect:

- sharpen motion edges
- let mud blood and iron read more distinctly
- avoid comic-book saturation spikes

Prompt addon:

> impact-violence overlay, hard realism of mud blood iron and motion, sharper local contrast without drifting into stylized action spectacle

## Horror and dread overlays

### Quiet dread overlay

Use for:

- barrow approach
- hush scenes
- uncanny routes

Effect:

- desaturate further
- soften horizon clarity
- make negative space feel active

Prompt addon:

> quiet-dread overlay, drained color and softened distance making the air feel watchful, fear carried by silence and space rather than obvious monsters

### Veil dread overlay

Use for:

- veil-touched scenes only

Effect:

- grey-white haze lowers contrast
- edges lose certainty
- soundlessness is implied visually

Prompt addon:

> Veil-dread overlay, grey-white rime-mist muting distance and swallowing sound, contrast lowered in a cold unnatural but still deniable way

### Ritual unease overlay

Use for:

- temple or seidr scenes
- dead-adjacent rites

Effect:

- keep lighting directional and severe
- suppress comfort colors
- let one odd accent feel wrong but faint

Prompt addon:

> ritual-unease overlay, directional severe light, comfort colors suppressed, a faint sense that something old is listening from just beyond certainty

---

## Combination matrix

Use this to avoid repetitive grades.

| Scene type        | Good families                                                | Avoid defaulting to                   |
| ----------------- | ------------------------------------------------------------ | ------------------------------------- |
| fjord trade       | fjord steel, relief after hardship, poverty attrition        | only blue-orange blockbuster contrast |
| jarl in hall      | hall politics, communal warmth, pre-battle aggression        | overly royal gold richness            |
| thrall labor      | moor ash, poverty attrition, poor-shelter ember              | noble heroic lighting                 |
| völva ritual      | temple cold-stone, Veil dread, ritual unease                 | purple magic glow                     |
| market scene      | poverty attrition, long-summer mud, relief after hardship    | cheerful fairground color             |
| funeral           | grief, temple cold-stone, quiet dread                        | dramatic gothic black-red overload    |
| march scene       | long-dark frost, moor ash, winter depression                 | adventure-poster brightness           |
| barrow approach   | quiet dread, Veil dread, black-pine compression              | monster-movie green fog excess        |
| forge or workshop | forge pressure, archive memory, relief after hardship        | high-fantasy molten-orange spectacle  |
| feast             | hall politics, communal warmth, aggression overlay if needed | tavern-fantasy coziness               |

---

## Regional color identities

Use these when you want the image to feel tied to a specific part of the world.

### Frostfjord and western coast

- slate blue
- salt white
- wet black rope
- fish-oil amber
- basalt grey

### Grimholt and the iron road

- iron black
- rust brown
- slag grey
- dim watch-fire amber
- drained wind-light

### Black Pine and Vargheim

- black-green compression
- bark brown
- charcoal grey
- moss-dark shadow
- rare pale mist streaks

### Thornwall and the moors

- ash grey
- peat brown
- thorn darks
- dead straw
- cold wind-whitened surfaces

### Deepholm and industrial gravity

- furnace orange accents
- worked iron grey
- stone-dark interior mass
- copper dullness
- torch soot black

### Skaldhaven and archive culture

- muted tallow gold
- weathered parchment tan
- cliffstone grey
- sea-cold blue outside the room

### Icebreak and the far north

- bleached white
- cold cyan-grey
- false aurora green hints
- deep shadow blue
- black volcanic edge tones

---

## Practical selection algorithm for the AI

When writing a final prompt, choose grading in this order:

1. Choose whether the scene is outdoor or indoor.
2. Choose the region or terrain identity.
3. Choose the time and weather condition.
4. Choose the emotional overlay.
5. Decide where the small warm accents live.
6. Decide whether the Veil is present.
7. Decide whether the Cracking is visible.
8. Remove anything that makes the image look like the exact same scene as the last one.

## Example selection logic

### If the scene is a jarl meeting indoors

Use:

- hall politics grade
- slight aggression or suspicion overlay
- silver, fur, and firelight accents
- no Cracking
- no Veil unless it intrudes from outside

### If the scene is a market on a cold day

Use:

- poverty attrition overlay
- fjord steel or long-summer mud depending on region and season
- more object color variety than a barrow scene, but still restrained

### If the scene is barrow horror

Use:

- quiet dread or Veil dread overlay
- heavily muted palette
- no bright green horror-cliché cast
- maybe one corpse-light or rune-light accent only

### If the scene is a rare positive moment

Use:

- communal warmth or relief overlay
- keep warmth local and earned
- do not suddenly turn the whole world golden and cheerful

---

## Prompt building phrases for color and grading

These can be dropped directly into final prompts.

### General cinematic phrases

- restrained Nordic film grading
- austere desaturated live-action color treatment
- severe prestige historical-fantasy color grade
- grounded natural-light realism with controlled warmth
- weather-heavy tonal realism

### Contrast control phrases

- soft low-contrast distance under overcast
- slightly hardened local contrast around iron and faces
- warmth isolated to firelit skin and timber
- flattened winter midtones
- drained distant background with tactile foreground detail

### Warmth control phrases

- only a thread of amber warmth
- local firelight rather than full-scene warmth
- warmth held close to the body and hearth
- almost no comfort color in the frame

### Uncanny control phrases

- faintly wrong color temperature without fantasy glow
- the air feels cold and incorrect rather than magical
- subtle impossible-light behavior in the far distance
- barely perceptible sky-scars above the cloud deck

---

## What not to do with color

Avoid these failure modes:

- making every scene teal-and-orange
- using heavy blockbuster contrast on quiet scenes
- making horror scenes neon green or blue for no reason
- making all interiors cozy and tavern-like
- making positive scenes sunny and cheerful like a heroic epic
- saturating costume colors beyond what dyed wool would support
- using the same exact grade for fjords, moors, forests, halls, and ice
- turning the Veil into a fantasy color filter instead of a world condition

---

## Fast presets

Use these short add-ons when speed matters.

### Cold severity

> cold-severity grade, ash grey and frost blue dominating, warmth reduced to tiny local accents

### Political warmth under tension

> political-firelight grade, richer amber around faces and benches but cold shadows holding the room tight

### Depressive winter

> depressive winter grade, flattened blue-grey midtones, exhausted cold realism, almost no relief color

### Aggressive iron

> aggressive iron grade, harder contrast, rust and iron accents, force and discipline in the palette

### Quiet supernatural dread

> quiet-supernatural-dread grade, drained tones, softened distance, one faint uncanny accent only

### Fragile communal refuge

> fragile refuge grade, ember warmth held close against a world that remains cold at the edges
