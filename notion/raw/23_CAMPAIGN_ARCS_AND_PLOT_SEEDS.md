# Campaign Arcs and Plot Architecture

**Project:** Iron Ledger -- Mercenaries of the Rimevegr **Purpose:** Master
campaign-planning hub for the branching long-form saga. This document no
longer functions as a loose pile of seeds. It now serves as the command
spine for the full overhaul.

**Scope of the overhaul:**

- primary live years: Y312-Y315
- critical prequel pressure: Y311
- Y315 must function as a full endgame and aftermath year, not a short
epilogue
- hidden event detail continues to use `scripts/spoiler_codec.py` where
secrecy matters
- 23A remains the foundation and transition file; 23B carries the detailed
Y313 Deepholm war-phase build; 23C carries the later Y313 Long Dark and
horror-convergence aftermath; 23D carries the Y314 reconstruction,
fracture, and revelation phase; and 23E now carries the Y315 Iron Barrow
climax and aftermath

## Plot summary of the campaign

- **Y311 - The buried causes:** The crisis starts before the main story.
Tribute grows harsher, trade becomes a weapon, old outlawries and blood
debts stir again, and private losses begin to shape later loyalties. By the
end of the year, the region is already unstable, and the first wrong signs
around the barrows have appeared.
- **Y312 - The land divides:** The Black Axes spend the year moving through
convoy duty, patrol work, assemblies, ferry disputes, and food politics.
What looks like routine mercenary work reveals the real shape of the coming
conflict: one side gathering strength through tribute and fear, another
through roads, trade, and alliances, while quieter powers build influence
through debt and dependence. Strange weather, bad dreams, and uneasy graves
begin to gather into a pattern.
- **Y313 - Open war:** The rivalry breaks into campaigning around
Deepholm. Hosts are raised, supply lines become targets, harbors matter as
much as walls, and the fighting turns into a long grind of siege work,
attrition, and shrinking choices. The question is no longer who can win a
local dispute, but who will still have the strength to rule after the war.
- **Late Y313 - The Long Dark:** The war leaves behind hunger, desertion,
exhausted truces, and brittle rule. Then the deeper crisis steps out of
rumor. Patrols vanish, corpse lights appear, roads empty, and barrows open.
By winter, the living can no longer pretend that war and the dead are
separate problems.
- **Y314 - The truth surfaces:** The survivors try to rebuild with repaired
routes, renewed trade, fresh patrol contracts, and assemblies meant to
restore order. Instead, the evidence hardens. The outbreaks connect, the
Wardens gather proof, Dalla's visions deepen, and Thorne's condition points
toward an older design under the land. The Iron Barrow and the Galdr-Forge
emerge as the hidden center of the whole disaster.
- **Y315 - The final campaign:** Once the source is understood, there is no
partial answer left. The remaining powers have to form a working coalition,
reach the Iron Barrow, hold the ground above it, descend into the buried
system, and decide whether the thing below will be sealed, broken,
exploited, or allowed to break the land completely.

### Endings

- **Outcome I - The Ash Peace:** The buried threat is sealed and the region
survives under a damaged but workable peace. It is still a bitter ending:
too many people are gone, the cost cannot be hidden, and what remains has
to be carried rather than celebrated.
- **Outcome II - The Last Good Wall:** The land is saved, but only through
extreme sacrifice. The threat is contained, yet the people who do it are
broken, lost, or permanently marked, and the world that survives is one of
duty, grief, and hard endurance.
- **Outcome III - The Kingdom of Graves:** The deeper threat may be
  checked,
but human rule curdles into the real horror. Fear, hunger, coercion, and
debt become the shape of the new order, and the region survives only as a
harsher and more brutal place.
- **Outcome IV - The Open Veil:** The final attempt fails badly enough that
the land itself changes. The dead become a lasting force, settlements and
roads fail, and the Rimevegr stops being a place the living can rule on
their own terms.

---

## 1. Mission of This Overhaul

The goal is to build a campaign architecture that can support a massive,
branching, competence-driven war-and-horror saga across more than 6000
lines of planning material without collapsing into vagueness or
contradiction.

This chapter family must do six things at once:

1. preserve grim lore accuracy inside the Rimevegr's existing canon
2. model military and political action with strategic intelligence rather
than plot convenience
3. give captains, jarls, healers, spies, and galdr-workers believable
motives, limitations, and adaptations
4. keep the point-of-view hierarchy disciplined so the real plot vessels
are the people with leverage, competence, and consequence-bearing choices
5. support a gamebook-style branching object structure where one decision
leads to a different chapter-object later
6. drive toward four major outcome families: two hard, fatalistic good
endings and two dark endings where either the Veil or human savagery breaks
the land

This is not a heroic wish-fulfillment campaign. It is a harsh competence
saga. The people who survive do so by timing, logistics, nerve, memory,
reading men correctly, and paying the right costs before they become fatal.
Lump should not be treated as the default vessel for the main power plot.
He is best used as a secondary low-status lens for the bottom of the
mercenary chain, while Voss, Gest, Petra, Thorne, Dalla, and other
higher-leverage figures carry most of the strategic, political, and
supernatural weight.

---

## 2. Non-Negotiable Story Standards

### Grim Lore Accuracy

Nothing in this campaign structure should feel imported from a softer
fantasy. Law, custom, food pressure, oath logic, kin obligation, weather,
fear of shame, and the deniable supernatural must all remain grounded in
the setting bible and simulation data.

### Tactical and Strategic Competence

The important people in this story are allowed to be smart. Ordovast should
be terrifying because his campaign logic often makes sense. Sigrun should
be formidable because she understands systems, not because enemies become
foolish. The Pale Widow should be effective because she sees where timing,
rumor, and weak morale can do what armies cannot.

### Consequences Must Be Mechanical in Spirit

Even in novel-planning mode, outcomes should feel as if they emerged from
ledger pressure, supply strain, route control, injuries, law, and emotional
fracture. Victory that costs nothing is not a real branch.

### Branching Must Stay Legible

The branching structure must feel rich without becoming unreadable. Every
major choice should alter later political leverage, military position,
morale, personal trust, supernatural exposure, or survival odds in a way
that can be tracked cleanly.

### Point of View Must Follow Real Leverage

Do not default to Lump as the main vessel of the plot. He is the weakest
man in the band and should be used mainly when the story needs a
ground-level look at fear, rank, hunger, humiliation, camp labor, or the
underside of mercenary life.

The main campaign-driving viewpoints should usually belong to those who can
actually read, shape, or survive the power struggle: Voss for command
pressure, Gest for ledger reality and judgment, Petra for tracking and
loyalty strain, Thorne for curse and violence, and Dalla or other keyed
figures for the deeper supernatural line.

If a scene is about strategy, leverage, negotiation, oath, supply,
betrayal, or Veil interpretation, prefer the character who is closest to
the decision rather than the lowest-status bystander.

### Mystery Box Must Be a System, Not a Trick

Each major event should create more questions than it fully answers. The
reader or player should be encouraged to form theories, compare signs,
distrust surface explanations, and entertain multiple plausible meanings
before the story finally collapses those possibilities into truth.

This must be handled as a structural system:

- every major reveal should answer one live question while opening two or
three more dangerous ones
- clues should support multiple interpretations, not just one hidden answer
- political explanations, human lies, and genuine supernatural causes
should often overlap so the audience must think rather than merely wait
- mystery should deepen curiosity, not create randomness; the truth must
feel retrospectively inevitable once enough pieces are visible
- even when the answer arrives, it should usually create a larger and more
frightening frame around the world than the audience previously understood

The result should be active theory-building. People reading or playing the
campaign should keep asking not just "what happened," but "what does this
mean," "who benefits," and "what terrible version of the answer is still
possible."

---

## 3. Chronological War-and-Horror Spine

| Year | Narrative function    | Campaign pressure                                                          | Story use                                      |
| ---- | --------------------- | -------------------------------------------------------------------------- | ---------------------------------------------- |
| 311  | buried prequel year   | old bargains, outlawries, hidden grievances, first omens                   | flashbacks, revelations, unanswered debts      |
| 312  | positioning year      | contracts, the Allthing, weak alliances, first barrow signs                | slow-burn escalation and faction testing       |
| 313  | open war year         | Ordovast's march, Deepholm pressure, siege logic, winter backlash          | major competence-porn military phase           |
| 314  | revelation year       | reconstruction, faction fracture, Galdr-Forge truth, dead in motion        | irreversible branching into endgame conditions |
| 315  | endgame and cost year | Iron Barrow assault, sealing, aftermath, scarred survival, final reckoning | climax, resolution, and paid-for future        |

This gives the saga a clear rhythm:

- Y311 explains why the present is already loaded with dry tinder.
- Y312 arranges the pieces and teaches the reader how power really moves.
- Y313 proves what those systems do under military strain.
- Y314 reveals that even the winners have inherited something worse than
war.
- Y315 forces the land to pay the full price of whatever truth was
uncovered.

### Stable chronology anchor map

This is the locked year-by-year ladder for the overhaul. Later prompts may
add branching paths inside these periods, but they should not violate the
order of pressure.

#### Y311 — The buried year

Y311 is the hidden causal year. Ordovast hardens tribute logic and
mine-backed military pressure. Sigrun answers not with noise but with
roads, crossings, market leverage, and long-term preparation. The Pale
Widow expands her healer, debt, and rumor web quietly enough that most
people mistake it for charity.

At the personal level, Petra's sister is pulled into danger, Thorne's older
violence stops staying buried, Kell's debt habits congeal into fate, and
Voss starts to feel the first undeniable signs of age and limitation. At
the same time, the first deniable omens appear around barrows, dreams,
scars, and wrong weather. Nobody yet knows whether these are linked.

#### Y312 — The positioning year

Y312 opens with public motion on every front. Ordovast summons tribute,
Sigrun opens the spring trade road, and the Widow places agents and rumors
in circulation. The Black Axes take work and become useful enough to
matter.

The Allthing season then turns the invisible pressure visible. Contracts,
security, prestige, rivalry, bargaining, and insult all converge in
Deepholm. Neutrality weakens. In the cold months, debt, shelter,
winter-hall questions, and barrow disturbances turn politics into bodily
risk. Ordovast's southward move on Deepholm and Sigrun's refusal at the
gates make open conflict feel inevitable.

#### Y313 — The war year

Y313 begins with thaw exposing the dead from the failed siege and with
every serious power taking stock. Ordovast regroups ruthlessly at Grimholt.
Sigrun fortifies passes and levies for real war. The Widow consolidates
what debt and fear have already bought her. The band's own numbers reveal
exhaustion before battle even begins.

The summer and autumn phases must deliver full campaign logic: armed
diplomacy, collapsed peace-shields, southward march, assault at Deepholm's
gate, convoy strain, broken harvest, rationing, and winter attrition. This
is the year when human conflict consumes the strength needed to face what
is coming beneath the soil.

#### Y314 — The revelation year

Y314 begins as a recovery attempt. Dead are counted, refugees move,
political blocks realign, and leaders try to frame the war's outcome to
their advantage. But the barrow fields go quiet in a way that feels wrong
rather than safe. Petra's sister arrives, the Widow's price comes due,
Dalla's condition deepens, and Thorne finds evidence tying his curse to
something older and more precise.

By the later phases of Y314, the campaign must shift from recovery fiction
to terrible clarity. The question is no longer whether the region can
return to normal. The question is what truth lies beneath the dead
movement, who reaches it first, and what kind of damaged order might still
survive once it is known.

#### Y315 — The endgame and cost year

Y315 is where the architecture cashes every check it has been writing since
the first omens. The Iron Barrow opens fully, the region contracts behind
walls, the joint expedition descends, and the truth of the Galdr-Forge
becomes a lived reality instead of a rumor-chain theory.

This year must not feel like a postscript. It is the decisive year in which
the campaign determines who leads, who pays, who survives, what the land
remembers, and which of the four ending families becomes real. Even the
best ending should still feel scarred, local, and costly.

### Chronology rules for later prompts

- Every new chapter-object should attach to one of these year-pressure
blocks.
- If a new story beat contradicts the live data files, canon wins.
- Mystery-box revelations should arrive in sequence: first omen, then
pattern, then interpretation, then terrible confirmation.
- Personal arcs should intersect the public timeline instead of floating
beside it.

### Y311 prequel release rule

The Y311 layer should not be front-loaded as static lore. It should appear
in flashback shards, remembered conversations, ledger fragments, outlaw
parley, and omen echoes only when present pressure makes the memory useful.

Each Y311 reveal should do three things:

- explain a live tension in the current year
- deepen trust or mistrust around one key character
- open a larger question instead of merely closing the old one

### Y312 positioning doctrine

Y312 should function as a slow-burn competence year, not a random pre-war
blur. Most scenes should begin as contract work, road movement, escort
duty, guard service, bargaining, or provisioning pressure and only
gradually reveal the larger political and supernatural trap.

In practice, that means:

- contracts are not filler; they are the engine that moves the band into
new information and obligations
- Sigrun, Ordovast, and the Widow all test boundaries through practical
systems before risking open rupture
- early barrow evidence should remain deniable in isolation but alarming in
accumulation
- by the end of Y312, the band should know more than ever while having less
freedom than ever

### Allthing power-struggle doctrine

The Y312 assembly must work as a branching leverage market rather than a
single argument scene. Public speeches, guard duty, escort work, wrestling
fame, private bargains, and rumor traffic should all alter later winter
options and political memory.

Rules for the Allthing pass:

- no major actor tells the full truth in public
- every promise made at Deepholm should create either future access or
future vulnerability
- legal ritual matters because witness counts and public shame still matter
- the band should leave with more visibility, less innocence, and narrower
room to stay unowned

### Late Y312 winter-survival doctrine

Late Y312 should feel like convergence rather than downtime. Grain
shortage, weather closure, debt strain, outlaw desperation, and barrow
unrest should all compress into the same narrow seasonal corridor so the
band enters Y313 already weakened, marked, and partially committed.

Rules for this pass:

- winter decisions must trade one survival need against another
- shelter always carries a political price
- mercy and law should come under genuine material stress
- the dead should become harder to dismiss precisely as human systems
become less able to respond cleanly

### Early Y313 mobilization doctrine

Early Y313 should present war preparation as systems work: levies, grain,
screening patrols, road control, fortification, scout traffic, and
deception. The most dangerous people in this phase are the ones who can
count, predict, and prepare, not merely swing hardest.

Rules for this pass:

- every military promise should have a logistics tail
- route knowledge and witness networks matter as much as direct strength
- both Ordovast and Sigrun should appear strategically intelligent in
different ways
- the band must feel squeezed between survival contracting and war
alignment

### Mid-overhaul audit checkpoint

After Prompts 6 through 10, the architecture remains aligned with the live
canon baseline:

- Y311 through early Y313 still form a coherent pressure ladder
- the survival economy remains harsh enough to govern decisions
- the POV hierarchy still favors leverage-bearing figures for strategic
scenes
- Y314 and Y315 revelations remain protected for later payoff

This checkpoint is the clean handoff into the southward march and war-phase
object build.

### Southward march doctrine

The Y313 march phase must treat maneuver as its own kind of battle. Before
the main Deepholm assault, the campaign should show scouting, route denial,
wagon protection, pass control, and screening clashes that make the later
siege feel earned.

Rules for this pass:

- movement decisions should create or remove later tactical options
- supply strain must keep shaping what commanders dare attempt
- early clashes should reveal competence and friction, not settle the war
too soon
- the band should be important at the screen-line and route level, not as a
miraculous army-sized solution

### Decisive canon events that must survive every branch

Prompt 3 locks the event skeleton pulled from the live data. Future
branches may change viewpoint, emphasis, local outcomes, or who witnesses
the event, but they should not erase these anchors from the campaign
architecture.

#### Political anchors

- EVT_312_S02_002 — Ordovast summons tribute and establishes open coercive
pressure.
- EVT_312_S03_003 — Sigrun opens the trade road and defines the Compact's
style of power.
- EVT_312_S04_004 — the Pale Widow places her Kolvik agent and begins the
soft takeover model.
- EVT_312_U01_021 and EVT_312_U07_027 — the Allthing is proclaimed and then
convened at Deepholm.
- EVT_312_U10_030 — the Widow brokers hidden intelligence exchange under
the cover of diplomacy.
- EVT_312_W13_076 and EVT_312_W17_080 — Sigrun calls for allies while the
Widow exploits the standoff to annex ground through debt.
- EVT_313_U01_026, EVT_313_U08_033, and EVT_313_U15_040 — the war-cloud
Allthing collapses politically and morally, ending the illusion that speech
alone can contain the region.

#### Military anchors

- EVT_312_W12_075 — Ordovast's first real southward march must appear as
the end of plausible deniability.
- EVT_312_W16_079 and EVT_312_W20_083 — the first Deepholm standoff and
retreat define the conflict's opening campaign logic.
- EVT_313_U02_027 — Ordovast returns with a true war host, wagons, and
siege intent.
- EVT_313_U04_029 and EVT_313_U05_030 — Sigrun's defensive mobilization and
the southern-pass skirmish prove that both sides are now committed.
- EVT_313_U17_042 — the Battle of the Deepholm Gate is a non-negotiable set
piece in any serious branch structure.
- EVT_313_U10_035 and EVT_313_U18_043 — trade collapse and war inflation
must be treated as campaign events, not background decoration.

#### Supernatural anchors

- EVT_312_U03_023 and EVT_312_U11_031 — Dalla's black-river dream and the
barrow stench announce that the land is wrong before the full pattern is
visible.
- EVT_312_W11_074 and EVT_312_W15_078 — the Grave Wardens' plea and the
midwinter Veil flare establish the first undeniable warning phase.
- EVT_313_U07_032, EVT_313_U12_037, and EVT_313_U20_045 — Dalla's
escalation, the Feldwick dead, and the overwhelmed Wardens turn omen into
active threat.
- EVT_314_S07_007 — the barrow fields going quiet must be framed as more
ominous than open attack.
- EVT_314_SUP_009, EVT_314_SUP_010, and EVT_314_SUP_012 — the Galdr-Forge
vision, organized draugr behavior, and Gudrid's warning identify the true
crisis.
- EVT_314_SUP_013 through EVT_314_SUP_015 — alliance with the Wardens, the
Widow's artifact trade, and the Iron Barrow unsealing are the final
pre-endgame locks.
- EVT_315_SUP_001 through EVT_315_SUP_008 — the regional draugr surge,
Dalla's preparation, Thorne's acceptance, the assembled expedition, the
forge chamber, the unbinding, and the surviving cost are the true endgame
anchors and must shape every serious ending path.

### Event-use rule for the whole overhaul

A decisive canon event must do at least one of the following in the
finished campaign architecture:

- appear directly as a chapter-object
- trigger a branch split or state change
- reshape faction leverage, supply, law, or morale
- deepen the mystery-box by opening a more dangerous line of theory

If an event does none of these things in the outline, it has not yet been
used properly.

The detailed chronology groundwork for this pass now continues in
23A_Y311_TO_Y312_FOUNDATIONS.md.

---

## 4. File-Split Plan for the Overhaul

Because the finished campaign architecture will exceed 6000 lines, this
project must be written as a coordinated document family rather than one
swollen file. The main 23 document acts as the hub. The heavy planning work
belongs in the subdocuments.

| File                                    | Role                                         | Target size     | Core content                                                   |
| --------------------------------------- | -------------------------------------------- | --------------- | -------------------------------------------------------------- |
| 23_CAMPAIGN_ARCS_AND_PLOT_SEEDS.md      | master index and branch logic hub            | 400-900 lines   | mission, structure, routing rules, ending map                  |
| 23A_Y311_TO_Y312_FOUNDATIONS.md         | prequel pressure and opening year setup      | 1500-1800 lines | Y311 flashbacks, Y312 positioning, first fractures             |
| 23B_Y312_ALLTHING_AND_WINTER.md         | politics, neutrality failure, winter fallout | 1500-1800 lines | Allthing play, contracts, hunger, desertion, covert moves      |
| 23C_Y313_WAR_FOR_DEEPHOLM.md            | main military campaign volume-planning       | 1500-1800 lines | march, scouting, siege, withdrawal, tactical objects           |
| 23D_Y313_LONG_DARK_AND_TRUCE.md         | horror convergence and forced alliances      | 1500-1800 lines | dead patrols, silence, truce logic, morale collapse            |
| 23E_Y314_TO_Y315_ENDGAME_AND_ENDINGS.md | revelation, endgame, and final resolution    | 1500-1800 lines | reconstruction, forge truth, Iron Barrow, four ending families |

Additional subdocuments may be added later if one track grows too dense,
but no single planning file should be allowed to bloat into failure
territory.

---

## 5. Branching Chapter-Object Standard

The final architecture should be built from numbered chapter-objects rather
than loose prose summaries. Each object must be able to route into later
objects, carry state, and create meaningful downstream pressure.

### Object numbering system

Use a stable ID format:

- O311-F01 = Year 311 flashback object
- O312-P03 = Year 312 political-pressure object
- O313-W07 = Year 313 war object
- O314-R02 = Year 314 revelation object
- O315-E01 = Year 315 endgame object

Cluster letters should stay consistent across the overhaul:

| Cluster | Meaning    | Typical use                                                |
| ------- | ---------- | ---------------------------------------------------------- |
| F       | flashback  | buried Y311 cause, recovered memory, old testimony         |
| P       | political  | assembly scenes, bargaining, leverage shifts, law pressure |
| C       | contract   | mercenary work, escort, guard duty, survival jobs          |
| W       | war        | march, siege, ambush, skirmish, retreat                    |
| H       | horror     | omens, barrow incidents, dread escalation, dead movement   |
| R       | revelation | major truths, forge knowledge, identity exposure           |
| A       | aftermath  | burial, rationing, blame, regrouping, cost accounting      |

The number should be stable once assigned. Even if the prose order shifts
later, the object ID should not be casually changed, because the ID is part
of the campaign-routing map.

### Mandatory fields for every chapter-object

Every object should eventually define the following minimum structure:

- object ID and short title
- year, season, and approximate day window
- object class
- primary point of view chosen for leverage, not default familiarity
- core location and movement range
- canon event anchors that justify the object's existence
- open strategic situation
- immediate decision pressure
- who currently holds leverage and why
- competent options the characters can realistically see
- desperate, mistaken, or morally ugly options
- unlock conditions and blockers
- state changes caused by the object's resolution
- direct routes to the next valid objects
- mystery-box payload: what question is answered and what larger question
opens

### Route types

Not every connection between objects is the same. Use four route types.

#### Direct route

The next object is effectively guaranteed if the current scene resolves in
the expected way.

#### Branch route

A visible choice or tracked condition sends the story to one of multiple
later objects.

#### Shadow route

The player or reader may not realize a consequence has been set in motion,
but a later object unlocks or darkens because of it.

#### Convergence route

Different branches can rejoin at the same later object, but they must
arrive with different morale, alliances, injuries, suspicions, or resource
states.

### Object quality bar

A chapter-object is not valid if it is only a cool scene. It must do at
least three jobs at once:

1. move the campaign situation forward
2. change or test at least one live relationship or state variable
3. raise, complicate, or partially answer a mystery-box question

### Required state-touch rule

Prompt 5 will formalize the full state-flag system, but Prompt 4
establishes the rule now: each object must declare what it touches.

Typical touched areas include:

- faction trust or hostility
- treasury and food security
- band morale and cohesion
- injury load and battle readiness
- widow leverage, oath burden, or outlaw risk
- Veil pressure, barrow awareness, and revelation depth

### Standard object shell

Each object should read like a usable planning node rather than a paragraph
of vibes. The minimum shell is:

- ID and title
- chosen POV and why that character owns the scene
- setup and pressure
- choices or unavoidable responses
- consequence block
- route list
- mystery-box note

### Example of routing logic in practice

A political object at the Allthing might route into:

- a contract object if Voss accepts paying work
- a war object if peace breaks publicly
- a horror object if a barrow sign interrupts the negotiations
- an aftermath object if the band tries to stay neutral and loses leverage

This is how the campaign becomes a branching pressure web rather than a
simple sequence of scenes.

---

## 6. State-Flag and Branching Logic Framework

Prompt 5 formalizes the campaign-routing layer that sits beneath the
chapter objects. The story should not branch only because the writer feels
like taking a new turn. It should branch because pressure variables have
changed and now make some outcomes more plausible than others.

### Flag families

| Flag family              | What it tracks                                         | Typical examples                                                                                 |
| ------------------------ | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| band condition           | whether the company can actually absorb risk           | treasury_tier, food_security, morale_state, casualty_load                                        |
| faction alignment        | who trusts, fears, owns, or hunts the band             | grip_standing, compact_standing, widow_leverage, outlaw_heat                                     |
| personal arc state       | which internal loyalties and wounds are active         | kell_debt_stage, petra_sister_status, voss_command_strain, thorne_curse_stage, dalla_galdr_stage |
| supernatural pressure    | how close the region is to open Veil crisis            | barrow_awareness, veil_pressure, forge_knowledge, warden_cooperation                             |
| legitimacy and aftermath | whether survivors can build anything durable afterward | oath_burden, public_reputation, survivor_legitimacy, settlement_credit                           |

### Flag types

Use only three state styles unless a later system truly requires more
detail:

- **Tier flags:** low, rising, high, breaking
- **Boolean locks:** true or false conditions for whether something has
been learned, chosen, betrayed, or preserved
- **Stage flags:** escalating tracks for personal or supernatural arcs such
as dormant, active, severe, irreversible

This keeps the web legible while still allowing meaningful consequence.

### Core state domains that should drive most routes

#### Survival domain

These decide whether the band can choose freely or is cornered by need.

- treasury_tier
- food_security
- winter_shelter
- casualty_load
- morale_state

#### Political domain

These decide who offers work, who believes promises, and who closes doors.

- grip_standing
- compact_standing
- widow_leverage
- thing_honor
- outlaw_heat

#### Personal domain

These determine whether the band holds together under stress.

- kell_debt_stage
- petra_sister_status
- thorne_curse_stage
- voss_command_strain
- gest_ledger_integrity
- dalla_galdr_stage

#### Horror domain

These decide whether the region is still dealing with rumor or has crossed
into organized dread.

- barrow_awareness
- veil_pressure
- grave_warden_trust
- forge_knowledge
- iron_barrow_status

### Branching rules

Every chapter-object should update at least one major flag and may update
two or three secondary flags. Avoid empty scene transitions.

Use these routing principles:

- if survival flags collapse, the band accepts uglier work and loses moral
room
- if political standing polarizes, neutral routes narrow or disappear
- if personal arc flags worsen, betrayal, fracture, or sacrifice routes
unlock
- if supernatural pressure rises faster than knowledge does, panic and dark
outcomes become more likely
- if knowledge, trust, and cohesion rise together, the hard good endings
remain possible even when the cost stays severe

### Shadow-flag rule

Not all consequences should be visible right away. Some objects should
quietly advance hidden counters such as:

- widow_leverage
- thorne_curse_stage
- public suspicion
- forge_knowledge

These hidden shifts create delayed consequences and support the mystery-box
system without resorting to arbitrary twists.

### Ending-gate logic

The final ending families should be determined by state clusters rather
than one late binary choice.

- **Hard good endings** require some combination of strong warden
cooperation, real forge knowledge, preserved band cohesion, and survivable
regional legitimacy.
- **Dark human endings** emerge when political hatred, low legitimacy, and
scarcity outpace cooperation.
- **Dark Veil endings** emerge when supernatural pressure outruns
understanding, timing, and sacrifice discipline.

### Prompt 5 implementation rule

From this point onward, every major object written for 23B onward should
include:

- one primary route condition
- one or more touched state flags
- one note about what later content becomes easier, harder, or impossible

This is the minimum logic needed to keep the campaign architecture
coherent.

---

## 7. Authoring Rules for the Next Passes

- Prefer intelligent opposition over dramatic coincidence.
- Prefer pressure from food, weather, law, oath, injury, and logistics over
abstract destiny.
- Use flashbacks only when they answer a present-tense pressure point.
- Let political and military branches reshape personal arcs.
- Let personal failures reshape larger events.
- Keep the branch web readable enough that another writer could trace it
and use it without guessing.

## 8. Prompt 16 — Controlled flashback engine

Flashbacks in this campaign are not decorative backstory. They are timed
pressure-release devices that answer a present-tense question exactly when
that answer becomes dramatically useful.

### Core engine rules

- every flashback must be triggered by a live pressure point in the present
- each insert should answer one active question while opening a larger one
- flashbacks must return quickly to the present decision rather than stall
the campaign spine
- no reveal should undercut the late Y314 to Y315 truth pipeline
- Lump can witness consequences, but the key explanatory flashbacks should
stay with leverage-bearing characters unless the low-rank view is the point

### Approved flashback channels

| Channel                   | Best use                                                           | Typical carriers                     |
| ------------------------- | ------------------------------------------------------------------ | ------------------------------------ |
| witness memory            | old oaths, betrayals, assembly insults, command errors             | Voss, Petra, Gest                    |
| letter or ledger fragment | debt trails, false accounts, missing names, hidden obligations     | Gest, Petra, Widow-linked scenes     |
| seith or dream bleed      | omens, barrow echoes, shared dread, buried recognition             | Dalla and other touched witnesses    |
| confrontation recall      | blood-price history, old warbands, personal shame, outlaw bargains | Thorne, Voss, former comrades        |
| public testimony          | law-bound revelation under witnesses                               | Allthing, truce hall, council scenes |

### Release matrix

| Present-tense trigger                    | Flashback payload that may unlock                                                   | What must still remain hidden afterward              |
| ---------------------------------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------- |
| Ordovast tribute pressure in Y312        | old grievance chains, failed loyalties, prior coercive bargains from Y311           | the full endgame shape of the regional war           |
| Petra's sister or healer-debt pressure   | fragments of the southern trauma and why Petra's loyalty hardens the way it does    | the complete account of every survival compromise    |
| Thorne's hunters closing in              | his old name, the blood-price logic, and earlier violence that will not stay buried | the full Galdr-Forge truth and why his marks exist   |
| Dalla's shared visions and trance events | earlier omen echoes that prove the dead pattern predates open war                   | the exact center of the waking-barrow network        |
| the Iron Barrow approach in Y315         | the oldest hints that flesh and rune-work were once joined deliberately             | who precisely profited first from that buried system |

### Pacing rules for insertion

- use flashbacks at turning points, not as chapter openers by default
- prefer short, sharp shards over long explanatory scenes
- if a flashback does not alter the reader's reading of the current
decision, it should be cut
- one strong flashback after a major escalation is better than many weak
ones
- every inserted memory should tighten either pity, dread, blame, or
resolve

### Object-network rule

Flashback objects should keep the F-tag logic already established in the
chapter system.

- F objects feed into present objects; they do not replace them
- a flashback should usually route back into a current-year node within the
same dramatic sequence
- the engine exists to make the campaign feel inevitable in hindsight
without making it predictable too early

## 9. Prompt 17 — Major faction masterplans

The campaign now needs explicit long-game strategy for each major power. No
important faction should behave like a mood. Each one needs a coherent
plan, a fallback pattern, and a recognizable theory of how order is won.

### Masterplan doctrine

- every major actor should pursue a multi-season plan rather than reacting
scene by scene
- when a plan fails, the faction should adapt according to its nature, not
lose intelligence for the sake of plot
- public justification and private objective should often differ
- rival captains should think in food, pay, shelter, and honor first, then
in ideology if anything remains
- collisions between smart plans should create the best branches in the
campaign

### Masterplan matrix

| Actor                      | Public claim                                 | Real objective                                                                                  | Primary tools                                                         | Adaptive fallback                                                                     |
| -------------------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Ordovast                   | restore order and rightful tribute           | turn temporary dominance into permanent jarldom                                                 | tribute, fortification, fear, hired steel, public punishments         | buy proxies, purge dissent, force one last decisive alignment                         |
| Sigrun                     | preserve trade and lawful independence       | build the only durable regional order strong enough to outlast war                              | markets, roads, contracts, chartered defense, political legitimacy    | convert ceasefires and war footing into a governing framework                         |
| Pale Widow                 | heal, mediate, and keep routes open          | own the hidden leverage of debt, information, medicine, and later artifacts                     | healer network, agents, grain stores, black ledgers, secret bargains  | step from shadow influence into open power only once others depend on her             |
| Voss and the Black Axes    | stay paid and stay free                      | keep the band intact without being swallowed by larger powers, then choose the least fatal duty | contract selection, discipline, reputation, practical alliance-making | accept temporary command alignment only when the root threat leaves no neutral ground |
| Bryn and the Grave Wardens | protect graves and warn the living           | force the region to recognize the barrow crisis as a civilizational threat                      | evidence, ritual authority, specialist contracts, blunt warnings      | trade purity for sanctioned authority if that is what survival requires               |
| rival captains             | survive the season and profit where possible | convert chaos into territory, pay, prestige, or escape                                          | raiding, intimidation, switching sides, local oaths                   | defect, bargain, or fold into larger blocs when the dead change the math              |

### Ordovast masterplan

**Strategic theory:** order comes from submission, tribute, and the visible
cost of refusal.

**Year ladder:**

- **Y312:** test tribute, walls, and obedience while mapping which
settlements can be bent and which must be broken
- **Y313:** convert preparation into open campaign, siege pressure, and
legalized conquest masked as enforcement
- **Y314:** compensate for battlefield depletion through fear, hired bands,
and punishment politics
- **Y315:** offer one last bargain to competent survivors if direct
dominance is no longer possible

**Blind spot:** he understands power and coercion well, but repeatedly
underestimates how badly prolonged strain and supernatural threat can
hollow out obedience.

### Sigrun masterplan

**Strategic theory:** the side that keeps trade, law, and supplies
functioning will inherit the future even if it loses men in the present.

**Year ladder:**

- **Y312:** secure routes, market trust, and selective alliance options
without triggering war before the coast is ready
- **Y313:** defend in depth, preserve Deepholm, and let Ordovast spend more
than he can truly afford
- **Y314:** turn reconstruction, the Allthing, and the barrow tithe into
proof that legitimacy can still exist under pressure
- **Y315:** transform emergency coalition into the first real regional
command and then into durable governance

**Blind spot:** her system-building strength can drift toward cold
instrumentalism; people may follow her competence while still fearing what
permanent rule under it would cost them.

### Pale Widow masterplan

**Strategic theory:** the person who knows the hidden needs of the region
can own it without needing to wave a banner first.

**Year ladder:**

- **Y312:** place agents, gather debts, and turn private suffering into
future leverage
- **Y313:** let stronger factions bleed while quietly preserving the only
trade and healing channels still functioning
- **Y314:** reveal ledgers, open grain stores on terms, and make regional
dependence feel like relief
- **Y315:** secure access to forge knowledge and step into overt authority
only after her network has become indispensable

**Blind spot:** she tends to view people as positions in a web; that can
buy stability, but it also breeds the kind of resentments that survive long
after crisis ends.

### Voss masterplan

**Strategic theory:** survive first, stay unowned second, and only then
choose a fight worth losing people for.

**Year ladder:**

- **Y312:** take contracts that pay and inform while avoiding irreversible
capture by any single bloc
- **Y313:** preserve the band through competent war work, ration losses,
and refuse vanity engagements
- **Y314:** shift from pure mercenary survival toward selective
guardianship once the barrow threat proves regional and structural
- **Y315:** commit fully when neutrality becomes a lie and the root threat
has to be faced directly

**Blind spot:** his caution can look like emotional distance or refusal to
choose, which creates friction inside the band even when his reading is
correct.

### Bryn and the Wardens masterplan

**Strategic theory:** the dead do not care about faction pride, so the
living must eventually be forced into painful recognition.

**Year ladder:**

- **Y312:** warn quietly and gather proof without triggering useless panic
- **Y313:** escalate public warning as the count of dead and breaches rises
- **Y314:** push for tithe, sanctioned authority, and unified barrow
response
- **Y315:** convert specialist knowledge into the operational backbone of
the final expedition

**Blind spot:** the Wardens can sound like zealots before the evidence
becomes visible enough, which delays the recognition they most need.

### Rival captain adaptation rules

Rival bands should not share one mind, but they should all follow the same
harsh logic of professional survival.

- **Wulfgar and the Red Tide:** profit through fear until the dead make
fear less marketable than cooperation
- **Hadric and the Three Wolves:** rent loyalty to whichever power offers
food, authority, and sanctioned cruelty
- **Sura and the Bone Pack:** preserve kin loyalty and ancestral ground,
aligning only when oath terms remain honorable and survivable
- **remnant and neutral bands:** drift, defect, merge, or vanish when
winter, debt, and barrow pressure strip away their independence

### Collision map

The strongest branches should come from these masterplans hitting one
another:

- Ordovast's coercive jarldom against Sigrun's legitimacy-through-system
model
- the Widow's invisible sovereignty against everyone else's need to believe
they still rule themselves
- Voss's autonomy logic against the moral demand to finally choose a side
- Warden evidence against every leader's desire to postpone the truth until
it is cheaper
- rival captains choosing territory, profit, or survival in ways that
reshape the regional map from below

## 10. Prompt 18 — Band-member personal arc lattice

No important band member should feel detachable from the main campaign.
Personal arcs are not side quests. They are the human cost and
decision-pressure system that makes the larger war-and-Veil structure
matter.

### Lattice doctrine

- every core band member needs a campaign-facing pressure line, not just a
private wound
- each personal arc should intersect at least one political object, one
survival object, and one horror object
- personal beats must alter trust, timing, command, or access rather than
only adding emotion
- the band should feel more interdependent by Y315, not less, even when the
members are scarred or changed
- Lump remains secondary, but he still needs a meaningful
witness-and-belonging line

### Arc lattice overview

| Character | Core personal question                                                             | Campaign function                                          | Most important intersections                                   |
| --------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------- |
| Voss      | what does command owe the people who survive under it                              | command strain, strategic choice, moral cost               | contracts, truce logic, expedition charter, post-war future    |
| Gest      | can a man keep honest account in a world that survives by concealment              | ledger reality, truth-keeping, material consequence        | pay, famine, route math, survivor record                       |
| Kell      | can a man built for brute reliability become something more than a disposable wall | line-fighter dignity, sacrifice, earned self-worth         | debt pressure, chokepoints, endgame holding action             |
| Petra     | how long can care and loyalty survive when every system turns kin into leverage    | tracking, moral witness, kin duty, diplomacy under strain  | sister thread, Widow bargains, refugee and civilian protection |
| Thorne    | is he a hunted man, a weapon, or a person who can still choose his own use         | curse logic, blood-price, Galdr-Forge key role             | outlaw past, hunters, rune truth, sealing decision             |
| Dalla     | is she being consumed by the Veil or becoming the only bridge that can read it     | omen interpreter, shared dread carrier, ritual necessity   | visions, mass trance, barrow seals, forge closure              |
| Lump      | can the lowest-status man become proof that belonging is more than usefulness      | low-rank witness, emotional ground truth, survival texture | camp fear, command consequences, post-war continuity           |

### Voss line — authority under narrowing choices

- **Y312:** Voss tries to keep the band solvent without surrendering its
freedom
- **Y313:** command strain becomes visible as every smart choice still
costs men, sleep, or trust
- **Y314:** he shifts from avoiding entanglement to accepting partial
guardianship of the region because neutrality is no longer honest
- **Y315:** his final test is whether he can lead people into a necessary
descent without treating them as expendable tools
- **Best use:** strategy scenes, hard refusals, quiet command aftermath,
and the question of what the Black Axes become once the war is over

### Gest line — the ledger against comforting lies

- **Y312:** tracks short pay, hidden strain, and the first signs that
numbers are already lying to the proud men using them
- **Y313:** war cost turns him into the keeper of unwelcome truth about
stores, wounded burden, and who can actually last the season
- **Y314:** his counts become civic and regional rather than merely
band-local, making him one of the people who can prove recovery or collapse
honestly
- **Y315:** he becomes the recorder of what the victory really cost and
whether the survivors are building on truth or myth
- **Best use:** ration scenes, council briefings, audit moments, and
post-battle reckonings where the emotional truth lands through arithmetic

### Kell line — from closed wall to chosen stand

- **Y312:** Kell's debt habits and silence create distrust, but his
reliability in danger keeps him indispensable
- **Y313:** he becomes the blunt instrument that keeps the band alive
during the hardest fighting, even as his humanity remains mostly hidden
- **Y314:** barrow work and pressure around Thorne force him into clearer
acts of chosen loyalty rather than passive obedience
- **Y315:** the gate-holding and last-stand logic should pay off his arc by
showing that he is not just a weapon but a man choosing what kind of life
he is defending
- **Best use:** chokepoints, aftermath silence, gestures of loyalty, and
scenes where action says what dialogue never will

### Petra line — kin duty inside collapsing systems

- **Y312:** the first letters and rumors about her sister make every
southern and trade-facing job emotionally loaded
- **Y313:** survival duty and family duty collide as the band cannot spare
clean rescue energy during open war
- **Y314:** the Widow's favor and her sister's return force Petra into
morally difficult choices around secrecy, debt, and care
- **Y315:** her line resolves not by forgetting the past but by choosing
what kind of protector she will be in the new order
- **Best use:** witness scenes, refugee and healer moments, negotiations
where compassion and steel sit in the same hand, and any branch where the
civilian cost needs a human face

### Thorne line — hunted past to chosen instrument

- **Y312:** old names and old enemies begin surfacing before the band fully
knows why he watches the dark the way he does
- **Y313:** blood-price pressure and the Long Dark make his past impossible
to keep partitioned from the group's survival
- **Y314:** the bone tablet and barrow work prove that his marks belong to
a much deeper history than mere feud or curse gossip
- **Y315:** his line resolves at the forge, where the question is no longer
what he is, but whether he can choose how that buried making is used
- **Best use:** pursuit scenes, tense confessions, rune discoveries, and
any node where human guilt and supernatural destiny must overlap

### Dalla line — from omen-bearer to necessary bridge

- **Y312:** her dreams and unease remain deniable enough that many can
still call them nerves, weather, or misfortune
- **Y313:** shared visions and bodily changes make her impossible to
ignore, even for those who do not trust seith
- **Y314:** she becomes one of the only people who can interact with the
barrow system without simply dying or going mad
- **Y315:** the final burden is to let her matter without turning her into
a pure plot device or saint; she should remain human even while acting as a
bridge
- **Best use:** dread confirmation, ritual preparation, quiet recovery
scenes, and moments where knowledge itself costs the knower something

### Lump line — witness, belonging, and the underside of survival

- **Y312:** keep Lump mainly at the band-floor level — hunger, humiliation,
labor, fear, and the question of whether he earns his place
- **Y313:** let him witness what command decisions look like from below
without making him the strategic center of the story
- **Y314:** he becomes useful as a proof-of-belonging line; if the band
survives, even a man like Lump has a place in that survival
- **Y315:** his late function is emotional continuity and the lived proof
that the endgame is about preserving a human world, not just sealing a
mechanism
- **Best use:** camp texture, aftershock perspective, small acts of care,
and rare low-rank scenes that make the cost of survival concrete

### Relationship cross-wiring rules

- Voss and Gest should function as command judgment versus material truth
- Petra and Thorne should intersect where kin duty, secrecy, and
danger-to-others overlap
- Kell and Voss should pay off trust through positioning and shared danger
rather than speeches
- Dalla and Thorne should intersect as two different forms of unwanted
chosen-ness
- Lump should most often illuminate the consequences of decisions made by
others rather than originate the core strategy line

### Payoff requirement for later prompts

When building contracts, set-pieces, intrigue, and endings later, check
whether at least three of these personal lines are being advanced by the
same event. If not, the event is probably too detached from the band that
is supposed to live it.

## 11. Prompt 19 — Contract-to-arc conversion layer

Mercenary work is the main engine that gets the band from one year-phase to
the next. Contracts should never feel like filler jobs between "real" plot
beats. They are how the real plot reaches the band.

### Conversion doctrine

- every contract must pay at least two story debts at once: survival money
and structural movement
- paid work should always alter one or more of these: alignment,
information, enemies, trust, route access, or exposure to the Veil problem
- the same contract can begin as practical labor and end as political or
horror revelation; that transformation is desirable
- if a contract could be removed without changing later leverage, it is not
yet connected tightly enough to the campaign spine

### Contract conversion map

| Contract type               | Surface reason to accept                           | Hidden campaign function                                                              | Typical outcomes                                           |
| --------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| escort                      | get paid to move people or goods safely            | reveals route pressure, faction alignment, ambush logic, and who still controls roads | new patrons, new enemies, intelligence, supply strain      |
| patrol or garrison          | winter shelter, steady silver, local standing      | ties the band to one settlement's politics and makes neutrality harder to maintain    | civic trust, obligation, resentment, territorial knowledge |
| tribute or debt enforcement | fast pay and favor with stronger powers            | forces moral choices about law, coercion, and who the band is really serving          | honor strain, command tension, faction reputation shifts   |
| barrow-clearing             | rare high pay, emergency need, specialist prestige | converts rumor into direct horror proof and moves the band toward the Forge line      | casualty risk, Warden alliance, Veil escalation            |
| convoy or grain protection  | food, silver, and goodwill                         | makes logistics visible as the real battlefield beneath speeches and raids            | road control, famine mitigation, rival interference        |
| rescue or retrieval         | personal motive wrapped in paid duty               | fuses private arc pressure with regional conflict                                     | kin loyalty shifts, secrecy, altered strategic commitment  |

### Year-by-year contract ladder

#### Y312 — contracts as intelligence and alignment sorting

In Y312, the band should still believe work can stay local and practical.
That illusion matters.

- early escort and patrol jobs reveal which roads are safe, which
settlements can still pay, and which factions are quietly preparing for
trouble
- assembly security and hall-duty work at the Allthing convert reputation
into political visibility
- winter garrison offers turn food and shelter into alignment traps
- even small jobs should tell Voss and Gest who is buying more iron, grain,
tar, or silence than a peaceful year would explain

#### Y313 — contracts as war commitment by increments

In Y313, the contract layer should show how bands slide into war not only
through banner oaths but through practical necessity.

- screening patrols and road-watch jobs become pre-battle intelligence work
- emergency escort of civilians or stores becomes de facto military service
- siege-adjacent work blurs the line between hired support and open
allegiance
- post-siege survival contracts reveal that victory itself creates new
dependency

The key design rule is that the band should feel itself becoming part of
the war before anyone says plainly that neutrality has already died.

#### Y314 — contracts as civic reconstruction and barrow emergency

In Y314, paid work should show the region trying to function again while
the supernatural crisis makes ordinary recovery unstable.

- patrol contracts around settlements become proofs of which local law
still works
- Warden jobs convert the band from mere sellswords into emergency
specialists
- grain-route protection reveals how much power now sits with whoever
controls food
- any contract involving Petra's sister, the Widow's healers, or Thorne's
past should bind the personal lattice directly into regional restructuring

#### Y315 — contracts become chartered duty and endgame mandate

By Y315, the language of "contract" should begin changing into charter,
vow, command mandate, or expedition share.

- the band is no longer just hired muscle; it is a necessary operational
unit in the final coalition
- payment still matters, but legitimacy, sacrifice, and post-war standing
now matter equally
- endgame work should feel like the highest and last transformation of
mercenary labor into public duty

### Conversion rules for chapter objects

When creating a contract object later, test it against this checklist:

1. **Who is paying, and what hidden pressure does that reveal?**
2. **What does the band learn that it could not have learned at a council
table?**
3. **Which personal arc gets tightened by taking the job?**
4. **What later war, political, or horror node becomes possible because
this job happened?**
5. **What price is paid even if the contract succeeds cleanly?**

If a contract object cannot answer all five, it needs deeper integration.

### Contract-state outputs to preserve

Paid jobs should regularly feed these persistent states:

- contract_reputation
- route_access_state
- local_trust
- faction_alignment_pressure
- treasury and food runway
- barrow_awareness or Veil exposure
- personal arc heat for Voss, Petra, Kell, Thorne, Gest, Dalla, or Lump

### Final rule

The band does not reach the Iron Barrow by destiny. It gets there because
years of paid work, bad roads, winter bargains, escort duty, failed
neutrality, and barrow contracts slowly turn one mercenary ledger into the
region's most useful surviving instrument.

## 12. Prompt 20 — Tactical set-piece library

The campaign now needs a reusable library of military set-pieces that can
recur across branches without feeling repetitive or generic. These are not
only big battles. They are the tactical situations that repeatedly test
command, formation discipline, weather judgment, and the cost of bad
positioning.

### Set-piece doctrine

- every set-piece should revolve around terrain, timing, fatigue, and
numbers, not heroic exemption from consequences
- battles should solve one problem while worsening another
- the same tactical form may recur in different years, but with altered
moral or logistical meaning
- the band should matter as a decisive small unit, not as an army-sized
miracle
- aftermath and casualty accounting are part of the set-piece, not separate
fluff

### Core battlefield families

| Family                | What it tests                                                         | Why it belongs in the campaign                                      |
| --------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------- |
| screening skirmish    | scouts, route sense, initiative, false retreat discipline             | determines who reaches the main fight informed or blind             |
| convoy pressure fight | wagon spacing, rear guard control, civilian panic management          | makes logistics visibly equal to battle                             |
| choke-point hold      | shield order, endurance, rotation discipline, nerve under pressure    | lets small bands decide outsized outcomes credibly                  |
| raid and counter-raid | speed, signal use, local knowledge, withdrawal judgment               | shows that war is also theft, pressure, and message-making          |
| siege-sector clash    | repair work, focused violence, reserve timing, engineering under fear | anchors the Deepholm competence-porn phase                          |
| retreat under contact | discipline after failure, not just before it                          | proves whether commanders can preserve a future after a lost moment |
| barrow breach fight   | terror control, ritual timing, confined-space combat                  | blends military realism with the horror ladder                      |

### Library of recurring set-pieces

#### SP-01 — Southern Pass screening clash

- **Typical year:** Y313 early campaign
- **Best carriers:** Voss, Petra, Thorne
- **Situation:** outriders, scouts, and light shield groups fight for ridge
sight, road access, and the right to force the other side onto worse ground
- **Core choice:** pursue incomplete success or preserve force for the main
body
- **Best use:** before major marches, when maneuver itself should feel
dangerous

#### SP-02 — Grain convoy under pressure

- **Typical year:** Y312 winter or Y314 shortage months
- **Best carriers:** Gest, Petra, Voss
- **Situation:** food carts, river shipments, or mule trains move through
terrain where every delay or theft has strategic consequence
- **Core choice:** save the cargo, the escorts, or the civilians caught in
the crush
- **Best use:** when the story needs to show that famine is a battlefield
condition

#### SP-03 — Hall and gate defense by rotation

- **Typical year:** Y313 siege or local winter defense
- **Best carriers:** Voss, Kell, Bjorn-adjacent witness
- **Situation:** defenders must hold wood, hinge, wall, or narrow entry
while tired, cold, and short of spare men
- **Core choice:** when to rotate, when to sally, and when to abandon pride
for survival
- **Best use:** any node where shield discipline matters more than raw
bravery

#### SP-04 — Marsh or treeline ambush response

- **Typical year:** any year from Y312 to Y314
- **Best carriers:** Petra, Thorne, low-rank witness secondarily
- **Situation:** hidden archers, boggy footing, broken sightlines, and
confused calls turn a routine movement into a survival problem
- **Core choice:** freeze and locate, push through, or fall back and lose
the route
- **Best use:** escort contracts, hostile-road chapters, and rival-band
pressure

#### SP-05 — Harbor-side scramble

- **Typical year:** Y313 Deepholm phase
- **Best carriers:** Gest, Petra, harbor witness
- **Situation:** cargo, berths, fire, and defenders all compete for too
little space while commanders are tempted to fixate on the main gate
instead
- **Core choice:** save the wall fight or save the supply artery that lets
the wall endure
- **Best use:** when logistics and battle must be shown as one system

#### SP-06 — Night raid with political consequences

- **Typical year:** Y312 or Y314
- **Best carriers:** Voss, Petra, rival-captain witness
- **Situation:** a strike on stores, boats, or sleeping fighters may be
tactically smart but politically ruinous depending on who ordered it and
who saw it
- **Core choice:** take the easy tactical win or preserve future legitimacy
- **Best use:** where law, witness pressure, and dirty warfare intersect

#### SP-07 — Ordered retreat through narrowing ground

- **Typical year:** Y313 aftermath or Y315 collapse phase
- **Best carriers:** Voss, Kell, Bryn-facing witness
- **Situation:** the force must pull back without turning fear into rout
while the enemy or the dead keep steady pressure on the exit
- **Core choice:** who holds last, what gets abandoned, and what future the
retreat preserves
- **Best use:** to prove that survival competence can be as dramatic as
attack

#### SP-08 — Barrow breach interior fight

- **Typical year:** Y314 or Y315
- **Best carriers:** Thorne, Dalla-adjacent witness, Kell
- **Situation:** confined stone, wrong echoes, limited light, ritual
windows, and enemies that do not behave like living raiders force a
different kind of combat logic
- **Core choice:** press toward the objective, protect the ritual worker,
or extract before panic becomes annihilation
- **Best use:** when the war library needs to merge fully with the
supernatural ladder

### Reuse rule for later branches

A set-piece may recur in more than one branch only if at least two of these
are changed each time:

- terrain
- who holds initiative
- what the band is trying to protect
- what personal arc is being tightened
- what political cost success or failure will create

### Integration rule

Every major battle or action scene added later should declare:

- which set-piece family it belongs to
- what state values it changes
- what later object it unlocks or closes
- which band member's arc it sharpens

If a combat scene cannot answer those four questions, it is spectacle and
should be reworked.

## 13. Prompt 21 — Political intrigue library

The campaign needs a parallel library for non-battle competence. Intrigue
in this setting should not mean courtly cleverness detached from material
reality. It means witness control, debt leverage, fosterage bargains,
hostage logic, rumor discipline, hidden payments, and law theater performed
by people who know that winter and steel will judge the result.

### Intrigue doctrine

- every intrigue scene should move leverage, not only reveal personality
- public law and private coercion should often occur in the same sequence
- bargains matter most when each side is competent and has something real
to lose
- hidden finance, kin obligation, and witness pressure should feel as
dangerous as blades
- intrigue wins must always create later obligations, not clean escape

### Core intrigue families

| Family                            | What it tests                                            | Why it matters                                             |
| --------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------- |
| public law theater                | witness management, speech discipline, shame, precedence | determines what can be justified openly later              |
| debt and favor bargaining         | hidden need, private leverage, selective mercy           | powers the Widow, Petra, and Gest-centered strain lines    |
| hostage or fosterage exchange     | trust under duress, kin pressure, future obedience       | shows how peace and coercion blur in a harsh society       |
| counterintelligence and rumor war | who knows first, who lies cleanly, who can verify        | turns information into regional power                      |
| truce-room negotiation            | enemy competence under shared pressure                   | keeps war logic human and strategic rather than cartoonish |
| covert finance and provisioning   | silver, grain, medical stores, tariffs, transport rights | proves politics is built on supply, not speeches alone     |

### Library of recurring intrigue set-pieces

#### IP-01 — Allthing speech under false peace

- **Typical year:** Y312 or Y314
- **Best carriers:** Gest, Petra, Sigrun-facing witness, Voss secondarily
- **Situation:** public forms still hold, but every word spoken under
witness is a move in a larger leverage struggle
- **Core choice:** win the room now or preserve usable relationships for
winter
- **Best use:** assemblies, legal claims, debt exposures, and reputation
turning points

#### IP-02 — Debt settlement in private

- **Typical year:** any year, strongest in Y312 and Y314
- **Best carriers:** Gest, Petra, Widow-linked witness
- **Situation:** a healer debt, pay discrepancy, transport fee, or
emergency grain bargain quietly decides who will owe whom when the next
crisis lands
- **Core choice:** accept humiliating dependence now or risk material
failure later
- **Best use:** to translate money, medicine, and hunger into enduring
political ownership

#### IP-03 — Hostage, fosterage, or kin surety exchange

- **Typical year:** Y312 tension build or Y314 stabilization attempt
- **Best carriers:** Petra, Voss, settlement elders, family-facing
witnesses
- **Situation:** peace or safe passage is guaranteed not by trust but by
putting a valued person where betrayal will hurt later
- **Core choice:** what human bond is worth risking to buy short-term order
- **Best use:** when alliances need to feel costly and embodied rather than
abstract

#### IP-04 — Quiet rumor placement

- **Typical year:** any year, strongest for the Widow and rival captains
- **Best carriers:** Gest, Petra, market witnesses, hidden agents
- **Situation:** a carefully planted story reshapes hiring, fear, or blame
without anyone being able to prove where it began
- **Core choice:** exploit a useful lie or keep the record clean and lose
leverage
- **Best use:** to show how power moves through halls, ferries, healers,
and trade routes

#### IP-05 — Truce table with knives still on belts

- **Typical year:** Y313 winter or Y314 autumn
- **Best carriers:** Voss, Bryn, Petra, Sigrun- or Ordovast-adjacent
witness
- **Situation:** enemies meet because worse forces press outside the room,
but every sentence still tests pride, survival, and whether the agreement
can outlast hunger
- **Core choice:** settle for a narrow workable peace or overreach and
break the room
- **Best use:** forced truces, ceasefires, and emergency coordination under
dread

#### IP-06 — Hidden ledger exposure

- **Typical year:** Y314 especially
- **Best carriers:** Gest, the Widow, law-facing observers
- **Situation:** someone produces records of tribute, bribes, missing
stores, or false accounts and turns numbers into a weapon more powerful
than an accusation alone
- **Core choice:** expose the truth fully or reveal only enough to buy
advantage
- **Best use:** where legitimacy, corruption, and memory collide under
public witness

#### IP-07 — Provision-right negotiation

- **Typical year:** famine or siege periods
- **Best carriers:** Gest, Petra, Sigrun-facing or Widow-facing witnesses
- **Situation:** grain, boats, road passage, stable space, or healer access
is allocated through bargaining that looks administrative but decides life
and death
- **Core choice:** preserve fairness or buy loyalty through selective
access
- **Best use:** to prove that logistics and politics are the same argument
in different clothing

### Intrigue-state outputs to preserve

Political and covert scenes should regularly feed these states:

- allthing_legitimacy
- widow_leverage
- compact_standing and grip_standing
- outlaw_heat
- local_trust and witness_reputation
- debt_obligation_map
- hidden_information_access
- truce_stability and future council viability

### Integration rule for later chapters

Every intrigue object should answer four questions:

1. **What leverage changes hands here?**
2. **Who now owes, fears, or distrusts whom more than before?**
3. **What material consequence follows from the words spoken?**
4. **Which later war, contract, or horror node does this bargain prepare?**

If the scene only sounds clever but does not change those things, it is not
yet real intrigue for this campaign.

## 14. Prompt 22 — Supernatural escalation ladder

The Veil progression now needs to be structurally explicit. The horror line
must move from deniable sign to regional emergency to civilizational threat
in a way that steadily changes how politics, war, and ordinary survival
function.

### Escalation doctrine

- each step up the ladder should remove one more comforting explanation
- supernatural events must change practical behavior: route choices, law,
spending, alliances, and command decisions
- the dead should remain uncanny and feared even when they become more
visible
- revelation should widen the frame of danger rather than simplify it
- the climax should feel earned because every earlier rung prepared the
land for it

### The seven-rung ladder

| Rung | Name                      | Typical signs                                                                     | Social effect                                                 |
| ---- | ------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| 1    | wrongness and omen        | bad dreams, odd frost, dead livestock, humming stones, wrong river visions        | people argue, deny, pray, and quietly alter routine           |
| 2    | deniable incidents        | isolated barrow stink, a few restless dead, unexplained illness, seith unease     | Wardens are taken more seriously, but only locally            |
| 3    | pattern recognition       | repeated incidents across regions, Dalla's visions, linked signs, missing patrols | leaders begin comparing notes and fearing a shared cause      |
| 4    | active dead pressure      | dead patrols, breached barrows, corpse lights, organized movement                 | travel, trade, and small-settlement confidence start to break |
| 5    | measurable Veil crisis    | confirmed thinning, mass visions, multiple breaches, failed wards                 | politics can no longer treat the threat as fringe or private  |
| 6    | revelation of the source  | Galdr-Forge truth, network logic, Iron Barrow identification                      | the crisis becomes historical and systemic rather than random |
| 7    | endgame breach or sealing | regional draugr surge, final descent, closure or failure at the root              | determines whether the land survives scarred or breaks open   |

### Ladder by year phase

#### Y311 to early Y312 — omen layer

This is the stage of wrongness without consensus.

- dreams, strange weather, livestock death, and old marks should feel
disturbing but still arguable as coincidence, shame, curse, or harsh season
- Dalla and the most sensitive witnesses notice more than others, but they
do not yet possess enough proof to command obedience
- the correct mood is unease, not spectacle

#### Late Y312 — denial begins to fail

By the Allthing and winter convergence, the audience and the sharper
characters should realize the signs are no longer isolated.

- Grave Warden warnings gain weight
- the midwinter flare and repeated incidents establish that the dead
pattern is regional
- politics still tries to treat the matter as secondary, which is part of
the tragedy

#### Y313 — active dread and organized dead

War weakens the living precisely when the dead begin acting in more
coordinated ways.

- dead movement, silence on roads, mass visions, and the Long Dark all
harden omen into territorial threat
- the horror line now changes logistics directly: fewer messengers, weaker
roads, more ration panic, harsher truces
- by the end of Y313, competent actors should understand that the problem
is no longer local burial unrest

#### Y314 — proof and historical revelation

The key transition in Y314 is from feared pattern to evidence-backed truth.

- barrow quiet becomes ominous rather than reassuring
- breaches, tablet evidence, Dalla's barrow contact, and measurable Veil
thinning reveal that the crisis is structural and old
- the Galdr-Forge line changes the meaning of every earlier omen by proving
the region sits on a connected buried system

#### Y315 — root confrontation

The final year turns the full ladder into lived reality.

- the dead surge, the Iron Barrow is identified, and the final expedition
is planned not as a gamble but as the only remaining competent answer
- the forge confrontation determines whether the ladder ends in containment
or in a deeper opening that would remake the region permanently

### Effect on human systems at each rung

| Domain             | Early ladder effect                                   | Late ladder effect                                                                     |
| ------------------ | ----------------------------------------------------- | -------------------------------------------------------------------------------------- |
| law                | warnings and burial taboos are easy to ignore         | assemblies, truces, and councils are forced to legislate around the dead               |
| trade              | certain routes become unpopular or "unlucky"          | supply lines close, prices spike, and grain control becomes sovereign power            |
| military logic     | odd reports are dismissed as nerves                   | force posture, patrol design, and coalition command now revolve around barrow response |
| religion and seith | practitioners are feared or mocked in unequal measure | seith, warding, and Warden evidence become operational necessities                     |
| morale             | whispers, tavern stories, uneasy sleep                | open dread, fatalism, desertion, and the need for public proof of hope                 |

### Integration rule for horror objects

Every horror or revelation object added later should state clearly:

- which rung of the ladder it belongs to
- what human system it destabilizes
- whether it increases fear, knowledge, or both
- what later rung it helps unlock

If a supernatural scene is creepy but does not move the ladder, it should
be cut or folded into a stronger node.

## 15. Prompt 24 — Final master branching outline

The campaign hub now needs one final consolidation layer: a clean numbered
network that shows where the main route lives, what states control
movement, and where sequel or prequel pressure can still enter without
breaking the spine.

### Consolidation doctrine

- the hub should describe routing clearly enough that another writer can
pick up any year-phase without guessing where authority lives
- 23A through 23E should remain the year-owner files, while this document
holds the command map and cross-links
- every late branch should still resolve through tracked state rather than
mood alone
- prequel hooks should explain the present, and sequel hooks should grow
from the scars of Y315 rather than ignore them

### Master numbered object network

| Node | Narrative function                  | Primary owner  | Core objects or focus                                               | Main route output                                                     |
| ---- | ----------------------------------- | -------------- | ------------------------------------------------------------------- | --------------------------------------------------------------------- |
| N01  | buried pressure and positioning     | 23A            | Y311 grudges, Y312 contracts, early barrow signs, Allthing pressure | alignment, debt, and omen states are established                      |
| N02  | open-war commitment                 | 23B            | O313-U01 through O313-U04                                           | the band and region are forced into declared military posture         |
| N03  | war cost becoming social fracture   | 23B            | O313-A01 through O313-A04                                           | victory, attrition, blame, and supply strain destabilize the map      |
| N04  | Long Dark convergence               | 23C            | O313-H01 through O313-H04                                           | forced truces, dead movement, and dread turn war into shared crisis   |
| N05  | reconstruction under false calm     | 23D            | O314-R01 and O314-R02                                               | civic recovery and political positioning resume under hidden pressure |
| N06  | proof and revelation                | 23D            | O314-R03 through O314-R05                                           | the Galdr-Forge and barrow-network truth become undeniable            |
| N07  | endgame muster and descent          | 23E            | O315-E01 and O315-E02                                               | the coalition commits to a final competent answer                     |
| N08  | forge hinge and irreversible choice | 23E            | O315-E03 and O315-E04                                               | seal, mis-seal, sacrifice, or exploitation determine the ending lane  |
| N09  | return, memory, and settlement      | 23E            | O315-E05 and O315-E06                                               | the surviving political order takes shape                             |
| N10  | final outcome family                | hub resolution | Ash Peace, Last Good Wall, Kingdom of Graves, Open Veil             | the campaign resolves into its lasting world-state                    |

### Cross-link rules between the nodes

- N01 must always feed N02 with enough alignment pressure that neutrality
has a material cost
- N02 and N03 together should determine whether the band reaches N04
fractured, cohesive, indebted, or politically exposed
- N04 must feed N05 and N06 by proving the dead have changed the rules of
travel, law, and alliance
- N06 is the last major truth gate; once crossed, the story should not
return to ordinary-war assumptions
- N07 and N08 are the decisive hinge for all four endings
- N09 decides whether victory becomes governance, oligarchy, vendetta, or
merely temporary breath before the next age of trouble

### State dependency ladder

The master outline depends most heavily on four state clusters.

| State cluster           | Primary flags                                                                                | Story job                                                          |
| ----------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| human legitimacy        | council_legitimacy, local_trust, widow_leverage, truce_stability                             | decides whether people can cooperate without immediate collapse    |
| war survival            | route_access_state, harvest_security, treasury, expedition_readiness                         | decides whether the living can still act competently at scale      |
| personal hinge pressure | voss_command_strain, petra_sister_status, thorne_autonomy, dalla_burden, gest_ledger_control | ensures personal arcs keep reshaping the public story              |
| supernatural escalation | barrow_awareness, veil_pressure, forge_knowledge, iron_barrow_status, seal_integrity         | determines how close the region is to systemic ruin or containment |

### Final branch map

1. **N01 to N03** decide who still has enough trust, food, and cohesion to
survive the Long Dark.
2. **N04 to N06** decide whether the region reaches revelation in time and
in usable form.
3. **N07 to N08** decide whether the final coalition acts competently at
the decisive hinge.
4. **N09 to N10** decide what kind of scarred order inherits the cost.

### Prequel and sequel hooks to preserve

#### Prequel hooks

- Y311 outlaw bargains can still explain later betrayals, disappearances,
and old blood-price claims
- Petra's sister, Kell's debt history, and Thorne's buried violence should
keep feeding present-tense consequence rather than sitting as solved
backstory
- early Dalla omen scenes remain reusable as retrospective proof once the
Forge truth is known

#### Sequel hooks

- surviving councils may stabilize into real law or harden into brittle
emergency rule
- the Widow's network can become either a shadow safeguard or a softer form
of domination
- the Black Axes can evolve into wardens, free captains, or politically
dangerous veterans
- even with the seal holding, barrow monitoring, border watching, and truth
control remain fertile future-pressure lanes

### Final use rule

When writing any later chapter, start by identifying its node, then check
which state cluster governs it, then route forward only to the endings or
hooks that those states genuinely support.

## 16. Prompt 23 — The four final outcomes

The campaign must now support four fully defined top-level endings. These
are not flavor variants. Each one should emerge from accumulated state,
irreversible choices, and the kind of coalition or collapse built across
Y311-Y315.

### Outcome design rule

- no ending should be granted by one last sentimental choice alone
- each ending must preserve the cost ledger of the whole campaign
- the two good endings should still feel bitter, local, and scarred
- the two dark endings should differ clearly: one is a human political
hell, the other a true Veil catastrophe
- ending prerequisites should be legible enough that earlier objects can be
written toward them deliberately

### Outcome I — The Ash Peace

A hard, costly, but real survival ending. Civilization holds in damaged
form. The living remain compromised but not extinguished. The good here is
narrow, bitter, and paid for in blood, amputations, broken houses, and
remembered dead.

**Core prerequisite cluster:**

- forge is successfully sealed
- alliance cohesion holds long enough to avoid post-climax fragmentation
- casualty truth is kept broadly honest
- Sigrun, Voss, Bryn, and key survivors preserve a workable shared
legitimacy
- the Widow is influential but not allowed total covert capture of the new
order

**Irreversible turn points that support it:**

- Voss chooses sealing over glory or faction gain
- Thorne is treated as a person and key participant, not sacrificed as a
mere tool
- Dalla survives or is preserved with dignity rather than consumed as
expendable ritual matter
- the survivors choose hard governance and mutual burden over revenge
spirals

**Ending feel:**

- the region lives, but many halls are emptier forever
- the Black Axes adapt into something like sanctioned guardians with scars
and memory
- the council or equivalent order is fragile, real, and always one winter
from failure

### Outcome II — The Last Good Wall

A more sacrificial good ending. The best people spend themselves to keep
the worst thing contained. The region does not heal fully, but it does not
wholly fall. This should feel noble only from a distance; up close it is
exhaustion, bereavement, and duty without reward.

**Core prerequisite cluster:**

- the forge is sealed or locked down at extreme human cost
- one or more central figures are broken, lost, or permanently altered in
the act
- the alliance only partially survives politically, but the land itself is
spared the worst breach
- regional order remains thinner, poorer, and more defensive than in the
Ash Peace

**Irreversible turn points that support it:**

- the final ritual succeeds because someone accepts a burden that cannot be
undone
- surface forces hold just long enough for a retreat but at severe cost
- survivors choose containment and duty over comfort, wealth, or personal
rescue

**Ending feel:**

- there is safety, but not relief
- memory of the saved world belongs to the dead and maimed as much as the
living
- this is the "best people spent themselves" ending, not the "everything
worked out" ending

### Outcome III — The Kingdom of Graves

The dark human ending. Factions fail to cooperate, revenge outruns law, and
the region destroys itself through smart but merciless decisions that
become a collective murder machine. The Veil does not need to win because
men do its work for it.

**Core prerequisite cluster:**

- political legitimacy collapses before or after the Iron Barrow crisis
- alliances are broken for pride, revenge, debt extraction, or power
consolidation
- the forge threat may be contained only partially, but human predation
takes over the map
- the Widow, Ordovast-like successors, rival captains, or councils
weaponize scarcity and fear rather than ending them

**Irreversible turn points that support it:**

- truces are abused or broken at the exact moment common survival was
possible
- civilians are treated as provisions, leverage, or examples rather than
people to preserve
- post-climax secrecy and blame destroy the chance of shared governance

**Ending feel:**

- the barrows may quiet, but the land still enters a brutal age
- rule comes through fear, tribute, and managed starvation rather than open
apocalypse
- this is the ending where human systems prove fully capable of becoming
the horror

### Outcome IV — The Open Veil

The darkest ending. Supernatural breach outpaces political containment. Old
wards fail, the dead move in organized numbers, and the social architecture
of the Rimevegr begins to come apart faster than any captain can patch it.

**Core prerequisite cluster:**

- forge knowledge comes too late, is mishandled, or is exploited rather
than sealed
- Dalla, Thorne, or the Warden line is misused, ignored, or broken at the
wrong moment
- barrow pressure outruns coordinated response and the network opens
further instead of closing
- the final coalition cannot hold the hill, the chamber, or the retreat
long enough to restore order

**Irreversible turn points that support it:**

- greed for artifacts or control interrupts the sealing window
- command fragmentation breaks the expedition at the crucial hinge
- key warnings are denied until the network can no longer be contained
locally

**Ending feel:**

- the dead become a strategic reality, not a crisis event
- settlements empty, roads fail, and regional governance becomes impossible
- this is not mere defeat; it is a change in what kind of world the
Rimevegr is

### Final outcome routing summary

| Ending                | Seal state                    | Human order state                           | Moral tone        |
| --------------------- | ----------------------------- | ------------------------------------------- | ----------------- |
| The Ash Peace         | sealed successfully           | damaged but viable shared legitimacy        | bitter good       |
| The Last Good Wall    | sealed at terrible cost       | survives in defensive, grieving form        | sacrificial good  |
| The Kingdom of Graves | contained or partly contained | human brutality becomes the ruling system   | dark human        |
| The Open Veil         | failed or broken seal         | order collapses under supernatural pressure | dark supernatural |

### Integration rule for the final branches

Every late-Y315 branch should make clear which of these four endings it is
now moving toward and which state cluster is deciding that movement.

This file is now the fully consolidated campaign command document. The
year-owned expansions live in 23A through 23E, while this hub preserves the
master branch logic that ties them together.
