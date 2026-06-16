# Simulation Rendering Guide — Iron Ledger

**Purpose:** Detailed rules for converting every simulation system's
output into prose. The simulation produces numbers, states, and
thresholds. The novel renders them as physical experience,
character behavior, and environmental detail. No number is ever
stated directly. No game term is ever used. The reader learns to
read the band's condition the way Gest reads his ledger — through
observation, not exposition.

> **Cross-reference:** `01_RIMEVEGR_SETTING_BIBLE.md` covers the world
> context (society, economy, law, customs) that simulation
> outputs are rendered within.

**Core principle:** Every simulation output has a _show_ rendering
and a _tell_ rendering. The tell rendering is always forbidden.

---

## Weather

> **Cross-reference:** `weather-as-character.md` extends weather
> states into multi-day story arcs, escalation patterns, and
> supernatural weather (The Hush, Veil-Thinning). This section
> covers the simulation-to-prose rendering table only.

### Named States → Prose Rendering

| State         | Forbidden Tell                    | Required Show                                                                                                                                                                                                                                                            |
| ------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Clear Grey    | "The weather was clear"           | Physical detail: the quality of light, the color of the sky, how far they can see. Cold is still there — clear grey means the wind has teeth.                                                                                                                            |
| Rime-Fog      | "Fog rolled in"                   | Proximity detail: the world shrinks. The man ahead is a shape. Sound carries wrong. Rime on eyebrows, on beards, on shield rims. Things appear and disappear.                                                                                                            |
| Light Rain    | "It started raining"              | Misery detail: everything is wet. Leather darkens. Hands slip. The ground gives. Men hunch. The fire hisses and smokes.                                                                                                                                                  |
| Driving Snow  | "A snowstorm hit"                 | Violence detail: the snow hits sideways. It fills boot-tops. Eyelashes freeze. The trail disappears. Every step is work. An arm goes up against it.                                                                                                                      |
| Rime Storm    | "A terrible storm struck"         | Survival detail: they cannot march. They dig in. The tent fabric cracks like a whip. The world is white noise. Men shout and cannot hear each other at arm's length. Breathing hurts.                                                                                    |
| The Hush      | "Everything went quiet"           | Dread detail: the silence is _wrong_. Not the absence of sound but the presence of listening. Men stop talking. Someone's hand goes to a weapon. Animals are gone. The air tastes of old metal.                                                                          |
| Veil-Thinning | "Something supernatural happened" | Perception detail: the edges of things look wrong. A shadow falls the wrong way. Someone sees something in the treeline that is not there when they look directly. Dalla makes a warding sign. The fire burns blue at the edges.                                         |
| Blood Sun     | "An omen appeared"                | Terror detail: the sun is the wrong color. Red light on snow. Men cannot look at it and cannot look away. Old men say they have seen it before, and they are lying. Something is different about the air — heavier, thicker, as if the sky has dropped a hand's breadth. |

### Weather Modifiers → Prose Behavior

**Forage modifier (0.0–1.1):** Do not render the modifier.
Render the _result_. If foraging yields less, the foragers come
back with less. They look tired. The bags are light. The
forager in charge says a single word: "Nothing," or "Thin."

**Travel modifier (0.2–1.0):** Render through distance-per-day
perception. When travel mod is low, the band covers ground
slowly. "By midday they had not reached the ridge they could see
at dawn." When travel mod is very low (rime storm), they do not
travel. "They stayed."

**Combat modifier (-30 to 0):** Do not render as a penalty.
Render through physical impairment. In driving snow: can't see
the swing coming. In rime-fog: can't tell friend from enemy
until they are close enough to strike. In the hush: the
wrongness of the silence makes men hesitate.

### Frostbite

Never say "he got frostbite." Render through body parts.

- **Onset:** Fingers stop hurting. That is the warning. Then the
  tips go white. The man cannot grip his weapon properly.
- **Established:** Toes swell inside boots. Taking boots off
  reveals dark patches. The skin does not return to color when
  pressed. Walking changes — shorter steps, weight shifting
  away from the damage.
- **Severe:** Blackened extremities. The smell. What the healer
  does with a knife and what it costs to watch.

### Season Rendering

**Long Summer (days 1–60):** The light is wrong for men from
the south — too long, never fully dark. Mud instead of ice.
Different exhaustion. Green things grow but nothing is gentle.
The land is thawing and what emerges from the thaw is not
always welcome.

**Long Dark (days 61–360):** Short sentences. Cold details. The
weight of grey sky. Night comes early and stays. The world
contracts. Fire matters more. Every scene carries the cold as
a physical presence — it is not backdrop, it is antagonist.

---

## Food and Foraging

> **Cross-reference:** `tension-and-stakes.md` § Supply Countdown
> covers how food scarcity creates narrative tension and its
> interaction with other tension sources. This section covers
> the simulation-to-prose rendering for food states.

### Supply States → Prose Rendering

| Days Remaining | Narrative Effect                                                                                                                                                                                        |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 7+ days        | Food is not mentioned. It is there. The men eat.                                                                                                                                                        |
| 4–6 days       | Gest mentions it. A number said once, to Voss. Portions are measured. Dalla serves carefully.                                                                                                           |
| 2–3 days       | The men notice. Complaints. The stew is thin. Someone eats their portion too fast and stares at others eating. Arguments start over who gets the heel of bread.                                         |
| 1 day          | Urgency is physical. The band moves toward food or toward a settlement. Every decision is filtered through the supply count. Voss takes a contract he would not otherwise take.                         |
| 0 (deficit)    | The band is starving. Render through bodies. Men slow down. Tempers shorten. The weakest look grey. Someone collapses on the march. Morale drops and the drop is visible — men do not meet Voss's eyes. |

### Foraging Results → Prose Rendering

**Good forage (surplus):** The foragers come back before
expected. Full bags. Someone found a stream with fish. The camp
smells of cooking. Men are briefly something less than miserable.

**Thin forage (near-zero yield):** The foragers come back late.
The bags are light. Roots. Bark stripped from birch. Something
that might be edible mushroom. The forager in charge gives a
report that is one word: "Sparse."

**Failed forage (zero):** The foragers come back with nothing.
It happens and the men know what it means. That night the stew
is thinner. Gest adjusts a number in his ledger and does not
show it to anyone.

### Terrain and Food

Render terrain quality through foraging difficulty, not through
description of flora:

- **Coast/fjord:** There are things to catch. Render through
  the labor of catching them — nets, tide-pools, the cold water.
- **Forest:** Game exists but is wary. Render through tracking,
  the stillness required, the time it takes.
- **Moors:** There is almost nothing. Render through the
  forager's face when he returns. The flatness of the land that
  offers nothing to eat and nowhere to hide.
- **Ice:** There is nothing. Render through absence. The land
  is white and empty and the word "food" starts to weigh
  differently.

---

## Morale

### Morale Levels → Character Behavior

| Level | Name     | Forbidden Tell               | Required Show                                                                                                                                                                                                                                          |
| ----- | -------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 5     | Keen     | "Morale was high"            | Men sing on the march. Someone tells a joke that is not cruel. Weapons are oiled voluntarily. The camp is orderly because the men choose it.                                                                                                           |
| 4     | Steady   | "The men were fine"          | Professional behavior. Orders followed without repetition. The fire watch stays awake. Men repair gear in the evening. Complaints are specific and reasonable.                                                                                         |
| 3     | Shaken   | "Morale dropped"             | Shorter answers. Longer silences at the fire. The watch needs checking. Someone sleeps through their turn and nobody reports it. Tasks are done, but slowly, and with effort.                                                                          |
| 2     | Wavering | "The men were restless"      | Men cluster by loyalty, not by task. Conversations stop when Voss approaches. Someone is missing in the morning — not deserted, just absent, found an hour later staring at nothing. Gest counts heads more often. The fire watch needs posting twice. |
| 1     | Broken   | "The band was falling apart" | Desertions. Open refusal. Two men fight over a blanket. Someone says the words "this isn't what I signed for" and means it this time. Voss has to decide what giving an order costs if it might not be followed.                                       |

### Morale Events → Prose Moments

**Positive events** are rendered as relief, not celebration.
Mercenaries do not celebrate. They _ease_. The tension drops
one degree. Someone sits down who has been standing for hours.

| Event               | Rendering                                                                                                                                                           |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Won engagement      | Brief satisfaction. Men check the dead for useful gear. Not triumph — relief that this one is over. Someone says "that's done" and means more than the fight.       |
| Paid on time        | Gest handles the silver. The men count theirs. For a night, the arithmetic works. Men buy ale if there is ale to buy. Trust is restored — not spoken, just present. |
| Secured winter hall | The weight comes off. Roof over head. Walls against wind. Men claim sleeping spots with the seriousness of land disputes.                                           |

**Negative events** are rendered through behavioral shifts:

| Event              | Rendering                                                                                                                                                       |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Heavy casualties   | Silence where there used to be voices. Gear piled from the dead. Someone picks up a dead man's knife and nobody says anything about it. The line is shorter.    |
| Late pay           | The question that is not asked. Men look at Gest adding numbers. The trust account has a withdrawal pending.                                                    |
| Captain broke oath | The thing that changes everything. Render through the Named Men first — they knew the oath, they witnessed it. Their silence is louder than the commons' anger. |
| Named Man killed   | A name that nobody says for a while. Then someone says it at the fire, testing whether the wound has scabbed. Sometimes it has. Sometimes it has not.           |

### Grievance System → Dialogue Scenes

Grievances surface as confrontations. The Named Man who has a
grievance does not say "I have a grievance." He says the thing
directly. "You said we'd be paid by Ashfall." "Bjorn is dead
because of that crossing." "I'm asking once."

Voss resolves grievances through what he says and what he does
after. The resolution check is rendered as social pressure —
whether the rest of the band accepts Voss's answer.

### Loyalty → Long-Term Character Behavior

Loyalty 5 (Blood-bound): The man follows Voss into a fight he
thinks they will lose, and does it without comment.

Loyalty 3 (Professional): The man does his job. He does not
volunteer. He does not stay awake to keep Voss company. When
asked for extra effort, he weighs the cost.

Loyalty 1 (Ready to leave): The man tests boundaries. Late to
muster. First to eat. Last to volunteer. When given an order,
there is a pause before compliance that is just long enough to
be noticed.

---

## Combat

> **Cross-reference:** `combat-to-prose.md` covers the full
> fight-scene prose conversion pipeline, blow-by-blow structure,
> and the 70/30 consequence-to-action ratio. This section covers
> the simulation rendering tables only.

### HEMA Stances → Body Language

> Canonical stance rendering table is in `combat-to-prose.md`
> § Stances. Four stances: Aggressive (Vom Tag), Balanced
> (Pflug), Defensive (Ochs), Low Guard (Alber). Never name
> the stance — render what the body does.

### Maneuvers → Physical Actions

> Canonical maneuver rendering (12 maneuvers) is in
> `combat-to-prose.md` § Maneuvers. Never name the maneuver
> — render the physical action and its sound/impact.

### Conditions → Physical Experience

| Condition | Rendering                                                                                                                                                               |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Prone     | On the ground. Scrambling. Looking up at a weapon coming down. The mud, the dirt, the view from below. Getting up takes time that the other man uses.                   |
| Staggered | The blow landed but he is still standing. Not right, though. A half-step sideways. Eyes unfocused for a moment. The weapon dips. One hit from becoming something worse. |
| Winded    | Can't breathe right. Mouth open. The weapon feels heavier. Swings come slower. The body is running out of what the fight demands.                                       |
| Dazed     | Head hit. Everything is bright and loud and slightly wrong. He knows he needs to do something but the signal takes longer to travel. Hands are slow.                    |
| Disarmed  | The weapon is on the ground, three feet away. Three feet is a lifetime. The choice: go for it and turn your back, or fight empty-handed.                                |
| Grappled  | Locked. Both men straining. Can't swing, can't break free clean. Breathing hard into each other's faces. The fight has become about leverage and weight.                |
| Bound     | His blade is controlled. He can feel the other man's strength through the steel. Trying to wrench free, trying to redirect, the weapon does not go where he tells it.   |

### Wound Severity → Immediate Cost

> Canonical wound severity table (Scratch through Mortal, five
> tiers) and multi-chapter consequence rendering are in
> `combat-to-prose.md` § Wound Severity. Full mechanical rules
> in `20_SIMULATION_RULES.md` § 5. This section covers prose
> rendering of wounds, healing, and scars.

### Wound Progression → Daily Texture

Wounds are not events. They are ongoing conditions that affect how
a character occupies every scene. Render wounds through daily life,
not just when the wound is mentioned.

**The first day:** Everything hurts. The character moves differently.
Other characters notice. Someone adjusts how they carry the gear
because the wounded man cannot. The leech checks — hands, linen,
the smell of yarrow.

**The first week:** The wound settles into routine. The character
has learned how to move around it. But fatigue comes earlier. Sleep
is bad. Appetite is wrong. The wounded man is slower on the march
and everyone walks at his speed without commenting.

**The second week:** If healing well — the wound itches. The
bandages come off for air and go back on. The character tests the
limb, gently. If healing badly — fever. Dalla talks to Voss in
a tone that means something. The man sweats at night.

**The third week and beyond:** Either the wound is resolving (scab
flaking, new pink skin, stiffness replacing pain) or it is winning
(infection, re-opening, the leech's expression becoming careful).

### Scar Rendering → Permanent Character Texture

Scars are not decorative. They are the record of things that
happened. Render scars through how the character interacts with
them.

- **Fresh scar:** Red, raised, tight. The character touches it
  without thinking. It pulls when the body moves certain ways.
  Other people look at it and look away.
- **Established scar:** White or pink. Part of the face, the arm,
  the body. The character does not notice it. Others have stopped
  noticing it. It comes up only when new people see it, or when
  the weather changes and it aches.
- **Disfiguring scar:** Burns, missing parts, collapsed features.
  The character has adjusted but has not forgotten. Children stare.
  New employers take a moment. The scar is always in the room.

### Incapacitation → Blocked Action

Render incapacitation not as a status effect but as the thing the
character cannot do. The reader sees what is missing.

"He reached for the shield and found his left hand would not close.
The fingers curled partway and stopped, shaking."

"She tried to run. The knee folded after three strides and she went
down on one leg, catching herself with her hands. She got up. She
did not try to run again."

"He spoke but nothing came out except a whistle of air through
the gap where the blow had caught his throat."

### Pain Rendering → Internal Weather

Pain is rendered through the character's relationship with their
body. Never quantify it. Show it through what the character does
and does not do.

- **Mild pain:** The character favors the wounded side. Shifts
  position often. Grimaces when they forget and move wrong.
- **Moderate pain:** The character is slower. Words are shorter.
  Patience is thin. Sleep comes late and leaves early.
- **Severe pain:** The character's world shrinks to the wound.
  Everything else is distant. Conversation is an effort. The
  body demands attention and will not be ignored.
- **Agonizing pain:** The world is the wound. Teeth clenched or
  sounds coming out that the character cannot stop. Sweat.
  Shaking. The loss of dignity that comes with being reduced
  to a body that is failing.

### Weather and Old Wounds

Before a rime storm, old wounds announce themselves. Every veteran
knows the feeling — the deep ache that starts in the knee, the
throb in the old scar, the stiffness in the fingers that got
frostbitten three winters ago. Render through multiple characters
simultaneously noticing. Snorri straightens his back with a sound.
Ubbe rubs his hand. Voss shifts his weight off his bad side. The
new men do not understand yet.

### Healing Scenes → The Leech at Work

Dalla (or whoever provides medical care) is rendered through
competence and economy of movement. The tools. The smell. The
patient's reaction. Never as magic — always as craft.

"She cleaned the wound with water she had boiled and cooled. Cut
away the dead skin with a small knife that was sharper than most
swords in the band. Packed the cavity with honey and moss. Wrapped
it. Told him not to use the arm for a week and knew he would use
it in three days."

### Stamina → Prose Rhythm

Stamina is invisible to the reader as a number. Render through
fight pacing:

- **Full stamina:** Fast exchanges. Aggressive. Pressing. The
  fighters are fresh and the fight is sharp.
- **Half stamina:** The rhythm slows. Longer pauses between
  exchanges. Someone takes a breath. Feet move more carefully.
- **Low stamina (< 1/3):** Winded. The fight becomes ugly.
  Swings are slower and do not recover as fast. The fighter
  leans on something. Guards instead of attacking.
- **Zero stamina:** Cannot attack. Can only cover and wait.
  The other man knows it. The fight becomes one-sided.

---

## Money and the Ledger

### Treasury States → Prose Rendering

| Health                    | Rendering                                                                                                                                                                                          |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Healthy (4+ weeks runway) | Money is not mentioned. Gest records transactions. Supplies are bought without discussion. The arithmetic works.                                                                                   |
| Tight (2–3 weeks)         | Gest mentions the number to Voss. Once. Buying decisions become deliberate. "Can we afford it?" is not asked aloud but is present in how Voss considers options.                                   |
| Critical (< 2 weeks)      | Gest shows the ledger to Voss. The number is specific. Buying stops unless essential. Contract negotiations shift — Voss cannot walk away. The employer knows it or doesn't, and it matters which. |

### Pay Day → Ritual Scene

Pay is rendered as a ritual because it is one. The men line
up. Gest weighs silver. Each man gets his due and checks
it. The transaction is witnessed. It is the contract made
physical — the promise kept in metal.

Late pay is the promise broken. Render through the absence
of the ritual. The day comes and Gest does not set out the
scales. Men notice. They do not ask. The silence asks.

### Currency and Cost

Silver and copper exist in the world. Characters use them.
Prices are mentioned when characters negotiate or buy.
But never as a roster — only in the moment of transaction.

"Twelve silver for the lot." "He paid in copper, all of it
worn thin." "Three silver a week, plus the usual for the
Named Men."

The reader learns prices the way the band learns them —
through what things cost when you buy them.

---

## Contracts

### Contract Lifecycle → Narrative Arc

Every contract is a story. The offer, the negotiation, the
terms, the work, the complications, the payment or the
betrayal.

**The offer:** Comes through a messenger, a meeting, a
tavern conversation. Render the employer's manner — desperate,
arrogant, cautious, lying. The offer tells you about the
employer before Voss decides.

**The negotiation:** Render through what Voss asks for and
what he does not get. The difference between the ask and
the deal tells the reader about power.

**The work:** Whatever the contract requires. Escort, guard,
raid, clear. Render the work as work — physical, tedious,
dangerous. Not quest. Work.

**The complication:** Every contract has one. The thing the
employer did not mention. The rival who shows up. The
weather that changes the plan. The target that fights back
harder than expected.

**The resolution:** Payment or betrayal. Both are rendered
through the ledger — what was promised, what was received,
what the difference is.

### Reputation → How NPCs Treat the Band

Reputation is rendered through how people react when the
band arrives.

- **Unknown (0):** They do not know the name. Nobody
  steps aside. The band is just armed strangers.
- **Known (1):** Someone has heard of them. A look, a
  muttered word. The innkeeper charges fair.
- **Respected (2):** People make room. The jarl's
  steward comes to talk. Offers arrive.
- **Feared (3):** People make room faster. Some doors
  close when the band passes. The offers are better
  but the welcome is colder.
- **Legendary (4–5):** The name precedes them by days.
  When they arrive, it is an event. Everyone has a
  story about them, and most of the stories are wrong.

### Feud → Persistent Consequence

Feud level is rendered through environment:

- **Cold (0):** Normal interaction.
- **Tense (1):** Prices are higher. Someone follows
  them through the market. The door guard asks more
  questions.
- **Hostile (2):** Gates close. They camp outside the
  walls. Supplies must be bought through intermediaries
  who charge double.
- **Blood-feud (3):** Active danger. Render through
  ambush risk, hired killers, the constant checking
  of the road behind.
- **Vengeance (4):** Open war with this settlement.
  The band cannot go there. The settlement is a
  place on the map that means danger.

---

## Settlements

### Settlement Size → Prose Scale

**Hamlet (20–60):** A handful of buildings. Everyone knows
everyone. The band outnumbers the population. When they
arrive, it is an invasion even if they mean no harm. One
building serves as tavern and meeting hall. The headman comes
out because there is no one else to send.

**Village (60–200):** A proper settlement. Smithy smoke.
Children who run when they see armed men. A headman with
authority and a palisade that might hold against a small
raid. The band fits in the village but changes it by being
there.

**Large Village (200–500):** Walls. A gate that can be
closed. A temple. Trade that exists beyond subsistence. The
band is noticed but does not dominate. Officials deal with
Voss as a contractor, not as a force of nature.

**Small Town (500–2000):** Stone walls. A jarl. A market
where prices are set by supply, not by desperation. The
band is one of several armed groups the town has dealt with.
Voss negotiates as a professional with professionals.

---

## Travel

### March Rendering → Physical Experience

Never say "they marched 15 kilometers." Render through time
and terrain.

"They walked until the ridge, then down the other side into
forest that slowed them to half-pace. By the time they made
camp, the hill they crossed at dawn was still visible behind
them."

**Fast march (20+ km):** Good terrain, good weather.
The band covers ground. Render through confidence —
the steady rhythm, the camp made before dark.

**Slow march (10–15 km):** Something is wrong. Terrain,
weather, wounded slowing the column. Render through
frustration — the visible distance that should have been
eaten already.

**Crawl (< 10 km):** Bad terrain plus bad weather.
Mountain in driving snow. Bog in rain. Render through
survival — every step is deliberate, the march is the
enemy.

**No march (0 km):** Storm. They stay. Render through
confinement — the tent, the cold, the men and women
who cannot be anywhere else.

### Hazards → Interruption Scenes

A hazard is a scene inserted into the travel sequence.
It interrupts the march and costs time.

| Hazard                  | Rendering                                                                                                                                   |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Rough surf / tidal trap | The coast turns hostile. Water where there was path. Wet gear, cold bodies, time lost waiting for the tide.                                 |
| Rockslide / cliff face  | The path is gone. Rubble. Climbing. The pack mule refuses. Time lost finding a way around or through.                                       |
| Fallen trees / bog      | The forest fights them. Cutting through or sinking in. Green things that grab at legs. Swearing.                                            |
| Fog lost                | They walk in circles. The landmarks are gone. The world is grey in every direction. Someone finally admits they do not know where they are. |
| Predator                | Something in the trees is watching them. Track marks. The sound of something large moving parallel. The decision: hunt it or avoid it.      |
| Thin ice / crevasse     | The surface cannot be trusted. Render through the sound — the crack, the shift, the held breath. Someone goes in or nearly does.            |
| Whiteout                | Nothing. No direction. No distance. They rope together and wait. Time disappears and comes back when the wind stops.                        |

---

## Calendar and Time

### Season Transitions

The shift from Long Summer to Long Dark is not a date. It is
a week when the light changes. The days get noticeably shorter.
The frost stays past midday. Someone puts on a second layer and
does not take it off again for months.

### Time Cost → Narrative Pacing

Activities take time. Time is rendered through what else does
not happen while the activity is underway.

"They foraged until midday, which meant they did not march
until midday, which meant they covered half the ground."

"The barrow took two days. Two days of not moving, not
earning, eating stores they could not replace."

Time is money and time is food and time is survival. Every
activity that costs time costs everything else too.

### Month Names → Atmospheric Markers

The month names exist in the world. Characters use them.
"We need to reach Ironmoon with silver to spare." "Barrowrise
is no time to be in the mountains." The names carry seasonal
weight — readers learn what each month feels like through
context.

---

## The Supernatural

### Veil Events → Prose Dread

Supernatural events in the Iron Ledger are not fantasy set
pieces. They are moments when the world is _wrong_ and the
characters know it. For extended weather-arc treatment of
each supernatural state, see `weather-as-character.md`
§ Supernatural Weather.

**The Hush:** The silence that means something is listening.
Render through absence — the birds that stopped, the wind
that died, the quality of air that changes. Men who have
been through it before react before the new men understand.
Weapons come out. Nobody talks. It passes or it does not.

**Veil-Thinning:** Reality is unreliable. Render through
small wrongnesses — a shadow at the wrong angle, a sound
that should not be there, the feeling of being watched by
something that is not in the treeline. Dalla reacts first.
Her methods are quiet and the men do not ask what she does.

**Blood Sun:** The sky is wrong. Render through scale —
this is bigger than the band, bigger than the immediate
situation. The world itself is afflicted. Men who are not
afraid of steel are afraid of this. The fear is older than
language.

### Supernatural Rendering Pipeline — Thorne and Dalla

Supernatural events are rendered through two characters
with distinct roles:

**Thorne reads. Dalla responds.** Thorne is the
diagnostic — he reads rune-signs, interprets warnings,
and advises Voss in private. His delivery is flat and
factual: "The barrow is wrong." He tells the band what
to avoid, what to respect, when to leave. He does not
explain mechanism. See `plot-planning.md` (Supernatural
Arc Rules, Rule 2) for his interpreter role.

**Dalla acts.** Her seidr gives her perception the men
lack — she reacts first during the Hush, responds with
runes and herbs during Veil-Thinning. Her methods are
quiet and the men do not ask. She is the band's only
response to threats steel cannot answer. See `pantheon.md`
(What Dalla Fears) for her theological uncertainty.

**Rendering order:** Thorne warns → Voss decides →
Dalla acts (if action is possible). The reader's access
to the supernatural layer comes through Dalla's behavior
(what she does, what she refuses to explain) and Thorne's
warnings (what he says privately to Voss). When both are
present, Thorne speaks first and Dalla moves second.
When only one is present, that character carries both
functions.

---

## Forbidden Renderings — Universal Rules

1. **Never state a number directly.** Not "they had twelve
   days of food." Instead: "Gest said they could eat for
   almost a fortnight if Dalla was careful."

2. **Never use game terminology.** Not "morale," "stamina,"
   "hit points," "armor class." The words do not exist in
   the world.

3. **Never summarize a state.** Not "the band was in poor
   shape." Show the specific indicators — who is limping,
   who is not talking, what the food situation looks like.

4. **Never editorialize on behalf of characters.** Not
   "Voss knew they were in trouble." Show what Voss sees
   and what he does. The reader concludes the trouble.

5. **Never explain the simulation.** The reader does not
   know there is a simulation. The world behaves
   consistently because the simulation drives it, but the
   reader experiences it as a world that makes sense.

6. **Never use weather as metaphor.** The weather is not a
   mirror of mood. It is a physical condition that affects
   the band's ability to operate. If it is storming during
   a crisis, the storm is its own problem, not a symbol of
   the crisis.

7. **Never skip the cost.** Every action has a cost in time,
   food, silver, or lives. The cost is always rendered.
   A fight scene is not over when the last man falls — it
   is over when Gest counts the dead, Dalla treats the
   wounded, and the ledger is updated.
