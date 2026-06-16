# Rimevegr prompt addons library

This document expands the core prompt framework into a large modular addon system. It is meant for an AI that will assemble final prompts, not for one-shot direct image generation by a human.

Use this library by combining:

1. one base template from the core template file
2. one character addon or one event addon
3. one location or terrain identity
4. one system driver if the scene is about process, pressure, or world logic
5. one grading family or emotional overlay from the cinematic color system
6. one small set of survival details

Do not stack too many addon blocks at once.

---

## Environmental pressure addon library

These add-ons are opt-in. Do not apply them unless the user has explicitly
asked for Veil presence or for the Cracking to be visible.

Pick one Veil intensity only. Use 2 to 4 symptoms, not every effect at once.

### No Veil addon

Use for the default state of the world.

Prompt addon:

> no supernatural distortion, only harsh cold weather, material hardship, and grounded frontier realism

### Veil level 1 — trace presence

Use for a faint brush of wrongness.

Prompt addon:

> a thin grey-white rime haze close to the ground, distant edges softening too early, a hint of recent silence, subtle unease without overt supernatural display

### Veil level 2 — atmospheric pressure

Use when the scene should feel wrong but still mostly ordinary.

Prompt addon:

> grey-white rime-mist pooling around stones and low ground, swallowed landmarks, muted depth, visible breath in sudden cold, one slightly wrong shadow angle, grounded dread

### Veil level 3 — active distortion

Use when reality is visibly strained.

Prompt addon:

> distance behaving unreliably, multiple weak light angles from impossible directions, pale corpse-lights at dusk, characters losing orientation, the air heavy with pressure and watchfulness

### Veil level 4 — focused attention event

Use for the strongest live-action-safe Veil presence.

Prompt addon:

> near-total silence, abrupt freezing pressure, animals already fleeing, fog almost forming faces that never resolve, body language showing that something unseen is actively watching

### Veil level 5 — edge-of-collapse

Use only when the user explicitly wants severe surreal reality-bending that still stays grounded.

Prompt addon:

> a subtly flattened horizon, repeated stone or tree lines, passages reading slightly too narrow or too deep, frost forming without wind, severe reality strain without any portal or spell spectacle

### Hush variant — death echo

Use for battlefields, plague sites, shipwreck remains, and old massacre ground.

Prompt addon:

> muffled air over a death-soaked place, weighted stillness, ash-sunk quiet, the world pressed down by old memory rather than flashy magic

### Cracking sky-wound addon

Use only for wide exteriors and panoramas.

Prompt addon:

> high in the cloud deck, faint broken-vein scar lines and a pale wounded sun with no warmth, distant evidence of a damaged sky rather than a magical spectacle

---

## Character addon library

Choose one primary role, then optionally one secondary role or status cue.

## Authority and hall-power characters

### Jarl

Use for:

- hall portraits
- court scenes
- receiving petitions
- feast leadership

Visual markers:

- high seat near the fire
- better wool and fur trim, but still weathered
- silver arm-rings or brooches
- named sword or better axe
- bodyguards or house-karls nearby

Prompt addon:

> regional jarl of the Rimevegr, seated with practical authority rather than royal splendor, weathered fur-trimmed cloak, silver arm-rings, guarded by trusted huskarls, hall politics visible in posture and seating order

### Overjarl or war-chief

Use for:

- military command images
- levy musters
- iron-road power scenes

Visual markers:

- heavier escort
- more militarized hall or yard
- banners are crude and practical, not heraldic pageantry
- patrol routes, iron, and discipline dominate the frame

Prompt addon:

> hard northern war-chief or overjarl, rule expressed through armed discipline, iron posts, patrol presence, war-worn authority, expansion and control rather than ceremonial kingship

### Headman or elder

Use for:

- village negotiation
- local judgment scenes
- receiving travelers

Visual markers:

- strong but modest clothing
- no regal luxury
- weathered authority through age, posture, and local respect
- seated near the entrance or law-stone rather than on a throne

Prompt addon:

> village headman or elder, practical local authority trusted to deal with armed strangers, heavy wool layers, work-worn hands, cautious hospitality, status shown through respect rather than wealth

### Reeve or steward

Use for:

- tax or storehouse scenes
- settlement management
- meeting merchants or band captains

Visual markers:

- tally sticks, keys, scales, wax tablets, small purse
- better boots and cleaner cloak than ordinary villagers
- anxious, competent expression

Prompt addon:

> reeve or steward managing stores and obligations, carrying keys scales or tally sticks, practical middle-ranking authority, part administrator and part survivor

### Harbour-master

Use for:

- dock logistics
- port control
- ship repair and toll scenes

Visual markers:

- salt-stiff cloak
- rope, hooks, cargo markers, jetty posts
- practical command of boats and workers

Prompt addon:

> harbour-master of a hard fjord settlement, salt-weathered and logistical, ruling by berth space repair access and dockside control, rope and pitch and iron tools all around

### Lore-keeper or archive master

Use for:

- Skaldhaven scenes
- relic handling
- written memory or lineage scenes

Visual markers:

- layered cloak, careful hands, scrolls or rune rubbings
- bone, ink, seals, shelving, carved record stones
- not a wizard, but a custodian of memory

Prompt addon:

> lore-keeper of the Rimevegr, guardian of sagas relics and names, severe learned presence, cliffside archive culture, memory treated as a political resource

### Widow power broker

Use for:

- influential women in authority
- side-pressure politics
- intelligence and debt scenes

Visual markers:

- controlled clothing quality
- keys, store access, or household control symbols
- calm expression stronger than visible force

Prompt addon:

> powerful widow ruling through grain silver rumor and measured intelligence, practical household authority turned political force, no softness and no theatrical villainy

### Huskarl or house-karl

Use for:

- gate scenes
- hall discipline
- bodyguard shots
- feud intimidation

Visual markers:

- professional shield and spear
- better-maintained iron than ordinary levy men
- disciplined stance and direct eye-line

Prompt addon:

> household huskarl, disciplined professional guard of a jarl's hall, practical iron helm, round shield, trained posture, paid loyalty rather than heroic swagger

---

## Free folk and working characters

### Bondi or karl farmer

Use for:

- daily village life
- field and storehouse scenes
- survival economy images

Visual markers:

- rough wool and work dirt
- grain pits, wood piles, broken tools, livestock
- tired competence

Prompt addon:

> free farmer of the Rimevegr, practical bondi household backbone, smoke-smelling wool, cracked hands, small reserves of grain and wood, survival measured in stores and labor

### Landless drifter

Use for:

- roadside scenes
- recruitment scenes
- bleak social mobility images

Visual markers:

- free but poor
- patched kit with few possessions
- wary, hungry, mobile

Prompt addon:

> landless drifter between settlements, free but rootless, all possessions carried on the body, hungry caution, the kind of person who becomes a laborer thief or mercenary depending on the week

### Fisher

Use for:

- fjord labor
- dock economy
- weather hardship

Visual markers:

- wet rope hands
- leaking boat, nets, fish sheds, oil smell
- cold spray and stiff clothing

Prompt addon:

> fjord fisher hauling survival from black water, numb hands, leaking boat, net weights and fish racks, harsh coastal labor rather than romantic seafaring

### Shepherd or drover

Use for:

- Thornwall scenes
- moor travel
- wool and mutton economy

Visual markers:

- crook, rope, dogs, wet wool, flock pressure
- thorn hedges, peat stacks, low visibility

Prompt addon:

> moor shepherd or drover, practical keeper of sheep through wind and peat, thorn-hedge country, wool trade survival, small stubborn competence against open cold land

### Smith or craft worker

Use for:

- workroom scenes
- Deepholm or village industry
- production-system images

Visual markers:

- soot, burn marks, iron bloom, hammer rhythm
- no ornate fantasy forge
- cramped, practical labor space

Prompt addon:

> frontier smith or metal-worker, soot-dark and labor-heavy, making repairs that keep a settlement alive, iron as necessity rather than artistry alone

### Charcoal burner or tar worker

Use for:

- forest industry scenes
- Vargheim and Ashmark identity

Visual markers:

- smoke-dark clothing
- blackened hands
- stacked timber, charcoal clamps, resin, tar pits

Prompt addon:

> charcoal burner or tar worker of the black pine, smoke-soaked laborer from a deep forest economy, resin and ash and controlled fire shaping daily life

### Trader or market seller

Use for:

- market day
- dockside exchange
- barter scenes

Visual markers:

- scales, cloth bundles, jars, hooks, cut silver, hack-silver
- guarded expression
- wares displayed as hard value, not colorful abundance

Prompt addon:

> northern trader in a poor hard market economy, scales and hack-silver and barter goods, suspicion and necessity in every exchange, no rich medieval fair atmosphere

### Healer or midwife

Use for:

- domestic authority
- wound scenes
- quiet village interiors

Visual markers:

- herbs, cloth wraps, bowls, thread, practical calm
- not robed mysticism
- exhaustion and usefulness

Prompt addon:

> healer or midwife of the Rimevegr, practical knowledge under pressure, herbs and bandages and hearth tools, respected because people need her, not because the world is kind

### Ferryman, watchman, or lighthouse keeper

Use for:

- boundary scenes
- night watch
- passage control

Visual markers:

- isolation, rope posts, fire basket, wet planks, edge-of-land atmosphere
- grim endurance and boredom sharpened by danger

Prompt addon:

> isolated ferryman or cliff watchman at the edge of a dangerous route, minor authority built on local necessity, cold wind and poor light and uncelebrated duty

### Skald

Use for:

- feast scenes
- recitation scenes
- cultural memory moments

Visual markers:

- speaking posture, cup or harp substitute, attentive hall
- less minstrel glamour, more sharp social intelligence

Prompt addon:

> skald performing memory law and mockery in a live hall, socially dangerous poet with a hard-earned place near power, voice treated like a blade

---

## Unfree, marginal, and dangerous characters

### Thrall

Use for:

- class contrast
- labor scenes
- feast cleanup or yard work

Visual markers:

- cast-off clothing worn thin at elbows and knees
- farthest from warmth and status
- burdened posture and practical silence

Prompt addon:

> thrall in the Rimevegr, unfree and debt-bound or captured, wearing cast-off wool and rough work clothes, serving at the edge of firelight, dignity reduced but not erased

### Freedman or ex-thrall

Use for:

- transition status scenes
- mercenary recruitment
- earned-hardship portraits

Visual markers:

- still poor but carrying self-ownership with tension
- one better piece of gear earned through service

Prompt addon:

> freedman or ex-thrall clawing into free status, still marked by labor and scarcity, one hard-won sign of independence, wary pride and no safety net

### Outlaw or wolfshead

Use for:

- forest terror
- night approach scenes
- border danger

Visual markers:

- harsh improvised gear
- stolen layers, territory marks, raw menace
- hunted and predatory at once
- default attractiveness_scale should be locked to -2

Prompt addon:

> wolfshead outlaw of the Rimevegr, expelled from law and kin order, improvised gear and hard eyes, the land has made him feral without making him supernatural

### Raider or bandit

Use for:

- settlement alarm scenes
- road ambush frames
- tribute and fear imagery

Visual markers:

- practical weapons and winter opportunism
- no glamorous pirate styling
- hunger and violence as economics

Prompt addon:

> hard northern raider or road bandit, poverty-driven violence, practical stolen gear, opportunistic brutality, no heroic saga romance

### Berserker or fury-drunk warrior

Use for:

- rare high-intensity scenes
- Thurr-linked dread

Visual markers:

- fearsome physical tension
- damaged hands, broken-knuckle feel
- terrifying human extremity, not monster design

Prompt addon:

> rare berserker in a human-scale killing fury, terrifying because he is still a man, not a beast or demon, violence outstripping reason in a grounded world

---

## Mercenary-band characters

### Mercenary captain

Use for:

- command portraits
- negotiation scenes
- march leadership

Visual markers:

- scarred competence
- little wasted motion
- better iron but still practical
- the band arranged around trust and fear

Prompt addon:

> mercenary captain of a Svarthird, hard competent authority built on survival arithmetic, weathered practical iron, face marked by old campaigns, commands by economy rather than speech

### Sergeant or ledger-keeper

Use for:

- pay ritual
- camp management
- internal politics scenes

Visual markers:

- purse, ledger, charcoal, knife, ration awareness
- thick hands and counting habit

Prompt addon:

> sergeant and quartermaster keeping the band's true law through coin and ration count, charcoal ledger at hand, practical authority expressed through arithmetic and memory

### Named veteran

Use for:

- close portraits
- group scenes with hierarchy
- old campaign weariness

Visual markers:

- individualized scars and habits
- reliable kit, not flashy richness
- the expression of someone who has survived too much

Prompt addon:

> named veteran of the Black Hird tradition, individually weathered gear and earned reputation, old wounds carried like inventory, competence heavier than bravado

### Common axe-man

Use for:

- rank-and-file band scenes
- marching or camp tasks

Visual markers:

- mixed kit quality
- practical axe, shield, pack, bedroll
- not yet mythic, simply useful

Prompt addon:

> common axe-man in a mercenary band, ordinary but hardened, patched wool and basic iron, one more body in the column whose value is measured daily

### Scout or skirmisher

Use for:

- forest movement
- flank watch
- ridge observation

Visual markers:

- lighter kit
- sharper attention to terrain and tracks
- quiet motion rather than posing

Prompt addon:

> skirmisher or scout moving ahead of the band, lighter gear, track-aware posture, practical stealth shaped by forest and moor rather than fantasy assassin aesthetics

### Shield-maiden or woman fighter

Use for:

- mixed company scenes
- competence under pressure

Visual markers:

- practical equipment equal to function
- not fetishized armor
- confident but unsentimental body language

Prompt addon:

> shield-maiden of the Rimevegr, treated as another proven fighter rather than a symbol, practical shield and spear work, cold-weather realism and earned presence

### Camp cook or field healer

Use for:

- stew scenes
- camp survival
- wound care

Visual markers:

- pot, cloth, knives, herbs, heat management
- everyone depends on them

Prompt addon:

> camp cook and practical healer at the center of a mercenary fire-circle, stew pot and hard choices and herbal knowledge, the band's survival held together by unglamorous labor

### Weak link or burdened porter

Use for:

- tension within the band
- survival math scenes
- column movement images

Visual markers:

- extra weight carried
- poorer footing or hesitation
- watched by veterans with flat judgment

Prompt addon:

> the weak link in a mercenary column, tolerated only while still useful, overloaded with gear, anxious under the eyes of harder men, survival pressure visible in every posture

---

## Sacred, magical, and uncanny characters

### Volva or seidr-wife

Use for:

- trance scenes
- prophecy images
- Veil-edge ritual moments

Visual markers:

- women-centered spiritual authority
- staff, thread, bone, cloth, trance posture
- feared respect rather than fantasy sorceress glamour

Prompt addon:

> völva or seidr-wife of the Rimevegr, feared and respected spirit-worker, trance-bound and severe, authority coming from knowledge of the dead and the Veil rather than spectacle magic

### Galdr-worker or rune-carver

Use for:

- ward making
- rune investigation
- craft-magic crossover scenes

Visual markers:

- knife, chisel, carved wood or stone, sleepless focus
- bodily cost and concentration
- practical workspace

Prompt addon:

> galdr-worker or rune-carver practicing costly warding craft, carved signs and breath-spoken activation, practical magic treated like dangerous labor rather than wizardry

### Wyrd-reader

Use for:

- omen scenes
- fatalist portraits
- quiet divination images

Visual markers:

- lots, marked bone pieces, attentive silence
- the face of someone reading odds and doom

Prompt addon:

> wyrd-reader feeling the pressure of fate in a practical world, divination through old signs and hard silence, no grand prophecy spectacle, only costly glimpses

### Rope-reader

Use for:

- Odynn-linked temple scenes
- oath or pain wisdom imagery

Visual markers:

- rope beam, crow feathers, cold stone temple, severe restraint
- ascetic, unsettling presence

Prompt addon:

> rope-reader priest of Odynn's silence, austere and severe in a cold temple, rope beam and crow-feather symbolism, faith surviving after certainty has died

### Dry-Eyed priestess

Use for:

- grief rites
- women-centered temple scenes
- post-sacred endurance images

Visual markers:

- temple cold, no fire, names of the dead, distaff and skull motifs
- grief without melodrama

Prompt addon:

> Dry-Eyed priestess serving grief and endurance, hard feminine ritual authority in a world of silent gods, sorrow made practical and communal rather than sentimental

### Barrow-keeper

Use for:

- funeral boundaries
- grave-edge scenes
- death stewardship imagery

Visual markers:

- half-sod hut, pebbles, tools, barrow stones, bone bowls
- lonely responsibility

Prompt addon:

> barrow-keeper at the edge of the dead, solitary caretaker of grave fields and old boundaries, ritual duty performed with no illusion that the work is safe

### Scar-mouth or Lopt-linked truth speaker

Use for:

- fringe religion scenes
- unsettling hall or alley moments
- social discomfort imagery

Visual markers:

- lived-in roughness, unsettling directness, negative space, hidden corners
- more human discomfort than occult grandeur

Prompt addon:

> scar-mouth figure from the margins of settlement life, unsettling truth-speaker associated with hidden corners and dangerous honesty, uncanny by behavior rather than costume excess

---

## Event and scene addon library

Choose one main event driver per image.

### Thing assembly or allthing

Prompt addon:

> thing-assembly in session, law-stone or cleared gathering ring, disputes weighed publicly under cold light, free men speaking by rank, judgment enforced by local power rather than divine certainty

Key elements:

- gathered free folk
- jarl or host authority
- law-stone, ring, dockside yard, or hall forecourt
- tension more than spectacle

### Weregild negotiation

Prompt addon:

> blood-price negotiation between households, silver weighed and grief contained in public ritual, law and threat existing side by side in the same cold space

Key elements:

- scales or hack-silver
- controlled rage
- kin witnesses

### Oath-swearing scene

Prompt addon:

> hard oath sworn before witnesses on stone iron or pain, contract gravity visible in faces and body language, a world where trust is social law and breaking it ruins lives

Key elements:

- hand cut or clasp
- rope-and-eye mark
- law-stone or contract stone

### Guest-right negotiation

Prompt addon:

> arrival of armed strangers at a settlement under guest-right negotiation, ale price and boundaries set before weapons are put aside, wary hospitality with a caloric limit

Key elements:

- gate or hall threshold
- measured politeness
- terms before comfort

### Meeting the jarl

Prompt addon:

> tense meeting with a regional jarl inside a smoky hall, rank revealed by seating and silence, the visitor judged as much by usefulness as by words

Key elements:

- high seat
- bodyguards
- hierarchy in the room

### Hiring the band or contract negotiation

Prompt addon:

> mercenary contract negotiation in a poor hard frontier world, silver terms weighed against risk, damp cloaks and guarded faces, survival arithmetic visible in the scene

Key elements:

- purse or measured payment
- map, route, or danger discussion
- no cheerful adventurer tavern tone

### Pay ritual or ledger-stone scene

Prompt addon:

> weekly pay ritual at camp, sergeant on a flat stone with purse and ledger, each fighter stepping forward for counted copper, hierarchy made visible through order and silence

Key elements:

- charcoal ledger
- small knife in wood
- line of waiting men

### Market trading scene

Prompt addon:

> hard northern market day, barter and weighed silver moving between practical hands, wool fish iron salt and grain exchanged under suspicion and necessity, no colorful festival abundance

Key elements:

- scales
- rough stalls
- bundled goods
- guarded faces

### Harbour loading or fjord trade scene

Prompt addon:

> fjord trade in motion, boats and cargo and net sheds under cold coastal weather, logistics and survival more important than romance or adventure

Key elements:

- jetty
- rope and barrels
- fish oil or sailcloth
- harbour-master oversight

### Longhall feast

Prompt addon:

> political feast in a smoky longhall, seating order as quiet negotiation, bread stew and meat served by rank, toasts and boasts shaping future trouble, realism over fantasy revelry

Key elements:

- high fire
- table pounding
- skald presence
- house-karls breaking tension if needed

### Skald recitation or mockery verse

Prompt addon:

> skald performing before a live hall where verse can honor ruin or start a feud, the room reading every word as memory law entertainment and weapon at once

### Village labor day

Prompt addon:

> communal labor scene in a harsh settlement, wood splitting net mending wool work and fence repair all happening under poor weather, survival shown as constant shared effort

### March on the road

Prompt addon:

> mercenary column on a hard route through the Rimevegr, pace shaped by weather terrain and carried weight, practical fatigue and long-road silence dominating the frame

### Watch in the Hush

Prompt addon:

> night watch during the Hush, all sound fallen away, guards holding still in unnatural silence, fear carried through posture and listening rather than visible monsters

### Temple rite or sacrifice

Prompt addon:

> short cold rite before silent gods, stone temple or sacred site with no comforting warmth, offerings and witnesses present, faith continuing because the alternative is worse

### Seidr working

Prompt addon:

> seidr ritual in a human and dangerous register, trance breath, thread bone and whispered dead, bodily cost visible, no spell-flare spectacle

### Galdr ward-laying

Prompt addon:

> ward-making by carved runes and spoken activation, dangerous craft under strain, practical materials and bodily exhaustion, magic treated like skilled labor with a price

### Funeral or barrow burial

Prompt addon:

> Norse frontier funeral in a post-sacred world, the dead honored with ritual gravity, cold earth or barrow-edge setting, grief expressed through duty and witness rather than theatrical mourning

### Barrow approach

Prompt addon:

> armed approach to a restless barrow, caution and cold dread leading the composition, old stones and wrong quiet suggesting danger before anything overt is seen

### Aftermath of violence

Prompt addon:

> aftermath of a raid fight or barrow clearing, survivors and scattered gear under bad weather, the true subject is cost, not triumph

---

## System illustration packs

These are not just scenes. They are domains of life that may each need 2 to 3 illustrations to explain how the setting works.

## Travel and route system

Suggested illustration set:

1. route planning beside a fire, map-stone, or road marker
2. the band crossing a specific terrain under real weather pressure
3. arrival exhausted, hungry, and diminished by the road itself

Prompt addon:

> travel in the Rimevegr as contract math, route choice, shelter scarcity, foraging pressure, and physical cost made visible in bodies gear and terrain

## Economy and barter system

Suggested illustration set:

1. market exchange using scales and hack-silver
2. village storehouse or granary showing invisible wealth
3. payment scene where silver, food, and labor stand in for abstract money

Prompt addon:

> economy of contraction and scarcity, where coin is worn smooth and barter fills the gaps, wealth measured in stores tools firewood and survival margin rather than luxury display

## Social rank and hall order system

Suggested illustration set:

1. hall seating by status
2. jarl versus karl versus thrall in one frame
3. a visitor reading the room before speaking

Prompt addon:

> social hierarchy visible from across a room, rank expressed by seating food clothing and who speaks first, no need for crowns or courtly pageantry

## Law and justice system

Suggested illustration set:

1. thing assembly at the law-stone
2. weregild settlement or dispute hearing
3. oath-swearing and witness scene

Prompt addon:

> law in the Rimevegr as public negotiation backed by force and memory, justice surviving without divine certainty, every ruling dependent on who can enforce it

## Religion and sacred-life system

Suggested illustration set:

1. stone temple interior with god-post and no fire
2. local rite or offering performed by weathered people
3. barrow-edge sacred duty scene

Prompt addon:

> post-sacred religion in a cold world where ritual continues after certainty died, severe sacred spaces, communal endurance, and silence where answers should be

## Magic and bodily-cost system

Suggested illustration set:

1. galdr-worker carving and activating runes
2. völva in trance or recovery
3. aftermath showing the physical toll of a magical act

Prompt addon:

> Norse magic as a dangerous craft with bodily cost, rare feared and practical, never clean or spectacular, always taking something from the user or the land

## Mercenary band-life system

Suggested illustration set:

1. pay ritual and ration counting
2. fire-circle with maintenance and grievances
3. band on the move with hierarchy made visible

Prompt addon:

> mercenary life as a moving ledger wrapped in wet wool and iron, loyalty tied to food pay warmth and hard competence rather than ideals

## Weather and season system

Suggested illustration set:

1. Long Summer mud haze insects and weak brightness
2. Long Dark blue-grey cold with deep rime and short light
3. a weather event such as rime-fog or driving snow overtaking a route

Prompt addon:

> environment as a daily enemy, seasons changing movement morale and survival, cold and damp treated as structuring forces rather than atmospheric decoration

## Settlement-fabric system

Suggested illustration set:

1. hamlet or village fabric from outside
2. productive work zones like sheds, smithies, jetties, or byres
3. defensive edge such as hedge, palisade, ditch, or gatehouse

Prompt addon:

> settlement life built from longhouses byres sheds store pits jetties and palisades, every structure carrying labor, defense, and winter logic

## Politics and faction-pressure system

Suggested illustration set:

1. diplomacy in a hall or guesthouse
2. patrol or tribute pressure on the road
3. market or chokepoint control as politics made physical

Prompt addon:

> local politics as control of roads grain armed men and trade flow, factions defined by what they can keep moving or stop moving in winter

## Barrows, dead, and Veil-pressure system

Suggested illustration set:

1. sealed or waking barrow exterior
2. first approach or entry moment
3. aftermath showing the land changed by proximity to the dead

Prompt addon:

> barrow pressure changing the land itself, temperature drop corpse-lights wrong silence and old wards failing, dread built through environment and consequence rather than monsters alone

---

## Fast combination patterns

Use these when the AI needs quick assembly logic.

### Character portrait pattern

- one role addon
- one status cue
- one background hint
- one texture detail

### Event scene pattern

- one event addon
- one location identity
- two survival details
- one crowd or hierarchy cue

### System explanation pattern

- one system addon
- 2 to 3 illustration variants
- one recurring environmental pressure
- one material-culture anchor

### Montage pattern

- one close human frame
- one mid-action frame
- one wide environment frame
- keep palette and weather consistent across all panels

---

## Universal negative guardrails for this addon library

Avoid unless the prompt explicitly demands otherwise:

- horned helmets
- ornate fantasy plate armor
- bright color splashes without local material reason
- glamorous wizard robes
- castles and grand stone cities outside the canonical settlement scale
- epic heroic battle posing
- clean modern grooming
- generic Viking-tourism imagery
- magical glow overload
- the Veil in scenes that are not veil-touched
- the Cracking in shots with little visible sky
