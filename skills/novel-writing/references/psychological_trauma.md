# Psychological Trauma — Iron Ledger (Lore Reference)

**Purpose:** The lore and period-accurate reference for psychological
harm in 9th–11th century Scandinavian warrior culture. Contains Norse
concepts of courage and its failure, the medieval understanding of
battle-madness and soul-damage, how mercenaries processed violence
without modern therapeutic frameworks, and the language they used to
describe what we now call PTSD, moral injury, and combat stress.

This document is the narrative and medical companion to the mechanical
trauma rules. All simulation mechanics, YAML schemas, recovery
timelines, subsystem commands, and integration code live in their
canonical locations.

All psychological understanding is period-accurate. No modern clinical
terminology appears in narrative rendering. The simulation tracks
modern-equivalent data internally; the prose renders 9th-century
understanding.

> **Mechanics live here:**
>
> - Trauma record schema, severity, accumulation:
>   `20_SIMULATION_RULES.md` § 5.18–5.19
> - Trauma conditions, triggers, recovery:
>   `20_SIMULATION_RULES.md` § 5.20–5.23
> - Trauma subsystem commands:
>   `20_SIMULATION_RULES.md` § 5.24
> - Combat sim integration:
>   `20_SIMULATION_RULES.md` § 5.25
> - Trauma prose rendering guidance:
>   `simulation-rendering-guide.md`
> - Character psychological tracking:
>   `22_MEMBER_STATBLOCKS.md`
> - Wound system (companion — physical damage):
>   `wound-and-healing-system.md`

---

## The Norse Understanding of the Mind

### No Word for "Trauma"

The Norsemen had no clinical concept of psychological damage. What
they had was richer and more brutal: a vocabulary built from observed
collapse. A man who broke in battle was not "traumatized" — he was
*argr* (unmanned), *hugsjúkr* (mind-sick), or *skegg-lauss* (without
beard, meaning without courage). The distinction mattered. Some
conditions were contemptible. Others were recognized as the price
of the life.

A man who flinched before blades was despised. A man who woke
screaming after a winter of killing was understood — not forgiven,
not treated, but understood. The difference between the two was
never articulated cleanly. The band knew when a man was breaking.
They just lacked the framework to help.

### Hugr — The Mind-Soul

Norse psychology centered on *hugr* — the active, conscious mind-soul
that governed will, courage, and intent. A man's hugr could be:

- **Strong (hugsterkr):** Steady under pressure, calm in blood.
  The ideal warrior state.
- **Restless (hugrunnr):** Agitated, unable to settle. The mind
  circles. Sleep is poor. The man is watchful beyond reason.
- **Sick (hugsjúkr):** The hugr is wounded. Decision-making fails.
  The man withdraws, or lashes out, or freezes. He is no longer
  reliable under pressure.
- **Broken (hugbrotinn):** The hugr has cracked. The man is
  functionally incapacitated by internal damage that no leech can
  reach. He may seem whole but cannot function as he was.

The hugr was understood as something that could be exhausted, just
like the body. A man could spend his hugr on too many battles, too
many winters, too many dead companions — and find that one day
there was nothing left to spend.

### Fylgja — The Following Spirit

Every person had a *fylgja* — a personal spirit or fetch, often
appearing in animal form, that accompanied them through life. The
fylgja was intertwined with fate and psychological wholeness:

- A man whose fylgja appeared to others in dreams was about to die.
- A man who could no longer sense his fylgja was considered cut off
  from his own luck — a dangerous state that affected the whole band.
- Trauma, in the Norse framework, was sometimes understood as the
  fylgja pulling away — the protective spirit withdrawing from a
  man who had seen too much.

This gave trauma a supernatural dimension. A broken man was not just
weak; he was *unlucky*. His fylgja had turned its face. Being near
him was dangerous for everyone.

### Hamr — The Shape-Self

The *hamr* was a person's outward presentation — their composure,
bearing, and social mask. A man who was *hamrammr* (shape-strong)
could maintain his outward form under any pressure. A man whose hamr
slipped showed his internal damage:

- Trembling hands where there were none before.
- A flinch at sudden sounds — doors, iron on iron, shouting.
- Changed gait — moving as if expecting a blow.
- Loss of the social mask: saying things that should stay inside,
  laughing at wrong moments, going silent when speech was expected.

The band watched each other's hamr constantly. It was the primary
diagnostic tool. When a man's hamr slipped, every man in the
Svarthird noticed — and began calculating what it meant for them.

---

## Sources of Psychological Damage

### Battle-Shock (Bardagi-Sótt)

The immediate response to extreme violence. Not cowardice — a
physiological overwhelm that the Norse recognized but had no medical
framework for:

- **Trigger:** Being in or witnessing close-quarters killing,
  especially chaotic engagements with no clear line of battle.
- **Presentation:** Freezing mid-action. Inability to respond to
  commands. Vacant staring. Hands that will not grip the weapon.
  Sometimes vomiting. Sometimes voiding. The body has decided to
  stop, and the mind follows.
- **Norse interpretation:** The man's hugr has fled his body
  momentarily. It will return. If it does not, he is *hugsjúkr*.
- **Band response:** Shield-brothers shake, shout, or strike the
  frozen man. If he comes back, it happened. No one mentions it
  unless it happens again. If it does, his reputation changes.

### Killing-Weight (Vig-Byrðr)

The cumulative psychological cost of killing. Not from a single
battle but from the slow accumulation of having ended lives. The
Norse understood this through their legal and spiritual frameworks:

- Every killing carried a *manngjöld* (man-price) — a spiritual
  and legal debt. Even justified killings in battle left a residue.
- Men who had killed many spoke of heaviness, of a weight that
  settled in the chest and did not lift.
- The *blood-guilt* concept was not purely legal. Some men felt
  physically heavier after prolonged campaigns. They slowed.
  They stopped singing.
- Berserkers were thought to be immune to killing-weight during
  their fury, but the price came after. The *berserksgangr*
  hangover was understood as the weight arriving all at once.

### Horror-Sight (Ógnar-Sjón)

Witnessing something that the mind cannot process. Distinguished
from battle-shock by its source — not personal danger, but seeing
things that violate the expected order:

- A companion's face destroyed beyond recognition.
- Children killed in a hall-burning.
- Torture — either witnessed or participated in.
- Corpse desecration, especially by enemies acting outside the
  norms of warfare.
- Starvation camps or siege aftermaths.
- Bodies recovered from water or long-dead.

The Norse had no concept of "processing" such sights. The
expectation was endurance: you saw it, you carry it, you do not
speak of it. The man who could not carry it was considered
weak — but the weakness was understood as a kind of
wound-of-the-eyes. He had seen something that cut him.

### Betrayal-Wound (Svikar-Sár)

Psychological damage from oath-breaking, betrayal, or being
abandoned by those sworn to protect you. In a culture built
entirely on oath and reciprocal obligation, this was perhaps the
deepest wound:

- A captain who left men behind to die.
- A shield-brother who ran when the line held.
- Payment withheld after service rendered.
- Being sold out to an enemy by a trusted ally.

Betrayal-wounds created a specific kind of damage: the inability
to trust. Men with unresolved svikar-sár became isolated within
the band, unable to lean on the mutual dependence that kept
mercenaries alive. They hoarded food, slept light, watched
every hand.

### Loss-Grief (Harmr)

The Norse did not separate grief from other forms of psychological
damage. *Harmr* was a catch-all for the pain of loss — of
companions, of home, of identity:

- Death of a shield-brother. The closer the bond, the deeper the
  harm. Men who had fought side by side for years formed bonds as
  intense as any kinship. Breaking those bonds through death left
  wounds that the Norse acknowledged but had no remedy for.
- Loss of home or family. A man who lost his hall, his farm, his
  people carried a kind of homelessness that was psychological
  as much as physical.
- Loss of identity. A farmer who became a killer. A free man
  enslaved and then freed. A man who did things in campaign that
  the man he was before would not recognize.

The sagas are full of *harmr*. What they are not full of is
recovery. Men carrying harmr either endured it or were consumed
by it. The lucky ones found new bonds. The unlucky drank
themselves to death or walked into a fight they could not win.

---

## Norse Coping Mechanisms

### The Fire and the Mead

The primary coping mechanism for all psychological damage was the
communal fire. After action, after march, after any crisis — the
band gathered at the fire. This was not therapy. It was proximity.
The warmth, the noise of others eating and talking, the sight of
living faces in firelight after a day of killing — this was what
the band had.

Mead and ale served a specific function: they loosened the hamr.
A man who would never speak of what he saw sober might, two horns
deep, say something that released pressure. The band tolerated
this. A man could weep into his cup and it happened only in
firelight. By morning it was unsaid.

The limit was functional. A man who drank so much that he could not
march, fight, or do his share of work had crossed from coping to
liability. The band's tolerance evaporated at that line.

### Saga-Telling

Recounting battles and events in stylized, crafted form served a
dual purpose: it processed experience through narrative, and it
reframed horror as story. A battle that was terrifying in the
moment became, in the telling, something with structure —
beginning, turning point, end. The man telling it could impose
order on chaos.

The sagas never mentioned fear except as a setup for its conquest.
This was not denial — it was a cultural technology for converting
raw experience into bearable form. The cost was that true
suffering went unspoken. The saga preserved the heroic version.
The real version rotted inside.

### Ritual and Sacrifice

Making offerings to the gods — particularly to Odin (who knew
suffering) and to Tyr (who knew sacrifice) — was understood as
transferring some of the weight to powers who could bear it.
A man who sacrificed after battle was not asking for forgiveness;
he was paying a debt, balancing the spiritual ledger.

Dalla's *seiðr* practice was the closest thing the Svarthird had
to psychological intervention. She read wyrd. She interpreted
dreams. She burned herbs and sang. Whether any of it worked in
a clinical sense was irrelevant — the act of someone attending to
the invisible damage was itself therapeutic. The men would not
call it that. They called it "Dalla's business."

### Physical Hardship as Medicine

The Norse instinctively treated psychological damage with physical
hardship — not as punishment, but as distraction and proof of
continued function. A man whose mind was sick was made to march,
to carry, to chop wood, to stand watch. The body's exhaustion
overrode the mind's circling.

This worked up to a threshold. Below that threshold, hard work
genuinely helped — it kept the man in his body, in the present, in
a world of immediate physical demands that left no room for the
images in his head. Above that threshold, the exhaustion
compounded the damage, and the man collapsed in a different way.

### Companionship and the Shield-Bond

The single most effective protection against psychological collapse
was the shield-bond (*skjaldvinr*) — the one-to-one relationship
between men who fought side by side. A man with a living,
functional shield-brother was significantly more resilient than
one without.

The shield-bond worked because it provided witness. Someone else
had seen what you saw. Someone else carried the same images. You
did not need to explain. You did not need to speak. You just
needed to know they were there, at the fire, alive.

When a shield-brother died, the surviving partner was at highest
risk of psychological collapse. The sagas record many instances
of men who became reckless, withdrawn, or changed in fundamental
ways after losing their *skjaldvinr*. The band knew this. Voss
would know this. Assigning a new partner was not replacing the
dead man — it was preventing a second loss.

---

## Manifestation Patterns

### Acute Response (Hours to Days)

The immediate aftermath of a traumatic event. The Norse would not
have distinguished this from battle-fatigue:

- **Withdrawal:** The man stops speaking. He does his tasks but
  initiates nothing. He eats mechanically or not at all. His eyes
  are present but not engaged.
- **Agitation:** The opposite pattern. The man cannot sit still.
  He paces. He snaps at questions. He wants to fight or walk or
  do anything that is not sitting with what happened.
- **Physical symptoms:** Trembling that comes and goes. Nausea
  without illness. Headache without injury. Exhaustion without
  exertion. The body processing what the mind cannot.
- **Flat affect:** The man seems fine. Too fine. He speaks normally,
  eats normally, does his work. But something is absent from his
  eyes. The hamr holds perfectly — but the person behind it has
  retreated to a room the others cannot reach.

### Chronic Response (Weeks to Months)

If the acute response does not resolve, it calcifies into patterns
the Norse knew well enough to name:

- **Night terrors (mara-ríðr — mare-riding):** The man wakes
  screaming, thrashing, fighting invisible enemies. The Norse
  attributed this to the *mara* — a supernatural entity that sat
  on the sleeper's chest. The reality was replayed experience.
  Night terrors disrupted the entire band's sleep and were
  deeply resented.
- **Flinch-sickness:** Involuntary startle response to sounds,
  sudden movements, or specific triggers (the clang of iron, the
  smell of blood, a particular word or phrase). A man with
  flinch-sickness was unreliable in surprise contacts.
- **Drink-seeking:** The transition from social drinking to
  functional need. The man drinks to sleep. He drinks to stop
  his hands from shaking. He drinks because the images come
  when he is sober. The band notices when a man's relationship
  to the ale-horn changes.
- **Anger-storm (bráð-reiði):** Disproportionate rage triggered
  by minor provocations. A man whose anger is no longer
  proportional to the cause is carrying unprocessed violence
  that bleeds out sideways.
- **Killing-calm (dráps-ró):** The opposite of anger-storm. A
  man who has killed enough that it no longer registers
  emotionally. He performs violence without any visible affect.
  This is not berserker fury — it is the complete absence of
  emotional response to taking life. Some men admired this.
  Others were deeply unsettled by it.
- **Withdrawal (einsetja):** The man retreats from the band.
  He takes solo watches. He sits apart at the fire. He stops
  maintaining gear, hygiene, or social obligations. He is still
  physically present but has resigned from the collective.
- **Risk-seeking (banvænn):** A man who has decided, consciously
  or not, that dying is preferable to continuing as he is. He
  volunteers for the most dangerous work. He fights without a
  shield. He provokes enemies. The band may interpret this as
  courage. It is not.

### Long-Term Damage (Seasons to Years)

What modern medicine calls PTSD. The Norse simply called it being
*used up* — a man who had given everything the life demanded and
had nothing left:

- **Cumulative will-erosion:** Permanent WIL loss. The man's
  baseline capacity for endurance, decision-making, and self-
  governance declines. Each additional trauma accelerates the
  decline. This is the psychological equivalent of accumulating
  physical scars.
- **Trigger-landscape:** A man with long-term trauma develops an
  internal map of things that set him off. Specific sounds,
  smells, weather conditions, locations, or people trigger acute
  re-experiencing that the man cannot control. The band learns
  his triggers through observation and avoids them — not out of
  kindness, but because an unpredictable man is dangerous.
- **Identity erosion:** The man no longer recognizes himself.
  The person he was before the campaigns — the farmer, the
  craftsman, the young man with plans — is gone. What remains
  is the fighter, and the fighter has nothing to offer except
  violence. "I was something else once" is the unspoken epitaph
  of long-serving mercenaries.
- **Numbness (kjölnun):** Complete emotional flattening. The
  man does not feel joy, grief, anger, or fear. He functions
  mechanically. He fights effectively. But the person is gone.
  What remains is a body that knows its job. This is sometimes
  mistaken for strength.

---

## Recovery and Resilience

### What Heals

Psychological recovery was not understood in the Norse period. What
existed were conditions that made recovery possible, observed
through centuries of men breaking and occasionally putting
themselves back together:

- **Time without threat.** The single most important factor. A
  man in continued danger cannot heal psychologically any more
  than a reopened wound can close. Winter quarters, a secure
  hall, weeks without combat — these created the conditions.
  They did not guarantee recovery.
- **Meaningful work.** Not busywork, but tasks that connected the
  man to something beyond the violence. Repairing a building.
  Teaching a skill. Tending animals. Work that reminded him he
  was more than a weapon.
- **Witness.** Someone who knew what happened and did not flinch
  from it. Not a confessor, not a therapist — just a person
  who could sit beside the broken man and not look away.
  Shield-brothers served this function. So did Dalla, in her way.
- **Story.** Eventually, converting the raw experience into
  narrative. This took time. A man could not tell his story
  until he had enough distance to shape it. Premature telling
  was re-traumatization. Late telling was calcification.
  The window was narrow and individual.
- **New bonds.** Forming new connections after loss. This was
  the hardest. A man who had lost his shield-brother and
  refused all new bonds was choosing isolation over the
  vulnerability of attachment. The band could not force this.
  It could only make the offer.

### What Does Not Heal

- **Pretending it did not happen.** The Norse cultural expectation
  of silent endurance worked for mild damage and failed
  catastrophically for severe damage. A man who suppressed
  everything eventually broke — and broke worse than if he had
  cracked earlier.
- **Drink past the threshold.** Moderate drinking medicated
  anxiety and loosened the hamr enough for release. Heavy
  drinking added a second problem to the first and accelerated
  decline.
- **Further violence.** Fighting did not cure the damage from
  fighting. It compounded it. Men who sought battle as a cure
  for their distress were accelerating their own destruction.
- **Isolation.** A man who withdrew from the band lost access to
  every coping mechanism the culture offered. The fire, the
  mead, the saga-telling, the witness of companions — all of it
  required proximity. The man who walked away from the fire
  walked toward his own end.

### Resilience Factors

Not every man broke. Some factors predicted who would endure and
who would shatter:

- **Prior exposure with recovery.** A man who had survived
  earlier trauma and found his way back was more resilient than
  one facing it for the first time. But this was not linear —
  each subsequent trauma drew from a diminishing reserve.
- **High WIL baseline.** Strong-willed men endured more before
  damage manifested. They were also more likely to suppress
  damage until it emerged catastrophically.
- **Active shield-bond.** Men with living shield-brothers
  recovered faster and broke less often.
- **Belief framework.** Men with strong faith — in the gods, in
  wyrd, in the afterlife — had a structure for containing
  meaninglessness. The man who believed his dead companion was
  in Valhöll was better off than the man who believed in nothing.
- **Youth.** Young men recovered faster. They also broke faster.
  The same plasticity that allowed quick recovery made them
  vulnerable to deep initial damage.
- **Sense of agency.** Men who believed they had choices — even
  illusory ones — were more resilient than those who felt
  trapped. Ubbe, who is saving silver to disappear, has a
  resilience anchor that a man with no exit plan does not.

---

## Period-Accurate Terminology Reference

| Modern Term                        | Norse / Period Equivalent                | Usage Context                          |
| ---------------------------------- | ---------------------------------------- | -------------------------------------- |
| PTSD                               | hugsjúkr (mind-sick)                     | Long-term psychological damage         |
| Panic attack                       | hugflótti (mind-flight)                  | Acute overwhelm, loss of control       |
| Flashback                          | mara-ríðr (mare-riding), ógnar-minni    | Relived experience, waking or sleeping |
| Hypervigilance                     | vök-ástand (watch-state)                 | Constant alertness beyond need         |
| Emotional numbing                  | kjölnun (cooling/freeze)                 | Flattened affect, no emotional range   |
| Moral injury                       | vig-byrðr (killing-weight)               | Guilt/shame from acts committed        |
| Dissociation                       | hamr-slit (shape-slip)                   | Detachment from self or reality        |
| Startle response                   | felmtr (flinch)                          | Involuntary reaction to triggers       |
| Survivor's guilt                   | eftir-sök (the searching-after)          | Why him and not me                     |
| Combat stress reaction             | bardagi-sótt (battle-sickness)           | Immediate post-combat breakdown        |
| Complicated grief                  | harmr-bani (grief that kills)            | Grief that does not resolve            |
| Substance dependence               | mjaðar-þræll (mead-thrall)              | Functional alcoholism                  |
| Rage disorder                      | bráð-reiði (sudden-wrath)               | Disproportionate anger                 |
| Death-wish / suicidal ideation     | banvænn (death-expectant)                | Active or passive desire to die        |
| Psychopathy / operational numbness | dráps-ró (killing-calm)                  | Violence without emotional response    |
| Anxiety                            | ótta-hugr (fear-mind)                    | Persistent dread without clear cause   |
| Depression                         | þunglyndi (heavy-mindedness)             | Persistent low mood, loss of drive     |
| Resilience                         | hugsterkr (mind-strong)                  | Capacity to endure and recover         |
| Shield-bond (protective)           | skjaldvinr (shield-friend)               | Close combat partner, primary bond     |
| Recovery                           | hugbót (mind-mending)                    | Return to baseline function            |
| Breakdown                          | hugbrot (mind-break)                     | Complete psychological collapse        |

---

## The Leech and the Mind

### Dalla's Approach

Dalla does not treat the mind the way she treats wounds. She lacks
the tools and the cultural framework for direct psychological
intervention. What she does instead is observe, interpret, and
create conditions:

- **Observation:** She watches the band constantly. Changes in
  eating, sleeping, drinking, speaking, and interacting are
  diagnostic data. She knows each man's baseline behavior. When
  the baseline shifts, she notices.
- **Herbal support:** Valerian root for sleep. Chamomile for
  agitation. Birch-bark tea for persistent headache. These are
  not treatments for trauma — they are treatments for symptoms
  that, left unchecked, compound the damage.
- **Seiðr framing:** When a man is breaking, Dalla may frame it
  in supernatural terms: "Your fylgja is restless. We must make
  an offering." This gives the man a narrative that does not
  require him to admit weakness. He is not broken — his spirit
  is unsettled. The distinction matters enormously in a culture
  where admitting fear is social death.
- **Proximity without demand:** She sits near the troubled man
  without asking questions. She brings food without comment.
  She includes him in tasks without acknowledging his
  withdrawal. This is the closest thing to therapeutic presence
  that the 9th century offers.
- **Intervention threshold:** Dalla will speak directly when a
  man becomes dangerous to himself or others. She will go to
  Voss privately. "Ubbe cannot stand watch alone tonight."
  She does not explain further. Voss does not ask.

### The Band's Role

The band has no concept of mental health care. What it has is an
instinct for self-preservation that incidentally supports
psychological recovery:

- **Roster management:** Voss keeps damaged men off point and
  away from solo duties, not because of kindness but because
  an unreliable man in a critical position kills the band.
- **Fire inclusion:** A man who withdraws is drawn back to the
  fire by habit, by the captain's insistence on full muster at
  meals, or by practical necessity (warmth, food distribution).
  This means even withdrawing men maintain minimal social
  contact.
- **Saga reframing:** Gest tells the stories. When he tells of
  a battle that damaged a man, he tells the version where that
  man fought well. This is not kindness — it is cultural
  technology. The man hears himself described as competent and
  brave, which is incompatible with the internal narrative of
  failure that trauma produces.
- **Work assignment:** Keeping a damaged man busy with
  purposeful tasks. Not punishment details — meaningful work.
  Sharpening weapons, repairing gear, assisting Dalla with
  herb collection. Tasks that say "you are still needed."

---

## Differential Presentation by Character

How trauma manifests depends on who the person was before the
damage. The same event produces different patterns in different
men:

### High-WIL Characters (Voss, Petra, Dalla)

- Suppress manifestation for longer periods.
- When they break, the break is sudden and severe — the dam
  bursting rather than the slow leak.
- Recovery is possible if they can be reached, but reaching
  them requires trust they are reluctant to extend.
- They are most likely to suffer in silence until a catastrophic
  event pushes them past their threshold.

### Low-WIL Characters (Orm, Dagfinn, Lump)

- Show symptoms quickly and obviously.
- The band notices early, which paradoxically improves outcomes —
  intervention happens before calcification.
- Recovery is faster if the social environment is supportive.
- They are most vulnerable to permanent identity erosion because
  they had less identity-capital to begin with.

### High-TOU Characters (Snorri, Ketil, Kell)

- Physical hardship — marching, cold, hunger — does not compound
  their psychological damage as quickly. Their bodies do not
  betray them as fast.
- But physical resilience masks internal damage. They keep
  functioning when they should not, and the band assumes they
  are fine because they are still marching.
- When the physical resilience finally fails (age, accumulated
  injury), the psychological damage arrives all at once.

### Characters with Prior Trauma (Thorne, Ubbe, Snorri)

- Each new trauma draws from a smaller reserve.
- Trigger-landscapes become more complex and harder to navigate.
- Recovery takes longer each time, and the baseline after recovery
  is lower than before.
- They are the most likely to develop chronic conditions
  (killing-calm, permanent numbness, drink-need).

---

## Trauma and the Narrative

### What the Reader Sees

The reader never sees the word "trauma." They see:

- A man who used to joke at the fire sitting silent.
- Hands that shake when they should not.
- The way someone flinches at a door slamming.
- A conversation that stops because the man's eyes have gone
  somewhere else.
- A refusal to talk about what happened, accompanied by behavior
  that screams what happened.

### What the POV Knows

Voss, as primary POV, processes psychological damage through a
military commander's lens:

- "Can this man still fight?" — the primary question.
- "Is he a danger to the band?" — the secondary question.
- "Can I afford to lose him?" — the pragmatic calculation.

He does not think about what the man is feeling. He thinks about
what the man is doing and whether it will get someone killed.
His concern, when it surfaces, masks itself as tactical
assessment. "Ubbe is sitting apart again" is how Voss registers
that Ubbe is psychologically declining.

### What Gets Said Aloud

Almost nothing. A man might say:

- "Bad dreams." (Translation: I relive the killing every night.)
- "The ale doesn't work anymore." (Translation: I cannot escape
  what I have seen.)
- "I am tired." (Translation: Something in me has stopped.)
- "He was a good man." (Translation: I cannot stop seeing his
  face when he died.)

The gap between what is said and what is meant is where the prose
lives. The reader fills the gap. The characters never do.

---

## Interaction with Physical Wounds

Psychological and physical damage compound each other:

- A man with chronic pain from old wounds is more susceptible to
  psychological damage because his reserves are already depleted.
- A man with psychological damage heals physical wounds more
  slowly because he does not care for himself properly — he
  forgets to change bandages, does not eat enough, does not
  rest when he should.
- The combination of chronic physical pain and psychological
  damage is the specific condition of veteran mercenaries. Ubbe
  and Snorri carry both. Their bodies and minds are both damaged,
  and each makes the other worse.
- Dalla treats the physical damage because she can reach it. She
  watches the psychological damage because she cannot. The
  distinction shapes her character.

---

## Cultural Boundaries

### What the Norse Culture Cannot Say

- "I am afraid." A mercenary cannot say this and remain in the
  band. Fear before battle is acknowledged only through ritual
  (offerings, wyrd-reading) — never through speech.
- "I need help." The concept of asking for psychological help
  does not exist. A man may seek Dalla for herbs to sleep. He
  will never say "my mind is broken."
- "I cannot do this anymore." Desertion is the only exit. A man
  who says he cannot continue is saying he is leaving. There is
  no concept of "I need a break" within the mercenary structure.

### What the Norse Culture Permits

- Weeping at the fire, under cover of drink. Acknowledged by
  no one. Remembered by everyone.
- Silence that lasts days. Interpreted as "he is carrying
  something" rather than "he is weakening."
- Reckless courage that is actually death-seeking. Interpreted
  as heroism by those who do not look closely.
- Ritual mourning after a companion's death. This is the only
  sanctioned emotional release, and it is formulaic — three
  days of acknowledged grief, then the man is expected to
  function.

---

## Rendering Rules for Prose

1. Never use modern clinical terms. Use Norse equivalents or
   plain physical description.
2. Show behavioral change, not internal monologue about feelings.
   "Ubbe stopped sharpening his axe" teaches the reader more than
   "Ubbe felt depressed."
3. Let the reader diagnose. Provide symptoms. Do not provide labels.
4. Use the contrast between what a character says and what they do.
   Dialogue hides; behavior reveals.
5. Physical symptoms carry psychological weight: shaking hands,
   changed appetite, disrupted sleep, involuntary startle.
6. The band works as a diagnostic chorus. When three men are
   watching a fourth, the reader knows something is wrong before
   it is named.
7. Recovery, when it happens, is shown through the reversal of
   behavioral markers: the man rejoins the fire, eats with
   appetite, speaks unprompted, laughs at a joke.
8. Permanent damage is shown through permanent behavioral change:
   the man recovers function but is visibly different from who
   he was. Harder, quieter, or more brittle.
