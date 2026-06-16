# Combat to Prose — Iron Ledger

**Purpose:** How to convert combat_sim.py output — round logs,
hit locations, wound severities, stances, maneuvers, conditions,
stamina states, and counter-attacks — into fiction that reads as
lived violence, not choreography. The simulation provides the
mechanical truth of what happened. The prose renders what it
felt like.

> **Cross-reference:** `simulation-rendering-guide.md` § Combat
> contains the HEMA stance and wound rendering tables. This file
> covers the full fight-scene prose pipeline and the 70/30 ratio.

---

## The Translation Principle

The simulation output is a medical examiner's report. The
prose is the survivor's testimony. These are not the same
document. The simulation says "CUT → torso → 6 damage → light
wound." The prose says: "The blade caught him across the ribs
and he felt the mail links break and something hot underneath."

Every combat scene begins with running the simulation. The
simulation determines who wins, who is hurt, where they
are hurt, and how long it takes. The author does not override
the simulation. The author renders it.

---

## Fight Duration → Narrative Time

### Simulation Rounds → Real Time

A simulation round is roughly five seconds of fighting. This
is critical for rendering.

| Rounds | Real Time           | Rendering Approach                                                                                                                                                                                                                                              |
| ------ | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1–3    | Under 15 seconds    | One paragraph. It is over before the reader finishes breathing. Fast, clipped sentences. "He swung. The other man blocked. He swung again and this time it landed. Done."                                                                                       |
| 4–8    | Up to a minute      | A short scene. The fight has phases — an opening, a middle where someone gets hurt, an end. Most mercenary fights. Two to four paragraphs.                                                                                                                      |
| 9–15   | One to two minutes  | A full scene. The fighters tire. Stances shift. Someone bleeds and the bleeding matters. The fight has its own narrative arc. The reader sees the stamina drain through the prose rhythm slowing.                                                               |
| 16–30  | Two to five minutes | A long fight between skilled or armored opponents. This is rare and significant. A duel between named characters. Multiple phases with distinct tactics. The stamina system drives the pacing — early aggression, mid-fight adjustment, late-fight desperation. |

### The One-Minute Rule

Most fights between mercenaries last less than a minute. The
reader should feel this. A one-minute fight does not get a page
of prose. It gets a paragraph or two. The brevity is the truth.
Men who fight for a living do not have extended exchanges — they
hit or get hit and one of them falls.

Long fights are the exception. When they happen, they matter.
A fifteen-round duel between Voss and a named opponent is a
scene because it is unusual. The length itself is information —
these are two men who know what they are doing.

---

## Hit Locations → Physical Experience

### Rendering by Location

| Location  | Physical Rendering                                                                                                                                                                                                               | Character Response                                                                                                                                        |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Head      | The world goes bright or dark. Sound changes. Balance fails. A head hit is the most disorienting thing in a fight. Render through perception distortion — "the ground tilted" or "everything was very loud and then very quiet." | Dazed condition: the fighter's next action is delayed, uncertain. He knows he has to do something but the signal takes longer.                            |
| Torso     | The deepest impact. Air leaves the body. Something breaks or something gives. A torso wound changes how the fighter stands, how he breathes, how he holds his weapon.                                                            | The center is hit and everything redirects around the damage. He fights differently now — guarding the wound side, turning to present the undamaged side. |
| Right Arm | The weapon arm. A wound here changes the fight immediately. Grip weakens. The swing comes from a different angle. The fighter compensates and the compensation is visible.                                                       | He switches grip, or his strikes get shorter, or he stops swinging and starts defending because the arm will not do what he asks.                         |
| Left Arm  | The shield arm, the balance arm. A wound here changes defense. The shield drops or hangs. The guard opens on one side.                                                                                                           | He stops blocking on that side. The opponent sees it. The fight shifts to exploit the opening.                                                            |
| Legs      | Mobility dies. A leg wound turns a fighter from someone who can maneuver into someone who stands and takes what comes.                                                                                                           | He plants. Cannot retreat, cannot advance easily. The fight happens at his feet or it moves away and he cannot follow.                                    |
| Hands     | The hardest location to protect and the most immediately disabling to lose. A hand wound drops the weapon or ruins the grip.                                                                                                     | Fingers do not work. The weapon turns in the hand or falls. He is not disarmed — he is un-handed.                                                         |
| Feet      | Rare but crippling. A foot wound stops movement dead.                                                                                                                                                                            | He cannot put weight on it. He fights standing on one leg or kneeling. Everything about the fight changes from this position.                             |

### Location Multiplier → Prose Weight

The simulation applies a location multiplier to damage. Do
not render the multiplier. Render the result. A head hit with
multiplier 1.5 is more devastating than a leg hit with
multiplier 0.8. The prose shows this through consequence: the
head-hit fighter staggers, the leg-hit fighter limps.

---

## Wound Severity → The Cost of the Scene

### Rendering Wounds

Wounds are the currency of combat scenes. Every wound costs
something and the cost must be visible.

**Scratch (1–3 damage):** Mentioned once, then forgotten
during the fight. Noticed after, when the shirt sticks to
it. A line of red that nobody except Dalla cares about. It
matters in the aggregate — three scratches become a light
wound's worth of attention.

**Light wound (4–7 damage):** The first wound that changes
behavior. The fighter adjusts. Pain is present but manageable.
Blood is visible but not flowing. This is the wound that a
professional fights through and a beginner flinches from.

**Serious wound (8–11 damage):** The wound that ends the
fight or turns it. Blood that does not stop. Something
internal is damaged — a muscle cut, a rib broken, something
that makes breathing or moving fundamentally different.
The fighter knows he is hurt badly. His face changes. The
pain announces itself in how he holds his weapon, how he
breathes, how his feet move.

_Bleeding starts._ The clock is ticking. Render through
wetness, through color, through the dark stain spreading
on cloth. Dalla needs to see this soon.

**Critical wound (12–15 damage):** The wound that ends
everything except the dying. Bone visible. Blood that pulses.
The fighter goes down or stays up through shock alone, and
shock does not last. If he stays up, render the unreality —
he is still fighting but he is already somewhere else. The
body has not caught up to what the wound means.

**Mortal wound (16+):** He falls and does not get up. Do
not make it heroic. Make it physical. The sound the body
makes when it hits the ground. The way the limbs do not
arrange themselves gracefully. What comes out of the
wound. The smell, if it is a gut wound. The duration —
mortal does not mean instant.

### Wound Accumulation

Multiple wounds compound. The second light wound is worse
than the first because the body is already paying the price
of the first. Render through degradation — each wound makes
the fighter less. Not suddenly, but inevitably. By the third
wound the reader should feel the fighter losing the fight
through attrition even if the simulation has not declared a
victor.

### Bleeding → The Timer

Bleeding is a scene timer. When a fighter starts bleeding,
the fight has a deadline. Render through:

- **Color changing.** The blood darkens as it leaves the body.
  Fresh is bright. Dried is dark. The stain tells time.
- **Performance drop.** The fighter's actions get slower as
  blood pressure drops. Swings that were fast become
  adequate, then slow.
- **Other characters' reactions.** Someone on the sideline
  notices. Dalla moves closer. Another Named Man starts
  watching instead of looking away.

---

## Stances → Character Reads

### Reading the Fight Through Stance Shifts

The stance shift is the character moment in a fight. When a
fighter changes from aggressive to defensive, the fight is
telling a story. The reader should see the shift through
physical description, not through labels.

**Aggressive → Defensive:** "He stopped pressing. His weight
moved back. The weapon came up to cover instead of to strike."
This is the moment the fighter understands he is losing, or
the moment he decides to wait.

**Balanced → Low Guard:** "He dropped the point. An invitation
or a surrender — you could not tell until you tried." This is
the moment of tactical confidence. The fighter trusts his
counter.

**Defensive → Aggressive:** "Something changed. He came forward
again. Whatever calculation he had been making was done." This
is the moment of commitment. He has decided to win or die
trying.

### Stance as Character

Voss fights balanced until he is hurt, then shifts aggressive.
He does not retreat. His response to losing is to attack harder.
This is character expressed through combat mechanics.

A different character — careful, patient — fights defensive
and waits for the counter. Their fighting style is their
personality.

---

## Maneuvers → Narrative Beats

### Attack Maneuvers as Prose Beats

Each maneuver type produces a different kind of prose beat:

**Cut** — The standard beat. A swing, a block or a hit.
Varies by weapon: a sword cut is a clean arc, an axe cut
is a chopping motion, a seax cut is short and close.

**Thrust** — A different rhythm. Faster, straighter. The
prose is shorter — "the point came forward" is the whole
beat. Thrusts at extremities render through precision: "under
the arm," "at the thigh," "between the mail links at the
collar."

**Heavy blow** — A power beat. The setup is visible. The
fighter chambers the weapon, shifts weight, commits. The
blow arrives with everything behind it. If it hits, the
impact is structural — things break. If it misses, the
fighter is open and both men know it.

**Half-sword** — An intimacy beat. Close range. One hand
on the blade. Looking for cracks in armor. This is the
ugly phase of fighting an armored man. The prose is tight
and specific — narrow distances, precise targets.

**Mordschlag** — A desperation or dominance beat. Gripping
the blade and swinging the crossguard like a hammer. Against
heavy armor, the only thing that transmits force. The prose
is percussive — short sentences for a blunt weapon.

### Control Maneuvers as Turning Points

Control maneuvers are the moments that redirect a fight.

**Bind** — Two blades locked. A moment of pure strength
and leverage. The prose pauses — the action stops being
fast and becomes tense. Who will redirect first. Who will
lose control.

**Shove** — The fight becomes wrestling. A man goes down.
Everything changes. Render the fall — the way balance fails,
the impact, the scramble.

**Grapple** — Close enough to breathe on each other. The
fight is no longer about weapons. Render through physical
contact — grip, weight, pressure, the smell.

**Shield bash** — A moment of blunt force. The rim of the
shield into the face or chest. Render through the stagger
that follows — a half-step, the eyes not tracking right.

**Disarm** — The weapon leaves the hand. The most decisive
non-lethal moment in a fight. Render the weapon hitting the
ground and the silence that follows.

### The Counter-Attack as Dramatic Reversal

The counter-attack is the most narratively powerful combat
event. The defender turns the attacker's offense into an
opening. In Low Guard, this is deliberate — he baited the
attack. From a skilled fighter, it is instinct — the
parry continues into a strike without a conscious decision.

Render the counter as a single flowing motion: "He caught
the sword on his blade and his blade kept moving, around
and in, and the other man's exposed side was there."

The counter changes who is winning. It is the narrative
reversal and should be rendered with the weight of a
turning point.

---

## Mass Combat vs. Small Fight

### Small Fight (1v1 or 2v2)

Full simulation rendering. Every round can be a prose beat.
The reader sees individual actions, specific wounds, the
progression. These are character scenes.

**Pacing:** Each round of simulation maps to one or two
sentences. A cut that misses is half a sentence. A serious
wound is a full paragraph.

### Skirmish (3v3 to 5v5)

Selective rendering. The POV character's fight is fully
rendered. Other fights are glimpsed between the POV
character's exchanges — a scream from the left, someone
falling in the periphery, the sound of shield on shield
somewhere behind.

**Pacing:** The POV fight is detailed. Other fights are
impressionistic. A 3v3 skirmish might give the POV fight
four paragraphs and the other fights two sentences each.

### Large Engagement (10+ fighters)

Chaos rendering. Nobody sees a large fight clearly. The
POV character sees what is directly in front of them and
hears the rest. Render through sensory fragments — a blade
in the corner of vision, a body underfoot, the press of
men, the sound that a group of fighting men makes.

**Pacing:** Fast. Short sentences. Fragments. The clarity
comes after, when the survivors look at the field and
count.

**The Aftermath:**

The simulation produces casualties. The aftermath scene
renders them. This is not the fight — this is after the
fight. Dalla moving between the wounded. Gest counting the
dead. The sound of a man who is hurt badly and cannot stop
making noise. The silence of the men who are too hurt to
make noise.

---

## The Aftermath Protocol

Every combat scene has an aftermath. The fight is not over
when the last man falls. It is over when the cost is counted.

### Step 1: The Immediate After

The noise stops. Breathing. The fighters who are still up
look at the fighters who are not. Someone says "it's done"
or says nothing. The adrenaline wears off and the wounds
announce themselves — the ones that were ignored during the
fighting.

### Step 2: Dalla's Work

The healer moves. This is medical reality, not healing magic.
Dalla uses cloth, herbs, a knife for what needs cutting. She
is efficient and her efficiency is terrifying. The wounded
man watches what she does to him and decides how afraid to be
based on her face.

### Step 3: The Counting

Gest counts the dead. Gest counts the living. Gest counts
the wounded and estimates how long before they are useful
again. These numbers go in the ledger and the ledger is
the truth.

### Step 4: The Equipment

The dead are stripped. Not cruelty — logistics. Weapons,
armor, boots, coins. Whatever is useful moves from the dead
to the living. If the dead are the band's own, this is done
quietly and with something that might be respect. If the dead
are the enemy, it is done efficiently and without comment.

### Step 5: The Narrative Weight

The aftermath is where the combat scene earns its meaning.
A fight that costs nothing means nothing. A fight that costs
a Named Man, or three commons, or Voss's sword arm for two
weeks — that fight shapes every scene that follows. The
aftermath renders the cost so the reader carries it forward.

---

## Violence Rendering Rules

### Sound Over Visual

Sound is more powerful than visual for violence. The sound
of blade on bone. The sound of a man being hit in the
stomach — not what it looks like, what it sounds like. The
sound a shield makes when it breaks. The silence after.

### Impact Over Choreography

Do not choreograph fights move by move. Render the impacts.
The reader does not need to know which foot was forward or
how the wrist turned. The reader needs to feel the blow
land.

### Physical Over Abstract

Violence is physical. Blood is warm. Steel is cold. Mud
is slippery. Armor is heavy. Everything in a fight has
weight and temperature and texture. Abstract descriptions —
"the battle raged," "swords clashed" — are forbidden.

### Aftermath Over Killing Moment

The killing blow is one sentence. The aftermath is a
paragraph. The moment of death is fast. The consequence
of death is slow. What the dead man's friend does next.
What Dalla cannot fix. What the ledger loses.

### The Reader's Body

The best violence writing makes the reader's body react.
Flinch, tighten, exhale. This comes from specificity.
"He was hit in the stomach" does nothing. "The blade
went in below the navel and he felt his legs stop working"
makes the reader's abdomen clench.

---

## Forbidden Combat Renderings

1. **No gaming language.** Not "he rolled a critical hit."
   Not "damage per round." Not "initiative." These words
   do not exist.

2. **No blow-by-blow choreography.** Not "he swung from
   the left, she parried to the right, then she
   riposted to the upper left." This reads as stage
   direction, not fiction.

3. **No clean deaths.** Nobody dies neatly in the Iron
   Ledger. Dying is ugly, slow, or sudden-and-messy.

4. **No unnamed heroics.** If a common soldier does
   something extraordinary, name him. Heroics come from
   people, not from extras.

5. **No painless wounds.** Every wound hurts. Pain is
   specific — sharp, dull, hot, cold, throbbing. The
   character responds to pain as a physical event, not
   as a narrative inconvenience.

6. **No martial arts jargon.** The characters do not
   know they are performing "Zornhau" or "Pflug."
   They swing, they guard, they push. The technique is
   in what the body does, not in what the technique is
   called.

7. **No equal exchanges unless the simulation says so.**
   If the simulation says one fighter dominated, the
   prose reflects domination. If the simulation says it
   was even, the prose reflects parity. The simulation
   is the authority.
