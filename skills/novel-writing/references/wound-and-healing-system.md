# Wound and Healing System — Iron Ledger (Lore Reference)

**Purpose:** The lore and medical reference for the Iron Ledger
wound system. Contains period-accurate 9th–11th century Norse
leech-craft, Galenic humoral theory, wound classification by
weapon type, healing stage narratives, infection descriptions,
amputation procedures, and medieval medical terminology.

This document is the narrative and medical companion to the
mechanical rules. All simulation mechanics, YAML schemas,
penalty tables, healing timelines, subsystem commands, and
integration code have been moved to their canonical locations.

All medical understanding is period-accurate. No modern medical
terminology is used in narrative rendering. The simulation
tracks modern-equivalent data; the prose renders medieval
understanding.

> **Mechanics live here:**
>
> - Wound record schema, sublocation tables, accumulation
>   rules: `20_SIMULATION_RULES.md` § 5.4–5.6
> - Healing timelines and stage mechanics:
>   `20_SIMULATION_RULES.md` § 5.7–5.8
> - Infection check formula and bone mechanics:
>   `20_SIMULATION_RULES.md` § 5.9–5.10
> - Pain, incapacitation, and penalty tables:
>   `20_SIMULATION_RULES.md` § 5.11–5.13
> - Health subsystem commands:
>   `20_SIMULATION_RULES.md` § 5.16
> - Combat sim integration code:
>   `20_SIMULATION_RULES.md` § 5.17
> - Wound prose rendering guidance:
>   `simulation-rendering-guide.md`
> - Character wound tracking:
>   `22_MEMBER_STATBLOCKS.md`

---

## The Medieval Healer's Understanding

### Humoral Framework

Every healer in the Rimevegr operates — knowingly or not — within
remnants of humoral medicine carried north by monks, traders, and
captured physicians. The body contains four humours whose balance
determines health:

| Humour                 | Element | Quality      | Excess Produces                     |
| ---------------------- | ------- | ------------ | ----------------------------------- |
| Blood (blód)           | Air     | Hot and wet  | Fever, swelling, florid complexion  |
| Phlegm (slim)          | Water   | Cold and wet | Lethargy, pallor, wet coughs        |
| Yellow bile (gall)     | Fire    | Hot and dry  | Anger, thirst, burning fevers       |
| Black bile (svartgall) | Earth   | Cold and dry | Melancholy, wasting, hard swellings |

A wound disrupts the humoral balance. Treatment aims to restore
it. A hot, swollen wound has excess blood — it is bled or leeched.
A cold, pale wound lacks vital heat — it is poulticed with warming
herbs. This framework is wrong by modern standards but internally
consistent and drives all healer decisions in the novel.

### The Leech (Læknir)

The Norse word for healer is _læknir_ (leech). The term carries
no stigma. A good leech is valued as highly as a good smith. In
the Svarthird, Dalla fills this role — she is not a physician in
the Galenic sense but a practical healer trained by observation,
oral tradition, and the hard arithmetic of what works and what
kills.

A leech's tools:

| Tool                  | Description                                     |
| --------------------- | ----------------------------------------------- |
| Bone needle           | Curved, for stitching flesh                     |
| Iron needle           | Finer, for delicate work near joints            |
| Sinew thread          | Swells when wet, tightening stitches            |
| Linen thread          | Lighter, for shallow wounds                     |
| The herb-pouch        | Yarrow, plantain, comfrey, wormwood, moss       |
| Birch-bark strips     | Splinting material, wound-wrapping              |
| Honey pot             | Antiseptic dressing (mechanism unknown to user) |
| Tallow / rendered fat | Wound-sealing, burn treatment                   |
| Iron probe            | A thin rod for checking wound depth             |
| Bone saw              | For amputation                                  |
| Cautery iron          | A flat-ended iron, fire-heated, for searing     |
| Leather bite-stick    | Held between the patient's teeth                |
| Linen bandages        | Cut from old shirts, boiled when possible       |
| Wooden splints        | Straight sticks, trimmed and padded             |
| Sphagnum moss         | Absorbent wound packing (genuinely antiseptic)  |
| Leech-stones          | River stones, heated, for drawing poultice      |

### The Wound-Drink Test (Sárdrykk)

The most reliable Norse diagnostic for gut wounds. The patient
drinks a strong broth of onion, leek, and garlic. If the smell of
the broth emerges from the wound, the gut wall is pierced and the
wound is mortal. No treatment exists. The leech tells the patient
to settle his affairs. This test is historically documented in
Norse sagas and is medically sound — a perforated intestine leaks
contents that carry the smell.

---

## Wound Classification

### By Weapon Type (Sárakenning — Wound-Knowing)

Medieval healers classified wounds by the instrument that made
them, because treatment differs fundamentally by wound geometry.

#### Hewn Wounds (Höggvundr)

Made by axes, swords, and heavy blades. Characteristics:

- **Geometry:** Wide, open, often deep. Clean or ragged edges
  depending on blade sharpness and angle.
- **Tissue damage:** Severs muscle, tendon, and sometimes bone.
  A clean axe-cut through the forearm can sever both bones.
- **Bleeding:** Heavy. The wound's width prevents natural
  clotting. Pressure and stitching required.
- **Treatment priority:** Stop bleeding, clean the wound bed,
  close the edges with stitches, poultice, bind.
- **Healing:** Good if closed clean. Poor if edges are ragged
  or tissue is missing (a chunk of flesh taken by an axe
  cannot be stitched closed — it must heal from the inside
  out, which takes weeks and leaves a concave scar).
- **Infection risk:** Moderate. The open wound bed is exposed
  but can be cleaned effectively.

#### Stab Wounds (Stungvundr)

Made by spears, swords (thrust), seaxes, and knives.

- **Geometry:** Narrow, deep. The puncture channel may be
  several inches deep but only finger-width at the surface.
- **Tissue damage:** Penetrates without severing. Can reach
  organs, major vessels, or joint spaces without obvious
  surface injury.
- **Bleeding:** May be minimal at the surface while bleeding
  heavily inside. The most deceptive wound type.
- **Treatment priority:** Probe the wound to determine depth
  and direction. Extract any embedded material (broken blade
  tip, cloth fragments pushed in by the weapon). Irrigate if
  possible. Cannot be reliably stitched closed (the channel
  seals and traps infection).
- **Healing:** Slow. Must heal from the deepest point outward.
  If the surface closes before the depth heals, an abscess
  forms — a pocket of putrefaction sealed under skin.
- **Infection risk:** High. The narrow channel is impossible
  to clean thoroughly. Cloth fibers driven into the wound by
  the weapon introduce contamination deep where irrigation
  cannot reach.

#### Crushing Wounds (Beystvundr)

Made by shield-boss strikes, mordschlag (pommel blows), mace
impacts, kicks, falls, and blunt impact.

- **Geometry:** No surface break or a small split over the
  impact point. The damage is internal — crushed tissue,
  broken bone, burst vessels beneath intact skin.
- **Tissue damage:** Deep bruising. Fractured bone. Dislocated
  joints. Internal bleeding pools under the skin as a
  hematoma (a hard, hot lump of trapped blood). Over ribs,
  a crushing blow can break ribs inward and puncture lung.
- **Bleeding:** Surface bleeding minimal. Internal bleeding
  can be life-threatening and invisible. A hematoma in the
  thigh from a heavy kick can hold a pint of blood.
- **Treatment priority:** Immobilize if bone is broken. Cold
  compress (snow, cold water cloth) to limit swelling. Monitor
  for signs of internal damage — growing hardness, skin color
  changing from red to purple to black, fever without visible
  wound.
- **Healing:** Varies enormously. A bruise heals in days. A
  cracked rib heals in weeks. A crushed knee joint may never
  heal correctly.
- **Infection risk:** Low (unless skin is broken), but
  complications from internal damage can be fatal.

#### Arrow and Bolt Wounds (Örvundr)

Made by short bow arrows, crossbow bolts, and javelins.

- **Geometry:** Penetrating wound with a foreign body lodged
  in the tissue. The arrowhead may be barbed (cannot be
  pulled back out) or bodkin-pointed (narrow, deep).
- **Tissue damage:** Entry wound is small. Internal track
  depends on penetration depth. An arrow through the shoulder
  may pass between bones and exit the back. An arrow in
  the abdomen is a death sentence without surgery.
- **Bleeding:** Controlled by the projectile itself — the shaft
  plugs the wound. Removal causes sudden heavy bleeding.
- **Treatment priority:** Do not remove the projectile in the
  field unless the leech is ready to immediately treat the
  hole it leaves. Cut the shaft short to prevent it catching
  on things and tearing the wound wider. Definitive treatment
  requires pushing the arrow through and out the other side
  (if the track allows) or cutting down to the head and
  extracting it. Both procedures are surgical and done only
  by a skilled leech.
- **Infection risk:** Very high. Arrowheads are dirty (often
  deliberately — some are stored in dung). The shaft drives
  cloth, leather, and filth deep into the body.

#### Burns (Brunavundr)

Made by fire, hot metal, scalding liquids, or cauterization.

- **Geometry:** Surface area matters more than depth. A palm-
  sized burn is painful but survivable. A burn covering an
  arm is potentially fatal from fluid loss and infection.
- **Tissue damage:** Reddened skin (first degree — painful but
  heals in days). Blistered skin (second degree — the body
  weeps clear fluid, extremely painful). White or charred skin
  (third degree — the nerves are destroyed, paradoxically
  painless at the center but agonizing at the edges).
- **Bleeding:** Minimal. Burns seal vessels.
- **Treatment priority:** Cool immediately (water, snow — not
  ice directly on the burn). Cover with clean linen smeared
  with honey or rendered fat. Do not break blisters (they
  are the body's natural dressing). Change dressings daily.
- **Healing:** Slow. Burns that destroy the full skin thickness
  heal by contracting — the scar tissue pulls surrounding
  skin inward, creating tight, rigid scars that limit
  movement. A burn across a joint (elbow, knee, knuckle)
  may heal into a contracture that permanently restricts
  that joint's range.
- **Infection risk:** Extremely high. The burned skin is dead
  tissue — perfect culture medium for putrefaction.

#### Frostbite Wounds (Kuldavundr)

Made by cold exposure. Treated as wounds in this system because
they produce tissue damage, require medical treatment, and can
result in permanent incapacitation.

- **Stage 1 — Frostnip:** White, numb patches on fingers, toes,
  ears, nose. No tissue death. Rewarm gently (body heat, warm
  water — never fire-heat, which causes thermal shock to
  constricted vessels). Full recovery in hours to days.
  Skin peels.
- **Stage 2 — Shallow frostbite:** Hard, waxy skin. Blisters
  form on rewarming (clear fluid — good sign). Tissue is
  damaged but alive. Recovery takes one to three weeks.
  The skin is sensitive and thin for months.
- **Stage 3 — Deep frostbite:** Skin and deeper tissue frozen
  solid. On rewarming, the area turns purple-black. Blood
  blisters (dark fluid — bad sign). The tissue is dead.
  Demarcation takes one to two weeks — the line between
  living and dead tissue becomes visible. Amputation at the
  demarcation line.

---

## Wound Accumulation from Combat

> **Mechanics moved.** Wound record schema, sublocation tables,
> accumulation rules, and stacking penalties are now in
> `20_SIMULATION_RULES.md` § 5.4–5.6.

**Key lore principle:** Every wound is a separate medical event.
A man struck three times in the right arm has three wounds, not
one merged injury. Each requires the leech's attention separately,
heals on its own timeline, and may fester independently. The
ledger tracks each one. The cost of violence is not abstract —
it is counted in stitches, in poultice changes, in days a man
cannot swing an axe.

---

## The Healing Stages

Each wound passes through defined stages. The leech recognizes
these stages by observation and adjusts treatment accordingly.
The simulation tracks the stage; the prose renders what the
healer and patient experience.

### Stage 1 — Fresh (Nývundr — New-Wound)

**Duration:** 0–4 hours after injury.

The wound is open, bleeding, and raw. The flesh is bright red
(unless deep — then dark red, and deeper still, the gleam of
white bone or the grey-purple of organs). This is the emergency
window. Everything the leech does in this window determines
whether the wound heals clean or festers.

**What the leech does:**

1. **Stop the bleeding** (staunching — blóðstöðvun). Direct
   pressure with clean cloth. Yarrow leaves packed against the
   wound (genuinely hemostatic — the plant name _Achillea
   millefolium_ reflects Achilles using it on wounds). If
   arterial (bright, pulsing blood), pressure above the wound
   on the limb. Tourniquet as last resort (a strip of leather
   twisted with a stick), knowing it may cost the limb.

2. **Clean the wound bed** (sárhreinsun). Irrigate with clean
   water. Wine or ale if available. Pick out every visible
   foreign body — cloth fibers, dirt, rust, bone chips. The
   iron probe is used to explore stab wounds for depth and
   direction. This step is agonizing. The patient is held down
   or bites the leather stick. The leech does not stop because
   the patient screams. Thorough cleaning is the single most
   important intervention.

3. **Close the wound** (sárlokun) if it is a hewn wound with
   approximable edges. Stitching with curved needle and sinew.
   Stitches placed a thumb-width apart. Each stitch tied
   individually (not a running stitch — if one stitch breaks,
   the others hold). The leech judges tension by how the skin
   pulls — too tight and the stitches cut through the swollen
   flesh in two days. Stab wounds are NOT stitched closed.
   They must heal from the inside, left open or loosely packed
   with moss or honey-soaked linen.

4. **Dress the wound** (sárbinding). A poultice of appropriate
   herbs applied directly:

   | Poultice      | Properties (Medieval Understanding) | Actual Effect                  |
   | ------------- | ----------------------------------- | ------------------------------ |
   | Yarrow        | "Draws the humours, stops blood"    | Hemostatic, mild antimicrobial |
   | Plantain leaf | "Cools the wound-heat"              | Anti-inflammatory              |
   | Comfrey root  | "Knits the body" (called knitbone)  | Promotes tissue growth         |
   | Honey         | "Seals against foul air"            | Genuinely antiseptic           |
   | Sphagnum moss | "Drinks the wound-water"            | Absorbent, mildly antiseptic   |
   | Rendered fat  | "Keeps the wound supple"            | Moisture barrier               |
   | Spider web    | "Stops the blood of small cuts"     | Hemostatic mesh                |
   | Garlic paste  | "Burns the rot from the wound"      | Antimicrobial (allicin)        |
   | Birch sap     | "Washes the wound-fever"            | Mild antiseptic                |

   The poultice is bound in place with linen strips. The
   binding must be firm enough to hold but not so tight it
   cuts off blood to the limb (checked by feeling the
   fingertips or toes below the binding — if they go cold or
   numb, the binding is too tight).

### Stage 2 — Clotting (Blóðstorknun)

**Duration:** 4–48 hours after treatment.

The bleeding has stopped. A clot (dark, jelly-like mass) fills
the wound. The edges are swollen and red — this is the body
marshalling blood (hot humour) to the injury site. The area is
warm to the touch. The patient feels a deep, throbbing ache
that worsens at night.

**What the leech watches for:**

- **Good signs (farsælt — "lucky traveling"):** Swelling that
  is firm, not spreading. Redness confined to the wound edges.
  The patient has appetite and can sleep (badly, but can sleep).
  Wound discharge is thin, pinkish (sanguineous — "of the
  blood").

- **Bad signs (úfarsælt — "unlucky traveling"):** Swelling that
  spreads beyond a hand's width from the wound. Redness
  streaking outward (the red lines of lymphatic spread — the
  leech calls this "wound-tracks" and knows it means the rot
  is traveling). Discharge turning thick and yellow-green.
  The patient loses appetite, shivers, sweats at night.

**Treatment:** Change the dressing daily. Fresh poultice. Keep
the wound elevated if on a limb. The patient rests. In the
Svarthird, "rests" means lies by the fire while the band
marches, carried on the mule if he cannot walk, or left in a
settlement if the band cannot wait. This decision falls to Voss
and is recorded in the ledger.

### Stage 3 — Closing (Gróun — Growing-Together)

**Duration:** Day 2 to Day 7 (light wounds), Day 2 to Day 14
(serious wounds).

The wound is closing. New tissue — called "proud flesh"
(holdkjöt) by the leech — grows from the wound bed to fill
the gap. In a stitched hewn wound, the edges knit along the
suture line. In a stab wound left open, the proud flesh builds
slowly from the deepest point, visible as dark red granulation
at the wound mouth.

The patient's body is working hard. He is hungry (the body
needs fuel to build tissue), tired (healing consumes energy
as surely as marching), and irritable (constant dull pain
wears at Will). The wound itches fiercely — a good sign,
the leech says, meaning the flesh is knitting, but the urge
to scratch can re-open closing tissue.

**What the leech does:** Removes stitches when the wound
edges hold on their own (typically day 7–10 for a well-
healing hewn wound). If a stitch has pulled through or
broken, the gap is re-stitched or packed with honey-linen.
Poultice shifts from hemostatic (yarrow) to tissue-promoting
(comfrey). The leech checks for "cold wound" — a wound that
has stopped closing and sits pale and flat, neither healing
nor festering. A cold wound is treated with a warming
poultice (mustard seed paste, garlic, heated stones applied
around but not on the wound) to "bring the humours back."

### Stage 4 — Knitting (Sáragrói — Wound-growth)

**Duration:** Day 7 to Day 21 (light), Day 14 to Day 45
(serious), Day 30 to Day 90 (critical).

The wound is structurally closed but not strong. The new
tissue is fragile — a hard knock, a sudden strain, or a
fight can re-open it. This is the most dangerous period for
a mercenary, because the man feels better than he is. He
wants to work. He reaches for something, swings at something,
kneels wrong, and the wound opens again. A re-opened wound
at this stage is worse than the original — the new tissue
tears more easily than the old, and infection risk is high
in the compromised tissue.

Bone fractures are in this stage for the longest. A bone
knits slowly — six to eight weeks for a clean fracture of the
forearm, eight to twelve weeks for a thigh bone, and the bone
is weak for months after. A man who bears weight too soon on
a knitting thigh-bone re-breaks it, and the second break
always heals worse.

**The leech's role:** Enforce rest. This is the hardest part
of medicine in a mercenary band — telling a man who feels
close to whole that he is not, and telling a captain who needs
every axe that this one is not ready. Dalla and Voss have
this argument repeatedly. The ledger records the cost either
way.

### Stage 5 — Scarring (Örmyndun)

**Duration:** Day 21+ (light), Day 45+ (serious), Day 90+
(critical).

The wound has closed permanently. What remains is a scar —
new tissue that is stronger than the wound but weaker and
less flexible than the original. The scar is red-pink and
raised at first, fading over months to white or grey-white.
In dark-skinned individuals, scars may darken. The tissue
underneath may be thinner, harder, or lumpy depending on how
well it healed.

At this stage, the wound is functionally healed but may
carry permanent consequences (see Incapacitation section).
A well-healed light wound produces a thin scar and no
lasting effect. A badly healed serious wound produces a
thick, contracted scar that limits range of motion.

### Stage 6 — Healed (Gróit)

The wound is fully resolved. The scar is mature (pale,
flat or slightly raised, no longer tender). The wound record
is marked `resolved: true`. Any permanent effects remain
on the character's statblock.

---

## Infection and Complications

### Wound-Rot (Sárfúi)

The medieval term for wound infection. The leech understands
it as "foul humours entering the wound from bad air, unclean
water, or evil influence." The reality: bacteria from dirty
instruments, unwashed hands, contaminated water, and embedded
foreign material.

> **Infection check mechanics:** See `20_SIMULATION_RULES.md`
> § 5.9 for the daily infection formula and modifiers.

#### Infection Stages

#### Stage 1 — Early Rot (Fyrsta Fúi)

Onset: 1–3 days after contamination.

Signs: The wound edges redden beyond normal swelling. The
discharge thickens and takes on a yellow or greenish tinge.
The area is hot and hard to the touch. The patient complains
of increased, pulsing pain. The leech recognizes this immediately.

Treatment: Re-open the wound (cut the stitches if stitched).
Clean aggressively — irrigate with boiled water or wine, remove
any visible pus (thick, opaque discharge — the leech calls it
_sárvar_, wound-liquor). Repack with garlic paste or honey. Bind
loosely. Change dressing twice daily.

#### Stage 2 — Spreading Rot (Breiðfúi)

Onset: 3–5 days after contamination without treatment (or
treatment failure).

Signs: The redness spreads beyond a hand's width. Red streaks
extend from the wound toward the trunk (the leech calls
these "wound-roads" — they follow the lymphatic vessels).
Discharge is copious, thick, and foul-smelling. The patient
has intermittent fever, sweats at night, and loses appetite.

Medieval concept: The leech may say the wound has "praised
pus" (lofsár) if the discharge is thick and white (which
actually indicates the body is fighting the infection) versus
"foul pus" (úhreint sár) if thin, grey-green, and stinking
(which indicates the infection is winning). This distinction
is historically important — medieval healers genuinely believed
thick white pus was a good sign. The concept of "laudable
pus" persisted into the 19th century.

Treatment: Drain the wound (lance any abscess — a sharp cut
into the pocket of pus, which pours out under pressure and
smells atrocious). Pack with hot compresses to "draw out the
pus." Garlic-and-honey dressing. Willow bark tea for fever
(genuine salicylate effect). The patient is fed broth and kept
warm.

#### Stage 3 — Deep Rot (Djúpfúi)

Onset: 5–10 days after contamination without effective
treatment.

Signs: The flesh around the wound darkens to purple-grey. The
discharge has a sweet, rotten smell that is distinct from
normal wound-smell — experienced healers recognize this
immediately as the smell of flesh dying while the patient
still lives. The patient has constant high fever, confusion,
rapid pulse, and may become delirious. The wound itself may
look "calm" — the surface has stopped draining because the
infection has gone deeper.

Treatment: Radical intervention. The leech cuts away all dead
and dying tissue (debridement — with a sharp knife, cutting
until the exposed flesh bleeds red, because red blood means
living tissue). The wound is now much larger but clean.
Alternatively, cauterization — pressing a red-hot iron to the
wound to sear all contaminated tissue. Cauterization is
agonizing, destroys tissue indiscriminately, and leaves a
severe burn wound in place of the infected wound. It is the
medieval surgeon's nuclear option. It works when nothing else
will.

If the wound is on a limb, the leech considers amputation.
Better to lose the arm than the man.

#### Stage 4 — Mortification (Dauðakjöt — Dead-flesh)

Onset: 10+ days of uncontrolled infection, or rapidly in
certain wound types (gut wounds, compound fractures).

Signs: The tissue is dead. It turns black. Gas forms under
the skin (gas gangrene — the skin crinkles and crackles when
pressed, and a foul gas escapes). The smell is overwhelming.
Other men move away from the patient. The patient is
delirious, septic (the infection has entered the blood), and
dying.

Treatment: Amputation of the affected limb, immediately, at a
point well above the visible mortification. If the infection
is on the torso or has spread beyond amputation range, there
is no treatment. The patient will die. The leech makes him
comfortable. Dalla has done this. She does not discuss it.

### Wound-Fever (Sárhiti)

Systemic fever caused by wound infection spreading to the
blood. Can occur from Stage 2 infection onward.

**Signs:** High, swinging fever (rises at night, drops slightly
by morning). Drenching sweats. Rapid, weak pulse. Confusion.
Thirst. The whites of the eyes may yellow (liver involvement).
Skin flushed or mottled.

**Treatment:** Willow bark tea (genuine antipyretic). Cool
cloths on forehead, wrists, groin (the major heat-loss
points). Keep the patient hydrated — broth, water, weak ale.
Address the source wound (the fever will not break while the
wound is still infected).

**Duration:** If the source infection is controlled, fever
breaks in 2–4 days. If not, the fever climbs until the
patient either breaks it (TOU check daily, difficulty scaling
with infection stage) or dies.

### Bone Complications

#### Simple Fracture (Beinhrot — Bone-break)

The bone is broken but the skin is intact. The bone ends
may be displaced (felt and sometimes seen as a deformity
under the skin) or in place (a crack, diagnosed by pain,
swelling, and the inability to bear weight or use the limb
normally, confirmed by the grinding sensation of crepitus
when the limb is gently moved).

**Treatment:** Traction (pulling the limb straight to align
the bone ends — this requires two people, one holding the
patient and one pulling) and splinting. Two straight sticks,
padded with cloth, bound firmly but not constricting on
either side of the break. The splint immobilizes the joint
above and below the break (a forearm splint locks the wrist
and the elbow).

**Recovery:** See Healing Timeline table below.

#### Compound Fracture (Opintbeinhrot — Open Bone-break)

The bone is broken AND the skin is breached — either the
bone end protrudes through the skin, or the wound extends down
to the broken bone. This is an emergency. The exposed bone is
a highway for infection.

**Treatment:** Irrigate the wound thoroughly. If the bone end
is protruding, push it back under the skin (this requires
strength, accuracy, and a patient who is held down or
unconscious — Dalla prefers a strong measure of mead or a
blow to the head if the patient will not hold still). Set and
splint as for simple fracture. Dress the wound as for a
serious hewn wound. Pray.

**Recovery:** Double the healing time of a simple fracture.
Infection risk: 40% base (the bone surface is contaminated).
A compound fracture that develops deep rot almost always
requires amputation.

#### Dislocated Joint (Úrliður)

The joint has been forced out of its socket. The limb is
frozen at an unnatural angle and the patient cannot move it.
The joint area swells rapidly.

**Treatment:** Reduction (forcing the joint back into the
socket). Technique varies by joint:

- **Shoulder:** The leech plants a foot in the patient's
  armpit and pulls the arm straight out and then rotates it
  back. A loud pop means success.
- **Finger:** Pull straight and twist. Quick.
- **Knee, hip:** Require more force and precise angles. Easier
  with two people — one stabilizes the body, one manipulates
  the limb.

Reduction must happen quickly — within hours, the muscles
spasm around the dislocation and resist. After a day, the
surrounding tissue swells so much that reduction without
cutting (surgery) becomes nearly impossible.

**Recovery:** The joint works immediately after reduction but
is loose and prone to re-dislocation for weeks. Binding,
limited use, and time.

---

## The Incapacitation System

> **Full mechanical rules moved.** Incapacitation record schema,
> incapacitation types, activity-specific penalty tables (head,
> arm/hand, leg/foot, torso), pain levels, and weather sensitivity
> mechanics are now in `20_SIMULATION_RULES.md` § 5.11–5.14.

Wounds produce specific functional impairments tied to anatomy
and activity. A man with a forearm wound cannot grip. A man
with a broken knee cannot kneel. A man with cracked ribs
cannot breathe deeply. These are not abstract penalties —
they are the physical reality of what a damaged body can and
cannot do, and they shape every scene in which the wounded
man appears.

**Narrative principle:** Show incapacitation through blocked
action, not through stated penalties. The reader sees what
the character cannot do and infers the rest.

- "He reached for the rope and his hand did not close on it."
- "He knelt and the knee locked halfway."
- "He tried to run. The leg answered but answered wrong."

### Pain as Internal Weather

Pain is experienced, not observed. A man with a set fracture
has a severe wound but moderate pain. A man with an infected
scratch has a light wound but severe pain. The leech asks
where it hurts and how it hurts — sharp, throbbing, burning,
dull — and adjusts treatment by the answer.

Chronic pain wears at the mind. A man in constant pain for
weeks becomes irritable, loses focus, sleeps poorly, and
eventually loses something he does not get back. The novel
tracks this erosion through Will, but renders it through
behavior: the short temper, the flinch, the thousand-yard
stare.

### Weather and Old Wounds

Old scars and healed fractures ache before weather changes.
Barometric pressure shifts genuinely affect healed injuries.
In the Rimevegr, this means:

- Before a rime storm: old knee injury throbs, healed rib
  fracture aches, scar tissue pulls tight.
- In deep cold: healed frostbite sites burn and tingle.
- In damp: old joint injuries stiffen.

This is used narratively as ambient detail and as character
texture ("Kell rubbed his forearm. The scar from the
Hook-fight was pulling. Bad weather coming.").

Veterans with enough old wounds gain a body-sense for weather
that functions as instinct. Their body tells them what their
eyes cannot see.

---

## Health Subsystem Commands

> **All commands moved.** The complete wound lifecycle command
> set (wound_apply, wound_treat, wound_heal, wound_infect,
> wound_worsen, wound_improve, wound_scar, wound_remove,
> amputation, condition_update) is now in
> `20_SIMULATION_RULES.md` § 5.16.

---

## Healing Timeline Summary

> **Timeline tables moved.** Healing timelines by wound
> severity, bone injury type, and field rest multiplier are
> now in `20_SIMULATION_RULES.md` § 5.8.

**Key lore principle:** In the field, wounds do not heal. A
man marching on a broken leg is not healing — he is enduring.
The leech knows this. Voss knows this. The decision to halt
the band so a man can rest, or to keep marching and lose the
man, is the ledger's cruelest arithmetic.

---

## Amputation — The Last Medicine

### When the Leech Reaches for the Saw

- Mortification (Stage 4 infection) on a limb — the tissue is
  dead and the death is spreading. Cut above the dead flesh or
  lose the patient.
- Crushing injury that has destroyed the limb beyond use — a
  foot caught under a fallen tree, a hand smashed by a
  shield-boss.
- Compound fracture with deep infection that will not clear.
- Severe frostbite (Stage 3) where black tissue demarcates
  cleanly — cut at the line of living tissue.

### The Procedure (Medieval)

1. **Decision.** The leech examines the limb, explains to the
   captain (and the patient, if lucid) that the limb is lost.
   The decision is the leech's. In the Svarthird, Dalla makes
   this call and Voss backs it. The patient does not get a vote
   if he is delirious. If he is lucid, he is told. His response
   varies from resignation to rage.

2. **Preparation.** A leather bite-stick between the teeth. Two
   strong men to hold the patient. A third to hold the limb
   steady. A tourniquet above the cut site (twisted tight with
   a stick). The bone saw, the cautery iron heating in the fire,
   clean linen for binding, rendered fat for the stump. If
   available: a strong measure of mead or ale to dull the
   senses. There is no anesthesia.

3. **The cut.** The leech cuts through skin and muscle with a
   sharp knife, working around the bone quickly. The bone is
   sawed through — the rasp of bone-saw is a sound that
   carries through the camp. Men who are not helping look away
   and do not speak. The severed limb is removed and disposed
   of (burned in the fire).

4. **Stump treatment.** The blood vessels are cauterized — the
   red-hot iron pressed against each visible vessel. The hiss
   of searing flesh. The smell. The patient loses consciousness
   or screams through the bite-stick. The stump is then dressed
   with rendered fat, bound in clean linen, and the tourniquet
   is gradually loosened (too fast and the rush of blood
   overwhelms the cautery).

5. **Recovery.** The surgical wound heals like a severe burn.
   Six to twelve weeks to close fully. Infection risk at the
   stump is high — daily inspection. The patient is weak from
   blood loss for days. The phantom pain (the sensation of the
   missing limb still being there, and hurting) begins
   immediately and may never fully stop.

### Post-Amputation Life

A man missing a hand can still fight — an axe lashed to the
stump, a shield strapped to the forearm. It is not optimal.
It is not as good as having the hand. But it is better than
dying of gangrene.

A man missing a foot walks with a wooden peg or a carved
block strapped to the stump. On flat ground, he manages. On
rough ground or in mud, he falls. Marching speed is halved.
Combat mobility is gone.

A man missing a leg above the knee uses a crutch. He does not
march. He rides the mule or stays in a settlement. His
fighting days are over unless he can fight from a seated
position (a wall, a doorway, the rail of a ship).

---

## Medieval Medical Terminology Glossary

These terms are used in narrative rendering. They replace modern
medical language with what a Norse leech would actually say.

### Wound and Injury Terms

| Medieval Term          | Modern Equivalent         | Usage Context                       |
| ---------------------- | ------------------------- | ----------------------------------- |
| Sár (wound)            | Wound                     | General term for any injury         |
| Höggvundr              | Incised/lacerated wound   | Hewn wound from blade               |
| Stungvundr             | Puncture wound            | Stab wound from point               |
| Beystvundr             | Contusion/crushing injury | Blunt force trauma                  |
| Örvundr                | Projectile wound          | Arrow or bolt wound                 |
| Brunavundr             | Burn wound                | Fire, hot metal, or scalding        |
| Kuldavundr             | Frostbite injury          | Cold damage to tissue               |
| Sárakenning            | Wound diagnosis           | Identifying wound type and severity |
| Blóð (blood)           | Blood                     | General                             |
| Blóðrás (blood-rush)   | Hemorrhage                | Heavy or arterial bleeding          |
| Blóðstorknun           | Clotting/coagulation      | Blood thickening in the wound       |
| Sárvar (wound-liquor)  | Wound discharge/pus       | Fluid from a wound                  |
| Holdkjöt (proud flesh) | Granulation tissue        | New tissue filling a wound          |
| Dauðakjöt (dead-flesh) | Necrotic tissue/gangrene  | Tissue that has died                |
| Beinhrot               | Fracture                  | Broken bone                         |
| Opintbeinhrot          | Compound fracture         | Broken bone through skin            |
| Úrliður                | Dislocation               | Joint forced from socket            |
| Beinagrisjun           | Crepitus                  | Grinding of broken bone ends        |
| Sárdrykk               | Wound-drink test          | Onion-broth test for gut wounds     |

### Treatment Terms

| Medieval Term        | Modern Equivalent         | Usage Context                        |
| -------------------- | ------------------------- | ------------------------------------ |
| Lækning (leeching)   | Medical treatment         | General term for healing arts        |
| Læknir (leech)       | Healer/physician          | The person who treats wounds         |
| Blóðstöðvun          | Hemostasis                | Stopping bleeding                    |
| Sárhreinsun          | Wound irrigation/cleaning | Flushing a wound with clean water    |
| Sárlokun             | Wound closure             | Stitching or binding a wound shut    |
| Sárbinding           | Wound dressing            | Applying poultice and bandage        |
| Saumuð (stitching)   | Suturing                  | Closing a wound with thread          |
| Hnútur (stitch-knot) | Suture knot               | Individual stitch                    |
| Grásáða (poultice)   | Poultice/compress         | Herb paste applied to wound          |
| Brendimerking        | Cauterization             | Searing tissue with hot iron         |
| Höfuðáverki          | Trepanation (if used)     | Opening the skull                    |
| Beinsetning          | Bone setting/reduction    | Aligning broken bones                |
| Spjöld (splint)      | Splinting                 | Immobilizing a fracture              |
| Umbinding            | Bandaging/binding         | Wrapping a wound or limb             |
| Dráttur (drawing)    | Traction                  | Pulling a limb straight for bone set |
| Skerðing             | Amputation                | Removing a body part                 |

### Infection and Disease Terms

| Medieval Term            | Modern Equivalent             | Usage Context                        |
| ------------------------ | ----------------------------- | ------------------------------------ |
| Sárfúi (wound-rot)       | Wound infection               | General wound infection              |
| Fyrsta fúi (first rot)   | Early infection               | Initial signs of infection           |
| Breiðfúi (spreading rot) | Cellulitis/lymphangitis       | Infection spreading outward          |
| Djúpfúi (deep rot)       | Deep tissue infection/abscess | Infection burrowing inward           |
| Sárhiti (wound-heat)     | Wound fever/sepsis            | Systemic fever from wound            |
| Kaldvundr (cold wound)   | Chronic non-healing wound     | Wound that stops progressing         |
| Lofsár (praised wound)   | Laudable pus                  | Thick white discharge (good sign)    |
| Úhreint sár (foul wound) | Purulent infection            | Thin, foul-smelling discharge        |
| Sárvegir (wound-roads)   | Lymphangitic streaking        | Red lines spreading from wound       |
| Svartfúi (black rot)     | Gangrene                      | Tissue death and mortification       |
| Gasfúi (gas-rot)         | Gas gangrene                  | Crepitant gangrene                   |
| Eitursár (poison-wound)  | Contaminated wound            | Wound with embedded foreign material |

### Condition Terms

| Medieval Term                 | Modern Equivalent          | Usage Context                      |
| ----------------------------- | -------------------------- | ---------------------------------- |
| Verkur (pain)                 | Pain                       | General                            |
| Bólga (swelling)              | Edema/swelling             | Inflammatory response              |
| Roði (redness)                | Erythema                   | Skin reddening from inflammation   |
| Hiti (heat)                   | Fever                      | Elevated body temperature          |
| Svitadagar (sweat-days)       | Febrile sweating           | Night sweats from infection        |
| Hristing (shivering)          | Rigors                     | Shaking from fever                 |
| Þvingunarsvefn (forced sleep) | Unconsciousness            | Loss of consciousness              |
| Höfuðverkur                   | Headache                   | Post-head-wound symptom            |
| Svimi (dizziness)             | Vertigo                    | Balance disturbance                |
| Sjónvilla (sight-trick)       | Visual disturbance         | Double vision, blurring            |
| Dauðafingur (dead-finger)     | Gangrene/necrosis of digit | Finger died from cold or wound     |
| Draugafótur (ghost-foot)      | Phantom limb pain          | Sensation in amputated limb        |
| Hreyfitap                     | Loss of mobility           | Cannot move joint or limb          |
| Kennslutap                    | Loss of sensation          | Numbness from nerve damage         |
| Styrktartap                   | Loss of strength           | Weakness from muscle/tendon damage |

---

## Integration with Existing Systems

> **Integration code moved.** Combat sim → wound record
> conversion, sublocation determination code, weapon-to-wound
> type mapping, statblock integration examples, and prose
> rendering rules are now in `20_SIMULATION_RULES.md` § 5.17
> and `simulation-rendering-guide.md`.

---

## Special Conditions

> **Mechanical thresholds and formulas:** See
> `20_SIMULATION_RULES.md` § 5.15 for the full rules.

### The Wound-Addled (Sárviti)

A character who has been wounded too many times accumulates
a composite psychological condition. This is not madness —
it is the exhaustion of a body that has been broken and mended
too many times. Each healed serious+ wound leaves a mark not
just on the body but on the mind.

The flinch reflex comes first — the body hesitates before
committing to violence, because it remembers what violence
costs. Then pain sensitivity — the nervous system is primed
for suffering, and new wounds hurt more than they should. The
old wounds ache together before storms. And underneath it all,
a permanent erosion of will — the accumulation of suffering
costs something irreplaceable.

In the Svarthird: Ubbe and Snorri are Wound-Addled. The younger
men see it but do not name it. The older men recognize it
because they are watching for it in themselves.

### The Iron Scar (Járnörr)

Rare. A character who has healed a mortal wound carries a
certain authority among other fighting men. He survived what
should have killed him. The scar is visible proof.

The scar speaks before the man does. Other characters treat
the bearer differently — not with respect, exactly. With the
particular regard men have for someone who has been where they
fear to go and come back changed. The body never fully
recovers from coming that close. The mortal wound site aches in
any weather colder than mild. The bearer learns to live with
what the wound took and what the scar gave.

---

## Cross-References

| Topic                       | Canonical File                               |
| --------------------------- | -------------------------------------------- |
| Wound mechanics (all rules) | `20_SIMULATION_RULES.md` § 5                 |
| Wound record schema         | `20_SIMULATION_RULES.md` § 5.4               |
| Sublocation tables          | `20_SIMULATION_RULES.md` § 5.5               |
| Accumulation rules          | `20_SIMULATION_RULES.md` § 5.6               |
| Healing timelines           | `20_SIMULATION_RULES.md` § 5.7–5.8           |
| Infection check formula     | `20_SIMULATION_RULES.md` § 5.9               |
| Pain and incapacitation     | `20_SIMULATION_RULES.md` § 5.11–5.13         |
| Health subsystem commands   | `20_SIMULATION_RULES.md` § 5.16              |
| Combat sim integration code | `20_SIMULATION_RULES.md` § 5.17              |
| Wound prose rendering       | `simulation-rendering-guide.md`              |
| Combat wound rendering      | `combat-to-prose.md`                         |
| Field medical procedures    | `medieval-skills-and-authenticity.md`        |
| Character wound tracking    | `22_MEMBER_STATBLOCKS.md`                    |
| Band state (YAML)           | `data/band_state.yaml`                       |
| Frostbite risk rules        | `20_SIMULATION_RULES.md` § 10                |
| Dalla's medical role        | `character-bible.md` § Dalla                 |
| Norse medical terminology   | `06_DICTIONARY_OF_NORSE_TERMS.md`            |
| Humoral theory context      | `01_RIMEVEGR_SETTING_BIBLE.md` § Norse Magic |
| Weather and healing         | `weather-as-character.md`                    |
