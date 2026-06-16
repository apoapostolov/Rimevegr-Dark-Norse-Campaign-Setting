# Political Villages — Lore Reference

Reference for writing and simulating the political landscape of Rimevegr
settlements. Covers how villages form unions, how jarls emerge, how feuds
escalate into wars, and how dark magic tilts the balance when manpower
fails.

This file is lore and narrative guidance. Mechanical rules are in
`20_SIMULATION_RULES.md` §18. Simulation script: `village_politics.py`.

---

## How Villages Work

### The Settlement as Organism

A Rimevegr village is not a political unit in any modern sense. It is a
cluster of families sharing a defensible position, a water source, and a
hall. The hall belongs to whoever can hold it. Usually a jarl, sometimes a
thane, sometimes just the man with the most fighters.

The village produces three things: food, people, and trouble.

Food comes from crops (short-season barley, turnips, kale), livestock
(sheep, goats, a few cattle), fishing, and foraging. The growing season is
sixty days. Everything else is preservation and rationing. A village that
cannot store enough food for 300 days of Long Dark is a village that will
lose people.

People come from births, which come from surviving women of childbearing
age. Infant mortality is brutal. A village of 80 might see 6-8 births in a
year and lose 2-3 of those before the first winter. Disease, cold, and
violence take the rest. A village grows slowly in peace and shrinks fast in
war.

Trouble comes from neighbors. Every village has land it claims, land it
uses, and land it argues about. The boundaries are marked by stones,
streams, and the memory of old men. When the old men die, the boundaries
move.

### The Seasonal Cycle

**Long Summer (Days 1-60):**

Planting, fishing, building, repairing. Every hand works. This is when
villages are richest and most vulnerable — the men are in the fields, not
on the walls. Raids during planting season are devastating because they
cost a year's food.

**Early Long Dark (Days 61-150):**

Harvest is in. Livestock culled to winter numbers. Preserved food stored.
This is the political season — men have time to argue, travel to gather
with other leaders, and plan. Most alliances are forged and most feuds are
declared between harvest and midwinter.

**Deep Long Dark (Days 151-300):**

Survival mode. Nobody raids in deep winter unless desperate. Villages
hunker down. Food stores shrink. Tempers shorten. Internal disputes peak.
Murders happen. The Long Dark kills more people through cabin fever and bad
decisions than through cold.

**Late Long Dark (Days 301-360):**

The thaw approaches. Remaining food is rationed hard. Scouts go out to
check passes and trade routes. Plans made in the political season are
executed or abandoned. War parties form. The cycle begins again.

### Village Economy

A village economy runs on three currencies: food, silver, and labor.

**Food** is the real wealth. Silver buys nothing if there is no grain to
sell. A village measures its health in stored food days — how long the
settlement can survive without new input. Anything above 200 days is
comfortable. Below 100 is dangerous. Below 60 is dying.

**Silver** circulates through trade, tribute, and contract payment. A
healthy village sees 8-20 silver per week in trade income. This pays for
tools, salt, iron, and mercenary protection. Silver leaves the village
through tribute to jarls, protection money to bands, and trade for goods it
cannot produce. Deepholm is the major exception: its daily market, mining
halls, and foundry move far more coin than a normal settlement, partly
because it is the only dependable source of galdr-grade silver wire.

**Labor** is the hidden currency. Every person in the village is a unit of
work. Children above ten work. The elderly work until they cannot. A
village cannot build, repair, plant, harvest, and defend simultaneously —
it must choose. Labor allocation is the jarl's real job.

### Proximity Economics and Political Pressure

Most Rimevegr politics begins as distance math. Villages trade most
intensely with the places close enough to reach within one or two days,
because those are the only partners who can deliver food, iron, salt,
charcoal, hides, or fighters before a local problem becomes a seasonal
crisis.

This creates natural pressure belts:

- **The fjord chain** -- Frostfjord Hollow, Kolvik, Stonebay, Skaldhaven,
and Ashen Reach exchange fish, boat repair, tar, relic traffic, and harbor
access. A quarrel here becomes a shipping problem for everyone.
- **The forest-border belt** -- Vargheim, Ashmark, Feldwick, and Ashen
Reach move charcoal, herbs, wagon timber, roots, wool, and rumor. When one
of these settlements is occupied or frightened, the whole belt gets poorer
and harder to trust.
- **The Deepholm basin** -- Deepholm, Thornwall, Raven's Perch,
Skaldhaven, and nearby carriers form the region's densest economic web.
Metal goes out. Food, wool, charcoal, ore, and labor come in. Whoever can
interrupt that loop can make war feel inevitable.
- **The moor survival circuit** -- Thornwall, Moor's End, Bleakwater, and
Grimholt trade sheep, peat, ferry access, levy bodies, and whatever grain
can be spared. It is the least profitable network and the most politically
brittle.

A village that controls a nearby crossing, pass, dock, kiln, mine, or
market does not merely become richer. It becomes necessary. In the
Rimevegr, necessity is the first stage of dominance.

### Population Dynamics

A village of 100 people might contain:

- 15-20 children under 10 (consumers only)
- 10-15 elderly or infirm (reduced labor)
- 25-30 women of working age (full labor, some fighters)
- 25-30 men of working age (full labor, primary fighters)
- 5-10 able fighters (men trained for war, not just strong farmers)

**Growth:** 5-8 births per year in a village of 100. Infant mortality
claims 30-40%. Net growth in a peaceful year: 3-5 people.

**Loss:** Disease, accident, violence, starvation, cold. A bad winter costs
5-10 people. A raid costs 3-15 depending on severity. A plague costs
20-40%. A famine costs 15-25%.

**Warriors:** Not every man is a fighter. A village of 100 produces about
8-12 men who can hold a shield wall. Training matters — a farmer with an
axe is not a huscarl. But in desperation, every able-bodied person fights.

**Warrior Breeding:** This is what it is. A village that wants fighters in
fifteen years needs women and surviving children now. Jarls who think in
decades encourage large families, protect pregnant women, and feed children
first. Jarls who think in seasons conscript everyone and wonder why the
next generation is thin.

---

## How Unions Form

### The Problem of Scale

A single village cannot defend against a determined enemy. Even Grimholt
with its stone walls and iron mine would fall if three villages combined
against it. The math is simple: 40 fighters cannot hold walls against 120
for more than a few days.

The solution is what the Rimevegr calls a **samband** — a binding together.
In practice: a mutual defense pact between settlements close enough to
reinforce each other within two days' march.

### What a Union Looks Like

A union is not a state. It has no constitution, no formal government, no
standing army. It is a web of oaths between leaders.

**Structure:**

- 3-6 settlements contribute fighters, food, and silver to a
common purpose
- One leader emerges as **overjarl** — the first among equals —
usually the one with the largest hall, the most fighters, or the strongest
personality
- The overjarl does not command the other settlements directly — he
leads the combined war-host and settles disputes between members
- Each settlement keeps its own jarl, its own economy, its own
internal governance
- The binding is seasonal — renewed each year at the **allthing**
(assembly of leaders) held after harvest

**What holds a union together:**

- Shared threat (another union, a large band, the Red Tide)
- Trade dependency (villages that need each other's goods)
- Kinship ties (intermarriage between leading families)
- Personal loyalty to the overjarl
- Fear of being outside the union when war comes

**What breaks a union:**

- The shared threat dissolves
- The overjarl demands too much (tribute, fighters, women)
- A member settlement is raided and no help comes
- Internal dispute over boundary, livestock, or women escalates
- The overjarl dies and no successor is agreed upon

### The Path from Union to Jarldom

A union that survives three winters starts to calcify. The overjarl begins
acting like a proper jarl. He collects tribute instead of requesting
contribution. He posts fighters in member settlements. He settles disputes
with authority rather than consensus.

If the member jarls accept this, the union becomes a jarldom — a territory
under one man's recognized rule. The old jarls become thanes, headmen,
reeves — subordinates.

If they resist, the union fractures. Sometimes violently.

The Rimevegr has seen this pattern hundreds of times. Most unions fail. The
ones that survive produce the great jarls — the Ordovasts, the Sigruns —
who rule because they turned a temporary alliance into permanent power.

---

## The Three Unions

### Comparative War Capacity

| Union             | Type     | Reliable fighters | Treasury base | Weekly inflow | War readiness | Core strength                                                   |
| ----------------- | -------- | ----------------- | ------------- | ------------- | ------------- | --------------------------------------------------------------- |
| Iron Grip         | Military | 40-55             | ~228 silver   | ~41 silver    | 2             | coercion, garrison discipline, tribute extraction               |
| Fjord Compact     | Economic | 75-95             | ~635 silver   | ~99 silver    | 1             | trade depth, logistics, metallurgy, allies with reasons to stay |
| Whispering Circle | Covert   | 20-49             | ~230 silver   | ~45 silver    | 1             | intelligence, sabotage, deniable influence, taboo arts          |

These numbers are not abstract. They determine how long each faction can
feed a levy, buy mercenary muscle, replace broken gear, survive a failed
harvest, or keep subordinate settlements loyal through a bad winter.

### The Iron Grip (Ordovast's Union)

**Overjarl:** Warchief Ordovast the Iron-Grip **Seat:** Grimholt (Large
Village, mountain stronghold, pop. 118)

**Member Settlements:**

- Grimholt (core — iron mine, 40-fighter garrison)
- Raven's Perch (mountain lookout, Thane Egil — subordinate)
- Bleakwater Landing (river crossing, Ferryman Olaf — vassal)
- Moor's End (moor hamlet, Elder Brosa — reluctant tributary)

**Force map and war finance:**

| Asset                     | Estimate                     | Notes                                                      |
| ------------------------- | ---------------------------- | ---------------------------------------------------------- |
| Population base           | ~241                         | small but tightly forced into war use                      |
| Fighters on paper         | ~53                          | most of the union's real striking power sits at Grimholt   |
| Treasury reserve          | ~228 silver                  | concentrated in Grimholt, not evenly shared                |
| Weekly trade/tribute flow | ~41 silver + 3 sheep monthly | includes Raven's Perch and Bleakwater payments             |
| Weekly upkeep burden      | ~28 silver                   | garrison, patrol, maintenance, food draw                   |
| Food stores               | ~350 person-days combined    | enough for pressure, not enough for a long failed campaign |

**Character:** Military. Ordovast rules through force and iron wealth. His
union is the most stable because it is the most controlled. He does not ask
— he demands. Settlements join because resisting is more expensive than
compliance.

**How the machine actually works:** Grimholt forges the nails, spearheads,
and fittings. Raven's Perch watches the passes. Bleakwater controls a
bottleneck no one respects until they need it. Moor's End provides the kind
of tribute that sounds small in council and feels catastrophic in a poor
household: sheep, wool, peat, sons for levy duty. The union's money is not
elegant money. It is squeeze-money.

**Political weakness:** Iron Grip looks stronger than it is because its
outer members obey from fear, not devotion. Ordovast can fund a campaign.
He cannot easily fund a long one without increasing tribute, and each new
tribute demand turns obedience into resentment.

<!-- SPOILER_START -->

乔乲乡乪乥乣乴乯乲乹为丠乏乲乤乯乶乡乳乴丠乩乳丠乢乵乩乬乤乩乮乧丠乴乯乷乡乲乤丠乷乡乲丮丠么乥丠乷乡乮乴乳丠乄乥乥买乨乯乬乭丧乳丠乳乭乩乴乨乩乥乳丠乡乮乤丠乔乨
乯乲乮乷乡乬乬丧乳丠买乡乳乴乵乲乥乬乡乮乤丮丠么乩乳丠乨乯乳乴丠乩乳丠乧乲乯乷乩乮乧丮丠么乥丠乩乳丠乲乥乣乲乵乩乴乩乮乧丠乓乶乡乲乴乨乩乲乤丠乢乡乮乤乳丠乡乳丠
乳乨乯乣乫丠乴乲乯乯买乳丮丠乗乩乴乨乩乮丠乡丠乹乥乡乲丬丠乨乥丠乷乩乬乬丠乭乡乲乣乨丮上上乗乥乡乫乮乥乳乳为丠乏乲乤乯乶乡乳乴丧乳丠乡乵乴乨乯乲乩乴乹丠乩乳丠买
乥乲乳乯乮乡乬丮丠么乥丠乨乡乳丠乮乯丠乨乥乩乲丠乴乨乡乴丠乴乨乥丠乯乴乨乥乲丠乳乥乴乴乬乥乭乥乮乴乳丠乲乥乳买乥乣乴丮丠义书丠乨乥丠乤乩乥乳丬丠乴乨乥丠乵乮乩乯
乮丠乳乨乡乴乴乥乲乳丮丠乍乯乯乲丧乳丠久乮乤丠乷乩乬乬丠乤乥书乥乣乴丠乩乭乭乥乤乩乡乴乥乬乹丮丠乒乡乶乥乮丧乳丠乐乥乲乣乨丠乷乩乬乬丠乲乥乴乵乲乮丠乴乯丠乩乮乤
乥买乥乮乤乥乮乣乥丮丠乂乬乥乡乫乷乡乴乥乲丠乷乩乬乬丠乳乥乬乬丠乡乣乣乥乳乳丠乴乯丠乷乨乯乥乶乥乲丠买乡乹乳丮

<!-- SPOILER_END -->

### The Fjord Compact (Sigrun's Union)

**Overjarl (de facto):** Jarl Sigrun of Deepholm **Seat:** Deepholm (Small
Town, industrial core, pop. 520)

**Member Settlements:**

- Deepholm (core — largest settlement, masterwork smithy, garrison)
- Thornwall (moor stronghold, Jarl Helga — proud ally)
- Kolvik (coastal shipwright, Harbour-Master Inga — trade partner)
- Skaldhaven (learning center, Lore-Keeper Audun — cultural ally)
- Ashmark (forest village, Reeve Torsten — buffer zone)

**Force map and war finance:**

| Asset                | Estimate                  | Notes                                                   |
| -------------------- | ------------------------- | ------------------------------------------------------- |
| Population base      | ~987                      | by far the largest pooled base in the region            |
| Fighters on paper    | ~91                       | includes Deepholm's garrison and Thornwall's levy body  |
| Treasury reserve     | ~635 silver               | enough to buy time, arms, transport, and outside blades |
| Weekly trade flow    | ~99 silver                | the strongest cash engine in the Rimevegr               |
| Weekly upkeep burden | ~62 silver                | expensive, but sustainable if routes remain open        |
| Food stores          | ~830 person-days combined | broadest survival cushion among the unions              |

**Character:** Economic. Sigrun does not conquer first; she prices,
subsidizes, equips, and binds. The Compact exists because her silver makes
cooperation more profitable than defection.

**How the machine actually works:** Deepholm turns ore and labor into
metal, tools, arms, and contract money. More importantly, its foundry and
galdr workshop together produce the region's only reliable galdr-grade
silver wire, which means higher warding and serious rune-repair depend on
Sigrun's town whether other jarls like that fact or not. Thornwall supplies
wool, meat, and a disciplined regional levy. Kolvik keeps hulls moving and
gets Deepholm silver to outside buyers. Skaldhaven adds legitimacy,
records, scribes, and the kind of learned prestige that makes agreements
feel older than they are. Ashmark works as buffer, infirmary, and quiet
exchange ground. Sigrun's real talent is not wealth by itself. It is
converting neighboring need into structured dependence without making the
dependence feel like chains.

**Political weakness:** This union is rich enough to arm for war but not
immune to fear. It depends on roads staying open, merchants believing
contracts will hold, and allies continuing to profit. One bad winter, one
tunnel failure, or one public humiliation at the Allthing can make
voluntary partnership feel suddenly optional.

<!-- SPOILER_START -->

乔乲乡乪乥乣乴乯乲乹为丠乄乥书乥乮乳乩乶乥丮丠乓乩乧乲乵乮丧乳丠买乲乩乭乡乲乹丠乧乯乡乬丠乩乳丠乴乯丠乣乯乮乴乡乩乮丠乏乲乤乯乶乡乳乴丠乷乩乴乨乯乵乴丠书乩乧乨
乴乩乮乧丠乨乩乭丮丠乓乨乥丠乩乳丠乡乲乭乩乮乧丠乔乨乯乲乮乷乡乬乬丬丠书乯乲乴乩书乹乩乮乧丠乴乨乥丠乭乯乵乮乴乡乩乮丠买乡乳乳丠乢乥乴乷乥乥乮丠乄乥乥买乨乯乬乭
丠乡乮乤丠乇乲乩乭乨乯乬乴丬丠乡乮乤丠乨乩乲乩乮乧丠乓乶乡乲乴乨乩乲乤丠乢乡乮乤乳丠乴乯丠买乡乴乲乯乬丠乴乨乥丠乢乯乲乤乥乲丮丠乓乨乥丠乷乯乵乬乤丠买乲乥书乥乲
丠乴乯丠乷乩乮丠乴乨乲乯乵乧乨丠乥乣乯乮乯乭乩乣乳丠仢亀五丠乳乴乲乡乮乧乬乩乮乧丠乇乲乩乭乨乯乬乴丧乳丠乩乲乯乮丠乴乲乡乤乥丠乢乹丠乵乮乤乥乲乳乥乬乬乩乮乧丠书
乲乯乭丠乄乥乥买乨乯乬乭丧乳丠乲乩乣乨乥乲丠乭乩乮乥乳丮上上义书丠书乯乲乣乥乤丠乴乯丠乷乡乲丬丠乳乨乥丠乨乡乳丠乴乨乥丠乮乵乭乢乥乲乳丠乡乮乤丠乴乨乥丠乷乥乡乬
乴乨丮丠乗乨乡乴丠乳乨乥丠乬乡乣乫乳丠乩乳丠乡乧乧乲乥乳乳乩乯乮丮丠么乥乲丠乡乬乬乩乡乮乣乥丠乩乳丠乶乯乬乵乮乴乡乲乹丮丠义书丠乴乨乥丠书乩乧乨乴乩乮乧丠乢乥乣
乯乭乥乳丠乥乸买乥乮乳乩乶乥丬丠乁乳乨乭乡乲乫丠乷乩乬乬丠乢乥乣乯乭乥丠乮乥乵乴乲乡乬丠乡乮乤丠之乯乬乶乩乫丠乷乩乬乬丠买乲乯乴乥乣乴丠乩乴乳丠乳乨乩买乳丮丠乔
乨乯乲乮乷乡乬乬丠乡乮乤丠乓乫乡乬乤乨乡乶乥乮丠乷乯乵乬乤丠乨乯乬乤丮上上乗乥乡乫乮乥乳乳为丠乖乯乬乵乮乴乡乲乹丠乡乬乬乩乡乮乣乥乳丠乢乲乥乡乫丠乵乮乤乥乲丠乴
乯乯丠乭乵乣乨丠买乲乥乳乳乵乲乥丮丠乓乩乧乲乵乮丠乣乯乮乴乲乯乬乳丠乨乥乲丠乭乥乭乢乥乲乳丠乴乨乲乯乵乧乨丠买乲乯乳买乥乲乩乴乹丬丠乮乯乴丠书乥乡乲丮丠义书丠买
乲乯乳买乥乲乩乴乹丠书乡乩乬乳丠仢亀五丠乩书丠乡丠乢乡乤丠乷乩乮乴乥乲丠乨乩乴乳丠乄乥乥买乨乯乬乭丧乳丠乭乩乮乥乳丠乯乲丠乡丠买乬乡乧乵乥丠乴乨乩乮乳丠乨乥乲丠
乷乯乲乫丠书乯乲乣乥丠仢亀五丠乴乨乥丠乃乯乭买乡乣乴丠乬乯乯乳乥乮乳丮丠么乥乬乧乡丠乯书丠乔乨乯乲乮乷乡乬乬丠乩乳丠乴乨乥丠乳乴乲乯乮乧乥乳乴丠乳乵乢中乪乡乲乬
丮丠乓乨乥丠乭乩乧乨乴丠乤乥乭乡乮乤丠乥乱乵乡乬丠乳乴乡乴乵乳丮丠乓乩乧乲乵乮丧乳丠乳乵乣乣乥乳乳乩乯乮丠买乬乡乮丠乩乳丠乵乮乣乬乥乡乲丮

<!-- SPOILER_END -->

### The Whispering Circle (Pale Widow's Union)

**Overjarl:** The Pale Widow (Jarl-Elect of Ashen Reach) **Seat:** Ashen
Reach (Large Village, forest hinge, pop. 142)

**Member Settlements:**

- Ashen Reach (core — pine tar, iron smelting, Pale Widow's hall)
- Frostfjord Hollow (Jarl Hrothgar — nominal ally, visibly hedging)
- Vargheim (Jarl Ulf Vargson — reluctant partner, distrusts soft hands)

**Force map and war finance:**

| Asset                | Estimate                  | Notes                                                              |
| -------------------- | ------------------------- | ------------------------------------------------------------------ |
| Population base      | ~394                      | middling size, scattered loyalties                                 |
| Fighters on paper    | ~49                       | far fewer reliably answer the Widow's call                         |
| Treasury reserve     | ~230 silver               | respectable, but politically unstable                              |
| Weekly trade flow    | ~45 silver                | tar, charcoal, fish, hides, ironwork                               |
| Weekly upkeep burden | ~27 silver                | lower than rivals because covert work is cheaper than open war     |
| Food stores          | ~420 person-days combined | enough to endure, not enough to absorb major disruption carelessly |

**Character:** The smallest and most dangerous union. The Pale Widow is
building power through intelligence, manipulation, selective patronage, and
the careful cultivation of fear. She has no true host and no appetite for
honest battlefield comparison. She prefers a political climate where other
people spend silver and blood while she spends information.

Hrothgar cooperates because the arrangement is profitable, deniable, and
useful against old rivals. Ulf cooperates because he values results and
because some threats disappear faster when he does not ask how. Neither man
belongs to her in the way Ordovast's subordinates belong to him. That makes
the Circle flexible. It also makes it treacherous.

**The Dark Arts:** The Pale Widow employs at least two practitioners of
arts that the other jarls consider taboo:

- **A seidr-worker** who communes with the dead and reads the Veil's
movements. Not galdr (rune-craft, which is accepted). Seidr — the woman's
magic that men fear and distrust. The practitioner lives outside Ashen
Reach in a cave that smells of burning herbs.

- **A curse-carver** who inscribes nithing-poles and ill-runes. This is
the art that other settlements would kill her for harboring. A nithing-pole
is a declaration of war on the spiritual plane — a horse's head on a stake,
carved with runes that call destruction on a named person or place. The old
jarls forbade it. The Pale Widow has used it before and does not advertise
the count.

- **Whisper-agents** — men and women placed in other settlements who
report back. Not fighters. Servants, traders, wandering healers, and useful
listeners. The Widow's war chest is partly silver and partly the fact that
she often knows who is desperate before they admit it aloud.
<!-- SPOILER_START -->

乔乲乡乪乥乣乴乯乲乹为丠乔乨乥丠乗乩乤乯乷丠乣乡乮乮乯乴丠乷乩乮丠乡丠乳乴乲乡乩乧乨乴丠乷乡乲丮丠乓乨乥丠乤乯乥乳丠乮乯乴丠乩乮乴乥乮乤丠乴乯丠书乩乧乨乴丠乯乮
乥丮丠么乥乲丠乳乴乲乡乴乥乧乹丠乩乳丠乴乯丠乷乥乡乫乥乮丠乢乯乴乨丠乲乩乶乡乬乳丠乵乮乴乩乬丠乯乮乥丠乣乯乬乬乡买乳乥乳丬丠乴乨乥乮丠乡乢乳乯乲乢丠乴乨乥丠买乩
乥乣乥乳丮上上乁乧乡乩乮乳乴丠乏乲乤乯乶乡乳乴为丠乳乨乥丠乩乳丠书乥乥乤乩乮乧丠乩乮乴乥乬乬乩乧乥乮乣乥丠乴乯丠乓乩乧乲乵乮丠乷乨乩乬乥丠乳乩乭乵乬乴乡乮乥乯乵
乳乬乹丠买乯乩乳乯乮乩乮乧丠乏乲乤乯乶乡乳乴丧乳丠书乯乯乤丠乳乵买买乬乩乥乳丠乴乨乲乯乵乧乨丠乡乧乥乮乴乳丠乩乮丠乂乬乥乡乫乷乡乴乥乲丮丠乎乯乴丠乬乩乴乥乲乡乬
乬乹丠买乯乩乳乯乮乩乮乧丠仢亀五丠乤乥乧乲乡乤乩乮乧丠乳乴乯乲乥乳丬丠乳买乯乩乬乩乮乧丠乧乲乡乩乮丬丠乣乲乥乡乴乩乮乧丠乳乨乯乲乴乡乧乥乳丠乴乨乡乴丠乬乯乯乫丠
乬乩乫乥丠乢乡乤丠乬乵乣乫丮上上乁乧乡乩乮乳乴丠乓乩乧乲乵乮为丠乳乨乥丠乩乳丠乥乮乣乯乵乲乡乧乩乮乧丠么乥乬乧乡丠乯书丠乔乨乯乲乮乷乡乬乬丧乳丠乡乭乢乩乴乩乯乮
乳丮丠乁丠乤乩乶乩乤乥乤丠乆乪乯乲乤丠乃乯乭买乡乣乴丠乩乳丠乡丠乷乥乡乫丠乆乪乯乲乤丠乃乯乭买乡乣乴丮上上乔乨乥丠乌乯乮乧丠乇乡乭乥为丠义书丠乢乯乴乨丠乵乮乩乯
乮乳丠乷乥乡乫乥乮丠乥乮乯乵乧乨丬丠乴乨乥丠乗乩乤乯乷丠买乬乡乮乳丠乴乯丠乯书书乥乲丠乨乥乲乳乥乬书丠乡乳丠乭乥乤乩乡乴乯乲丠仢亀五丠乴乨乥丠乮乥乵乴乲乡乬丠买
乡乲乴乹丮丠乆乲乯乭丠乴乨乡乴丠买乯乳乩乴乩乯乮丠乳乨乥丠乷乯乵乬乤丠乥乸乴乲乡乣乴丠乴乥乲乲乩乴乯乲乩乡乬丠乣乯乮乣乥乳乳乩乯乮乳丬丠乴乲乡乤乥丠乲乩乧乨乴乳
丬丠乡乮乤丠乬乥乧乩乴乩乭乡乣乹丠乴乨乡乴丠乳乨乥丠乣乡乮乮乯乴丠乥乡乲乮丠乴乨乲乯乵乧乨丠书乯乲乣乥丮上上乔乨乥丠乄乡乲乫丠乇乡乭乢乩乴为丠义书丠乴乨乥丠乣乯
乮乶乥乮乴乩乯乮乡乬丠买乡乴乨丠书乡乩乬乳丬丠乴乨乥丠乗乩乤乯乷丠乨乡乳丠乡丠书乩乮乡乬丠乯买乴乩乯乮丮丠乔乨乥丠乣乵乲乳乥中乣乡乲乶乥乲丠乣乬乡乩乭乳丠乨乥丠
乣乡乮丠乩乮乶乯乫乥丠乳乯乭乥乴乨乩乮乧丠书乲乯乭丠乢乥乹乯乮乤丠乴乨乥丠乖乥乩乬丠仢亀五丠乮乯乴丠乡丠乧乨乯乳乴丠乯乲丠乡丠乤乲乡乵乧乲丬丠乢乵乴丠乳乯乭乥乴
乨乩乮乧丠乯乬乤乥乲丮丠乔乨乥丠乗乩乤乯乷丠乨乡乳丠乮乯乴丠乡乵乴乨乯乲乩乺乥乤丠乴乨乩乳丮丠乙乥乴丮丠乂乵乴丠乳乨乥丠乨乡乳丠乮乯乴丠书乯乲乢乩乤乤乥乮丠乩乴
丮丠乔乨乥丠买乲乥买乡乲乡乴乩乯乮乳丠乡乲乥丠乵乮乤乥乲乷乡乹丮丠乔乨乥丠乮乩乴乨乩乮乧中买乯乬乥乳丠乡乲乥丠乢乥乩乮乧丠乣乡乲乶乥乤丮上上乗乥乡乫乮乥乳乳为丠
乍乡乮买乯乷乥乲丮丠乔乨乥丠乗乨乩乳买乥乲乩乮乧丠乃乩乲乣乬乥丠乨乡乳丠乢乡乲乥乬乹丠丳丵丠书乩乧乨乴乥乲乳丠乴乯乴乡乬丮丠义书丠乥乩乴乨乥乲丠乵乮乩乯乮丠乤乩
乳乣乯乶乥乲乳丠乴乨乥丠乗乩乤乯乷丧乳丠乯买乥乲乡乴乩乯乮乳丠乡乮乤丠乡乴乴乡乣乫乳丠乩乮丠书乯乲乣乥丬丠乁乳乨乥乮丠乒乥乡乣乨丠书乡乬乬乳丠乩乮丠乡丠乷乥乥乫
丮丠么乲乯乴乨乧乡乲丠乷乯乵乬乤丠乢乥乴乲乡乹丠乨乥乲丠乩乮乳乴乡乮乴乬乹丠乩书丠乴乨乲乥乡乴乥乮乥乤丮丠乕乬书丠乷乯乵乬乤丠乲乥乴乲乥乡乴丠乴乯丠乨乩乳丠乷乯
乬乶乥乳丠乡乮乤丠乣乬乯乳乥丠乨乩乳丠乧乡乴乥乳丮丠乔乨乥丠乗乩乤乯乷丧乳丠乳乴乲乥乮乧乴乨丠乩乳丠乴乨乡乴丠乮乯乢乯乤乹丠乨乡乳丠乣乡乵乧乨乴丠乨乥乲丠乹乥乴
丮

<!-- SPOILER_END -->

---

## Swing Settlements and Kingmakers

Not every settlement matters because it is large. Some matter because they
sit in the one place everyone eventually needs: the safe ferry, the
bad-weather landing, the neutral infirmary, the moor buffer, the haunted
edge where only one mad guide will go. These places do not dominate the
map. They tilt it.

### Feldwick — The Buffer No One Can Leave Alone

Feldwick is small, hungry, and currently occupied, but its political value
is far greater than its present strength. It sits between moor traffic,
sheep routes, and the zone where Thornwall's interests begin to overlap
with harsher northern pressure. If Feldwick were stabilized under friendly
rule, it could absorb raids, feed scouts, and blunt Ordovast's western
approach. If it remains broken, it stays a corridor for coercion.

Everyone therefore wants something different from Feldwick. Ordovast wants
it weak or compliant. Sigrun wants it unoccupied and economically tethered
to her allies. The Pale Widow wants it frightened enough to trade in
secrets. The villagers themselves would likely choose whoever restores seed
grain, predictable watch, and the right to sleep without mercenary boots in
the yard.

### Bleakwater Landing — The Crossing That Filters Power

Bleakwater's value is not wealth but control of passage. A settlement that
can barely feed itself still matters if messages, patrols, ore carriers,
and levy columns all need its ferry when weather or distance closes better
options. Whoever influences Olaf influences timing, and timing in the
Rimevegr often matters more than numbers.

Ordovast uses Bleakwater as a vassal bottleneck in his supply web. The
Widow sees it as an ideal listening post because everyone says too much
while waiting for a boat. Sigrun does not need to own it to benefit from
it, but she cannot ignore a crossing that can delay trade and quietly sort
rumor from truth.

### Ashmark — The Neutral Settlement Everyone Uses

Ashmark is not neutral because anyone respects neutrality as a principle.
It is neutral because too many powers need what it does: herbal care, tar,
forest access, quiet deals, and a place where wagons can stop without
openly declaring a side. That makes Ashmark a true kingmaker. It rarely
decides war with a banner. It decides war by opening or closing one gate,
treating one wounded messenger, or letting one convoy pass with no
questions asked.

If Torsten tilts fully toward Deepholm, the Fjord Compact gains depth and
safer movement through the forest edge. If he is bullied into silence or
captured by fear, the whole border belt becomes meaner, poorer, and easier
to poison with suspicion.

### Stonebay Hamlet — The Coast's Emergency Valve

Stonebay is politically invisible until weather turns bad. Then its beach,
shelter, and salvage rights suddenly become valuable to traders, fugitives,
smugglers, and anyone who needs to land where larger harbors are closed or
being watched. In peacetime it is a hamlet. In a crisis it becomes the kind
of place where a hidden arrival can change a season.

No union would waste a formal occupation on Stonebay unless the coast was
already contested. But every ambitious power would like a friendly elder
there, a cache on the beach, and first word of what the sea has delivered.

### Icebreak — The Margin of Politics and Terror

Icebreak does not matter in the normal arithmetic of food and silver. It
matters because desperate leaders still seek it out. Ragnhild's outpost
sits beyond sane commerce, but people travel there for warnings,
divination, last bargains, and answers they are ashamed to seek in public.
That makes Icebreak politically real without making it politically stable.

No faction can truly hold Icebreak for long. But access to it can shape
decisions made elsewhere. A jarl who comes back from the ice with a
prophecy, a relic, or a new fear may alter trade, levy plans, or marriage
bargains across half the region.

### Quick Leverage Map

| Settlement         | Why it matters                                      | Who courts it most                         | What flips it                                                |
| ------------------ | --------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------ |
| Feldwick           | moor buffer, food base, westward movement lane      | Sigrun and Ordovast                        | liberation, fresh occupation terror, seed-grain relief       |
| Bleakwater Landing | ferry timing, rumor filter, river choke             | Ordovast and the Widow                     | Olaf being threatened, bought, or replaced                   |
| Ashmark            | healing, forest access, quiet diplomacy             | Sigrun first, then everyone else           | convoy pressure, healer overload, forced closure of the gate |
| Stonebay Hamlet    | storm landing, covert coastal arrival, salvage      | Kolvik's traders, smugglers, hidden agents | wreck season, refugee landing, blocked main harbor           |
| Icebreak           | divination, taboo knowledge, edge-of-world prestige | desperate jarls and secret seekers         | prophecy, relic recovery, or panic from the ice              |

### The Political Rule

Large settlements wage wars. Small hinge settlements decide whether those
wars begin on schedule, arrive half-starved, or fail before they properly
start. Any serious regional struggle in the Rimevegr will eventually turn
on one of these places.

---

## Internal Fault Lines of the Three Unions

Most alliances in the Rimevegr do not break from enemy strength alone. They
break when hunger, insult, fear, and self-interest stop pointing in the
same direction. Each union therefore has a visible face and a hidden
fracture line.

| Union             | First likely crack                                    | Deepest fear                         | Most likely break trigger                                           |
| ----------------- | ----------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------------- |
| Iron Grip         | Moor's End in spirit, Raven's Perch in military value | looking mortal instead of inevitable | failed campaign, fresh tribute squeeze, visible defeat              |
| Fjord Compact     | Ashmark first, Kolvik second                          | trade confidence collapsing          | blocked roads, broken contracts, public humiliation                 |
| Whispering Circle | Frostfjord first, Vargheim second                     | exposure of taboo arts               | proof of seidr use, curse backlash, kin harmed by the Widow's tools |

### Iron Grip — Fear Behind Discipline

Ordovast's strength is concentration. His weakness is that everyone knows
where that strength lives. Grimholt is the fist. The outer settlements are
knuckles. If the fist misses, the knuckles begin wondering why they are
being broken for someone else's ambition.

Moor's End is the first place likely to fail in spirit. It is already
paying in sheep, fear, and endurance rather than belief. Bleakwater can be
bent by threat or coin from either side if Olaf thinks Ordovast's
protection is losing value. Raven's Perch is the most dangerous possible
defection, because Egil controls warning time and high-route visibility.
Ordovast's union holds so long as he looks like the future. One failed
offensive or one public retreat makes obedience feel negotiable.

### Fjord Compact — Prosperity Must Keep Feeling Real

Sigrun's alliance depends on profit being visible. Her people do not need
to love her, but they must continue to conclude that life near Deepholm is
safer, richer, and more predictable than life outside her orbit. That is a
strong bond, but it is still a bond made of expectation.

Ashmark is the first likely hedge point, because Torsten survives by
remaining useful to all sides. Kolvik could drift if war makes harbor trade
more dangerous than profitable. Thornwall is less likely to defect, but
Helga's pride is a real structural risk: if she feels treated like a
subordinate while bearing levy and sheep burdens, alliance strain turns
personal very quickly. The Compact does not fear battle most. It fears loss
of trust.

### Whispering Circle — The Alliance That Dies in Daylight

The Pale Widow's strength is that different people need different lies from
her. Its weakness is that those lies cannot survive equal scrutiny.
Hrothgar wants profit and flexibility, not damnation. Ulf wants practical
results, not open traffic with taboo arts. Both men can tolerate ambiguity.
Neither wants proof.

That makes Frostfjord the first public crack and Vargheim the first
potentially violent break. If one undeniable curse, dream-sending scandal,
or kin-targeted horror is traced back to Ashen Reach, the Circle loses the
protective fog it relies on. It is the union best able to unsettle its
enemies and the least able to survive exposure.

---

## Hostages, Fosterage, and Marriage as Statecraft

Open war is expensive. Kinship politics is cheaper. For that reason, most
long alliances in the Rimevegr are reinforced through children, marriages,
widow's property, and those household obligations that everyone pretends
are private.

### Fosterage Is Alliance Wearing a Child's Face

A foster-child sent to another hall is never just being educated. The child
is student, honored guest, soft hostage, future intermediary, and proof
that two households expect to share a future. If the relationship holds,
the fostered son or daughter grows into a living bridge. If it fails, the
same child becomes the sharpest moral knife in the room.

The practice is especially effective because it blurs affection and
leverage. People may truly grow to love the child they foster. That does
not make the bond less political. It makes it harder to break cleanly.

### Marriage Is Corridor, Contract, and Claim

Marriage among powerful households is rarely only about companionship. It
binds storehouses, ferry rights, grazing access, and inheritance
expectations. A bride may bring wool rights, a dowry chest, or a claim
route that suddenly makes a road worth defending. A groom may bring armed
protection, market access, or a name the other hall needs.

This is why marriage offers at the Allthing are so dangerous. They appear
to solve feuds while actually redrawing who will own future children, land,
and obligations. A refused offer is not just romantic disappointment. It is
public political insult.

### Widows Hold More Power Than Some Jarls Admit

A widow with land, servants, grain, or rights to a dead man's property can
become a political center overnight. She controls continuity. She can
remarry, refuse to remarry, foster out children, hold a hall together, or
sell protection piecemeal. The Pale Widow is simply the most visible
example of a deeper truth: in the Rimevegr, widow's property is strategy
wearing grief clothes.

### How the Three Powers Use Kinship

- **Ordovast** prefers blunt methods: sons fostered under supervision,
daughters traded to secure obedience, and household bonds that feel one
threat away from becoming hostage law.
- **Sigrun** prefers stable arrangements: fosterage, dowry,
contract-marriages, and practical widow settlements that keep roads,
workshops, and inheritance lines calm.
- **The Pale Widow** weaponizes ambiguity: offering refuge to widows,
delaying a marriage until it becomes leverage, or placing private
obligations where no one can attack them openly without looking
dishonorable.

### The Unspoken Rule

A village may reject tribute for a season. It is much harder to reject the
hall that raised your second son, married your niece, holds your widow's
claim, or fed your household in a winter when the Dry-Eyed were counting
children. That is why kinship politics outlasts many military victories.

---

## The People Beneath the Jarls

Jarls speak the loudest, but they do not control the region alone. Beneath
every hall is a second layer of political power held by people who are
harder to replace than a proud war-leader likes to admit.

### The Smith

A settlement without a competent smith is a settlement that borrows
survival from its neighbors. Weapons go dull, hinges fail, carts die, and
winter repair turns into public humiliation. That makes smiths political
figures whether they want the role or not. A master in Deepholm can
strengthen Sigrun's influence without ever leaving the forge. A skilled
worker in Ashen Reach can quietly refuse a commission and alter the tempo
of a feud.

### The Healer

Healers trade in obligation more than coin. Families whose children survive
fever, men whose wounds close clean, and women who live through hard births
all remember who made that possible. A healer's favor can steady a village
in crisis; a healer's warning can make an entire hall fear sickness,
poisoning, or curse-work. Ashmark's importance comes partly from exactly
this kind of soft authority.

### The Ferryman and Carter

Ferrymen, mule-masters, and road carriers decide which promises arrive in
time to matter. Ferryman Olaf is poor in silver but rich in leverage
because he controls a crossing others cannot ignore. A caravan-master who
chooses one route over another can enrich a market, starve a garrison, or
make one jarl seem better connected than he really is.

### The Lore-Keeper and the Scribe

Skaldhaven's influence proves that memory is political infrastructure. A
lore-keeper who preserves genealogies, boundary rulings, old grudges, and
barrow records can legitimize a claim or quietly weaken it. Scribes do not
carry shields, but they can turn rumor into precedent and convenience into
lawful custom.

### The Galdr-Worker

Galdr-workers sit in a strange place: feared, needed, and never fully
trusted. The person who can repair a ward-stone, verify a binding, or help
secure the Allthing grounds influences politics before the debate even
begins. Deepholm's strategic role is magnified by this. It does not only
make tools and silver wire; it helps decide whose protections are treated
as real.

### The Quiet Rule of Power

When a jarl ignores the smith, he loses iron. When he ignores the healer,
he loses confidence. When he ignores the ferryman, he loses timing. When he
ignores the lore- keeper, he loses legitimacy. When he ignores the
galdr-worker, he discovers too late that lawful ground and protected ground
are not the same thing.

---

## War Endurance and Campaign Logistics

Most Rimevegr leaders talk about courage and insult because those sound
noble. Wars are usually decided by less flattering things: fodder,
charcoal, ferry timing, pack animals, road maintenance, and whether the
grain convoy reaches the right hall before the snow closes.

### How Long Each Union Can Stay Dangerous

| Union             | Early strength                           | First likely shortage                             | Sustainable campaign profile                       |
| ----------------- | ---------------------------------------- | ------------------------------------------------- | -------------------------------------------------- |
| Iron Grip         | fast concentration of force              | food, outer-settlement loyalty, replacement labor | sharp offensive pressure, poor long-war resilience |
| Fjord Compact     | strongest pooled supply web              | road confidence, convoy safety, allied patience   | best defensive endurance and contracted response   |
| Whispering Circle | sabotage, deniability, low visible costs | trust, exposure tolerance, stable manpower        | thrives in disruption, weak in open holding war    |

### Iron Grip's Real Problem

Ordovast can mobilize faster than his rivals because his power is
centralized and his coercion is direct. But rapid mobilization is not the
same as long endurance. Grimholt can forge tools and arms. It cannot feed a
drawn-out regional campaign by itself. The more men Ordovast keeps in the
field, the more he must squeeze Moor's End, Bleakwater, and the roads under
his shadow. Each squeeze buys a week and loses a friend.

### The Compact's Strongest Weapon Is Continuity

Sigrun's strength is not battlefield fury but the ability to keep multiple
systems working at once: Deepholm's market, Thornwall's flocks, Vargheim's
charcoal, Kolvik's shipping, and Ashmark's neutral passage. That means the
Fjord Compact can endure a slow contest better than anyone else as long as
roads remain trustworthy and merchants believe contracts still mean
something.

### The Widow's Economy of Damage

The Whispering Circle cannot win a traditional supply contest against the
other two blocs. It does not need to. Its ideal campaign is one in which
roads close, sleep is lost, a convoy fails, a ferryman lies, a healer
becomes frightened, and everyone else spends twice as much silver to feel
half as safe. The Widow's strategy is cheaper than war because it makes
other people finance the panic.

### Roads, Water, and Seasonal Collapse

A single broken route can matter more than a lost skirmish. If the
Grimholt-Deepholm road becomes unreliable, prices jump and military
planning contracts. If Bleakwater's crossing fails, message speed and
resupply timing collapse. If Kolvik's harbor traffic slows, Deepholm's
silver and finished goods stop reaching wider buyers. In the Rimevegr, a
campaign does not fail only when men die. It fails when movement becomes
too expensive to trust.

---

## Legitimacy, Law, and Sacred Sanction

No ruler in the Rimevegr survives on force alone. Even the harshest leader
still needs his violence to look lawful to enough witnesses. That means
politics is always partly a struggle over names: justice, vengeance, duty,
oath, blood-price, ward-right, and the ancient fiction that the correct
ritual makes power cleaner than it is.

### Weregild and the Price of Order

Weregild does not prevent killing. It prevents every killing from becoming
endless war. A jarl who pays blood-price can present himself as a keeper of
order. A jarl who refuses it declares that law no longer restrains his
house. Once that happens, every grievance is reclassified as permission.

This is why the arithmetic matters so much. The dead are mourned, but the
silver is still counted. That counting is cold, unfair, and necessary.

### Oath-Stones and Public Memory

Oaths in the Rimevegr are not private promises. They are performed before
witnesses, sacred markers, and the kind of public memory that survives
longer than many households. To swear on an oath-stone and then break it is
to injure not only trust but a person's usable place in the legal world. A
jarl who becomes known for hollow oaths may still hold land, but he must
spend far more silver and fear to achieve what another man gains through
reputation alone.

### Sacred Ground and Ward-Rights

The Allthing's authority depends on more than custom. The assembly stones
are warded, watched, and symbolically maintained. Whoever supplies the
accepted galdr-worker for those protections acquires quiet prestige before
a single case is argued. That is one reason Deepholm and its allies hold
more influence than raw fighter count alone would suggest.

### Lawful Violence Versus Naked Violence

A raid called levy enforcement, a hostage called fosterage, a bribe called
dowry support, a feud called righteous blood-claim — politics in the
Rimevegr often consists of dressing force in the language of legitimacy.
Sometimes the language is sincere. Sometimes it is camouflage. The
distinction matters less than whether enough people accept it.

### Why This Matters in Practice

A ruler who can claim temple custom, proper weregild, oath-keeping,
ward-rights, and barrow stewardship seems ordained to rule even when his
position is fragile. A ruler who cannot do this may still frighten people,
but fear alone burns hot and short. Lasting power needs some sacred or
legal shape around it, even in a land this hard.

---

## Flashpoints and Likely Next Crises

The current balance is tense, not static. Several pressures are already in
motion, and any one of them could turn a season of hard bargaining into a
season of burning halls.

### The Deepholm Road Standoff

The Grimholt-Deepholm corridor is the single most likely place for a
political quarrel to become open mobilization. Ordovast wants pressure
rights, Sigrun needs traffic confidence, and both sides know the road
carries more than wagons. It carries the appearance of regional control.

### Thornwall's Pasture Test

Ordovast wants Thornwall's pasture and Helga's submission more than he
admits in formal speech. If sheep sickness, scouting violence, or levy
demands intensify, Thornwall may become the place where the wider struggle
stops pretending to be about negotiation.

### Feldwick's Breaking Point

A second occupation in one year rarely settles anything. It merely grinds
people down until revolt, flight, or retaliatory atrocity becomes more
likely than obedience. If Feldwick erupts, every nearby power will try to
frame the event as proof of its own necessity.

### The Bleakwater Bottleneck

A ferry crossing looks minor until the wrong convoy is delayed. Bleakwater
matters because timing matters. If messages, ore, levy bodies, or wounded
men begin arriving late, suspicion spreads faster than facts.

### Exposure of the Widow's Hand

The Whispering Circle survives on deniability. One proven case of
curse-work, dream-sending against a politically important household, or
visible Veil-thinning near a recognized settlement could unify people who
otherwise dislike each other. The Widow's greatest risk is not defeat in
battle. It is clarity.

### The Kolvik and Stonebay Coast Squeeze

If storms, raiders, or covert seizure pressure disrupt the coast, Deepholm
loses breathing room and Kolvik becomes more valuable and more vulnerable
at once. That would drag even nominally neutral coastal settlements into
harder alignments.

---

## Public Mood and Pressure from Below

Jarls imagine politics is made in halls. Much of it is actually decided in
kitchens, ferries, smithies, sheep pens, and mine mouths. When the lower
orders stop believing that sacrifice is being shared fairly, politics
changes whether the ruling houses approve or not.

### What Common People Actually Track

- whether grain stores are being stretched honestly or stolen upward
- whether levies return with pay, wounds, or neither
- whether healers think an illness is ordinary, poisoned, or cursed
- whether ferries and roads are safe enough to move family, wool, or fish
- whether a jarl's men pay for what they take

### Who Can Tilt the Political Weather

Miners in Deepholm and Grimholt, shepherd households in Thornwall and
Moor's End, ferrymen at river crossings, fisher families on the coast,
healers, and widows who control stores or kin ties all shape outcomes
without ever sitting in the high chair.

Thralls matter too, though rulers prefer not to say so aloud. Thralls hear
anger first, notice when stores are being hidden, and carry rumor across
households faster than heralds carry proclamations. A frightened thrall
population can destabilize a settlement long before open revolt becomes
thinkable.

### When Public Mood Turns

Common folk endure hardship better than insult. They will tolerate cold
rationing sooner than visible favoritism, and tribute sooner than
meaningless cruelty. But once people begin hiding grain, slowing carts,
misdirecting scouts, or quietly wishing for a different protector, a
political shift is already underway.

---

## Feuds and Rivalries

### How Feuds Start

In the Rimevegr, feuds are not personal grudges. They are economic disputes
formalized through violence.

**Common Causes:**

- **Livestock theft.** The single most common cause. A village raids
another's herds during the Long Dark when hunger presses. The victim
retaliates. The cycle begins.
- **Boundary dispute.** Two villages claim the same fishing ground,
hunting forest, or pastureland. Words fail. Axes do not.
- **Tribute refusal.** A stronger settlement demands payment from a
weaker one. The weaker refuses. The stronger burns something.
- **Blood debt.** A man from one village kills a man from another.
Weregild (blood-price) is demanded. If refused, the family of the dead man
has the right to take equivalent blood.
- **Raid escalation.** Svarthird bands hired by one village raid
another. The raided village blames the employer.

### Feud Escalation (0-4)

| Level | Name       | What It Means                                   |
| ----- | ---------- | ----------------------------------------------- |
| 0     | Cold       | No active hostility. Normal trade. Past is past |
| 1     | Tense      | Trade restricted. Insults traded at gatherings  |
| 2     | Hostile    | Trade cut off. Scouts watching borders. Raids   |
| 3     | Blood-feud | Active raiding. Weregild demanded. Bands hired  |
| 4     | Vengeance  | Total war. Settlement destruction as goal       |

Each level takes roughly one season to escalate unless accelerated by a
major event (murder of a leader, destruction of a crop store).
De-escalation requires active negotiation, weregild payment, or a shared
external threat that makes the feud too expensive to maintain.

### Gathering of Leaders (The Allthing)

Once per year, after harvest (around Day 90-100), leaders of nearby
settlements gather at a neutral site. The traditional sites are marked by
standing stones. The Allthing is sacred — violence is forbidden on Allthing
ground under penalty of outlawry from all participating settlements.

**What Happens in the open:**

- Disputes are heard and judged by the assembled leaders
- Alliances are renewed or dissolved
- Trade terms are negotiated for the coming year
- Feuds are formally declared or formally ended
- Marriages are arranged between families of different settlements
- Outlaws are declared or pardoned
- News is shared — who died, who was born, what bands are moving

**What Really Matters:**

- Who arrives with the largest visible escort without technically
violating sacred neutrality
- Who can feed guests, gift silver, or quietly forgive a debt on the
spot
- Which settlement looks underfed, over-armed, or short on pack animals
- Which jarl brings scribes, hostages, daughters, or mercenary witnesses
- Who sits beside whom when the public meal is served

The Allthing is the single most important political event of the year.
Missing it signals weakness. Dominating it signals power.

### Political Intrigue at the Allthing

The public speeches matter less than the arrangements made between them. A
leader with silver can appear patient. A leader with empty stores must push
too hard, reveal too much, or leave having promised more than can be kept.
That is why the Allthing is dangerous even when no sword is drawn.

**Ordovast's mode:** He comes with hard men, visible discipline, and the
implication that any agreement refused in council may be revisited later by
riders on the road. He wants tribute normalized, levies regularized, and
objections made to feel childish in the face of "security."

**Sigrun's mode:** She comes with ledgers, gifts, measured courtesy, and
terms that make cooperation sound like prudence rather than submission. She
wants roads open, tolls rationalized, harbor access protected, and
Deepholm's economic gravity accepted as regional common sense.

**The Pale Widow's mode:** She comes lighter, listens harder, and leaves
other people wondering why their private worries were mentioned so neatly
in public debate. She wants division without noise: enough mistrust that no
rival bloc can fully consolidate.

**Typical Allthing maneuvers:**

- a weregild case inflated or reduced to signal faction strength
- a marriage proposal that is really a corridor agreement
- a call for emergency levy funding that doubles as a loyalty test
- a debt quietly purchased from one hall in order to control another
- a neutral settlement forced to choose who may winter troops nearby
- an argument over barrow-clearing, ferries, or pass maintenance that is
actually an argument about who gets to define lawful force

**Dark reality:** The Allthing is sacred, but sacred does not mean clean. A
widow may be pressured to settle for less than a dead husband's worth. A
hungry village may vote for war because its jarl was promised grain. A
small hamlet may discover that neutrality is simply the state of being too
poor to bribe properly and too weak to refuse politely.

**Narrative use:** If the band attends the Allthing, they are not just
bodyguards. They are witnesses, leverage, intimidation, rumor-carriers, and
potential scapegoats. One wrong stare across the fire can become a winter
contract. One public insult can become a season of blood.

---

## Territory and Resources

### What Villages Fight Over

**Pastureland.** Sheep and goats need grazing. In the Rimevegr, good
pasture is limited by the short growing season. A village that loses its
grazing land loses its wool, its mutton, and its leather.

**Fishing Rights.** Fjord and coastal villages depend on fish for winter
protein. Fishing grounds are claimed by tradition. When a village's
population grows, it needs more fishing ground. The neighbor's ground looks
available.

**Timber.** The Black Pine provides building material, fuel, and charcoal
for smelting. Timber rights are hotly contested between forest-edge
settlements. A village without timber access cannot repair its walls, heat
its halls, or smelt iron.

**Iron and silver.** Only a few settlements have serious metal output. They
are wealthy and targeted. Control of iron is control of weapons, tools, and
trade goods. Control of Deepholm's silver and foundry craft is even more
strategic, because its smiths and galdr-workers draw the only dependable
silver wire used for higher warding and rune inlay. Grimholt and Deepholm
have the largest mining operations. Ashen Reach has a smaller smelter.

**Water.** River access for drinking, milling, and transport. Upstream
settlements can foul or divert water. This is a quiet weapon.

**Trade Routes.** Settlements on trade routes collect tolls and trade fees.
Control of a crossroads is control of regional commerce. Bleakwater Landing
exists entirely because of its ferry.

### Raiding vs. Conquest

Raiding and conquest are different strategies with different costs.

**Raiding:** Quick strike. Take livestock, grain, silver, thralls. Burn
what you cannot carry. Leave. Cost: low (a few fighters, a few days).
Reward: immediate loot. Consequence: the raided settlement hates you and
will retaliate.

**Conquest:** Occupy and hold. Install a loyal headman. Extract ongoing
tribute. Cost: high (fighters tied up in occupation, must feed them, must
defend against rescue attempts). Reward: long-term income. Consequence: the
occupied population resists, sabotages, and waits for you to weaken.

Most conflicts in the Rimevegr are raiding, not conquest. Conquest requires
manpower that most settlements and unions cannot spare. Ordovast is the
exception — he has the fighters to occupy and hold. This is what makes him
dangerous.

---

## Dark Magic as Political Weapon

### Why the Other Unions Fear It

Galdr (rune-craft) is accepted. A galdr-speaker who carves protection
runes, reads the wyrd, or wards a barrow is tolerated. Many settlements pay
for these services.

Seidr (spirit-craft) is feared but not forbidden. The old sagas say seidr
is women's work. A man who practices it is ergi — unmanly — and the shame
extends to those who associate with him. Women seidr-workers are tolerated,
feared, and consulted in private.

What the Pale Widow uses is worse. The curse-carver's art sits in the space
between galdr and something the old practitioners refused to name. The
nithing-pole is the visible sign. The invisible part is the invocation —
calling on forces from beyond the Veil to enforce the curse.

This is not superstition. In the Rimevegr, the Veil is real. Things move
behind it. The dead do not always stay dead. A curse-carver who knows what
he is doing can call attention from the other side. The attention is not
benevolent. It is not malevolent. It is interested. And interest from
beyond the Veil always costs something.

### What the Dark Arts Can Do (Narratively)

- **Nithing-pole:** Publicly declared curse against a person or
settlement. Causes bad luck that looks natural — livestock sickening, wells
going sour, nightmares among the population. Mechanically: settlement
morale drops, food spoilage increases, random bad events become more
frequent.

- **Veil-thinning:** The curse-carver can thin the Veil in a
specific location. This causes supernatural events — sounds, shadows, cold
spots, the occasional draugr stirring in nearby barrows. Mechanically:
settlement must resist supernatural fear, fighters refuse night watch, some
people flee.

- **Dream-sending:** The seidr-worker can send visions to sleeping
people within a few days' travel. Not control — just images, feelings,
dread. Useful for intimidation and psychological warfare.

- **Death-reading:** Reading the moment and manner of a specific
person's death. Not changing it — reading it. The information is valuable
for assassination planning.

### The Cost

Dark magic costs the practitioner. The curse-carver's hands shake. He
cannot sleep without herbs. His eyes have gone pale. He is aging faster
than his years. The seidr-worker has not eaten solid food in two months.
She speaks to things that are not there. Both of them are approaching a
threshold beyond which they will not return as themselves.

The Pale Widow knows this. She considers them expendable tools. She is
wrong — expendable tools with access to the Veil are the most dangerous
kind.

---

## How This Intersects With the Band

The band operates inside this political landscape as hired force, temporary
oath-keeper, road muscle, witness body, and sometimes disposable
intermediary. That gives it a peculiar kind of power. The band is rarely
large enough to rule anything for long, but it is often mobile enough to
decide who reaches the ferry, who arrives at the Allthing alive, whose
silver wagon makes it through the pass, and whose lie survives one more
week.

In practice, mercenaries become political because they move where household
men cannot. They go between unions. They hear private offers. They see
supply levels, morale cracks, and hidden fear before the great halls admit
any of it aloud. A jarl may call them tools, but tools that travel become
witnesses, and witnesses become leverage.

### Common Political Contract Tracks

- escort a jarl, heir, widow, foster-child, or law-speaker through
contested ground
- hold a road, ridge, quay, or ferry long enough for ore, wool, tribute,
or hostages to move
- collect weregild from a household that would rather gamble on feud than
payment
- investigate whether sickness, spoilage, livestock panic, or haunting is
natural or arranged
- defend a neutral settlement whose neutrality is beginning to crack
under outside pressure
- raid or counter-raid supply lines without forcing the employer to
declare open war
- recover a stolen ledger, relic, seal-ring, or hostage before the
Allthing hears of it
- stand as visible third-party witnesses while a bargain, marriage
compact, or hostage exchange is made
- quietly remove a witness, courier, or informer before testimony becomes
public law

### What Each Power Really Wants From the Band

#### Iron Grip Hires the Band to Make Fear Arrive on Time

Ordovast does not primarily hire mercenaries because he lacks men. He hires
them when he needs speed, deniability, or cruelty at arm's length. His
ideal use of the band is to do something his own sworn men would remember
too clearly: collect tribute from a wavering hall, escort hostages, punish
a road-reeve, or stand just outside a village long enough for rumor to do
the real work.

Payment from Iron Grip often looks straightforward, but the hidden price is
association. A band that does too much work for Ordovast becomes known as
part of the pressure system. That may bring short-term coin and easier
intimidation, but it also makes neutral villages slower to trust and more
likely to hide information.

#### Fjord Compact Hires the Band to Keep Systems Working

Sigrun and her allies want continuity more than terror. When they hire
outside fighters, it is usually to preserve movement: protect a convoy,
keep Kolvik's harbor calm, ensure Ashmark's neutral ground stays neutral
for one more assembly, or move refined silver and galdr materials without
openly militarizing the road.

Compact work often pays best and pays cleanest. It also entangles the band
in contract law, merchant expectation, and public reputation. If the band
fails a Compact employer, the damage spreads through ledgers, caravan
gossip, and workshop trust. A missed escort becomes an economic fact, not
just a private disappointment.

#### Whispering Circle Hires the Band to Carry Risk It Does Not Want Named

The Pale Widow's bloc prefers work that can be described three different
ways depending on who survives to tell it. A job may be sold as escort
duty, rescue, investigation, or recovery while actually being blackmail
retrieval, silence purchase, or curse-cleanup. The Circle values the band
not only as fighters but as outsiders who can be left holding blame.

This makes Widow contracts lucrative and poisonous. They often offer the
best immediate coin, the most useful secrets, and the worst long-term
stain. A band that takes too many of them may find itself feared in the
wrong way: not as hard men, but as people around whom infants sicken,
witnesses disappear, and doors are barred after dark.

### Why the Band Gets Pulled Deeper Than Intended

Most political work begins narrow: one escort, one collection, one night
watch, one meeting kept from turning into a knife fight. Then the band
discovers who is lying, who is desperate, who cannot actually pay, and
which insult is bigger than the contract described. In the Rimevegr,
mercenaries are often the first people to see the gap between the public
reason for a conflict and the real one.

A widow claims she fears raiders, but what she truly fears is a marriage
arrangement. A jarl says he needs convoy guards, but what he really needs
is witnesses who will later say his goods were lawfully his. A healer asks
for escort because of wolves, but the real threat is that she knows which
child was poisoned and by whom. The band keeps stepping into the second
truth behind the first one.

### How the Band Accidentally Becomes a Kingmaker

The band does not need a hall of its own to alter the balance of the
region. It only needs to be in the right place on the wrong day.

A single intervention can change more than a skirmish:

- getting a foster-son safely to the right household may hold an alliance
together for years
- keeping a ferry open for two extra days may let tribute arrive before a
feud becomes lawful war
- recovering a debt ledger may prove who truly owes whom before the
Allthing votes
- exposing one false curse or one real poisoning may destroy the
legitimacy of an entire faction move
- refusing to sell to one jarl in public can signal that his silver or
oath is no longer trusted

This is why the band is politically valuable even when it is not large. It
can alter timing, proof, and survival. In a fragile system, those things
matter as much as raw force.

### Political Escalation Ladder for Band Play

A good campaign should let political entanglement climb in clear steps
rather than arriving all at once.

1. **Local muscle work:** guard duty, escort, levy collection, road
watch.
2. **Witness work:** present at settlements where the band sees too much.
3. **Choice pressure:** two employers want the same road, prisoner, or
ferryman.
4. **Named enemies:** the band is recognized and remembered by households
that matter.
5. **Faction weight:** accepting or refusing a contract begins affecting
union-level trust.
6. **Allthing relevance:** the band arrives not just as labor but as
evidence, leverage, or a feared variable.

At the early stages, politics feels like background weather. By the later
stages, every contract is also a vote, even if nobody uses the word.

### Signs a Contract Is Politically Poisoned

The band should learn to fear certain patterns more than a low pay offer.

- the employer wants speed but not witnesses
- the silver is good but the terms are vague
- the target is said to be a thief, yet no one will say what was stolen
- a supposedly private task must be finished before the next Allthing
- the job involves moving a child, widow, or lore-keeper in secrecy
- the employer insists the band must not speak to ferrymen, healers, or
local old women
- everyone involved keeps saying the matter is not political

In the Rimevegr, that last sign is often the surest proof that it is.

### Long-Term Consequences for the Band

A band that works long enough in one region stops being anonymous. Jarls
begin measuring its reliability. Healers and ferrymen begin talking to it.
Lore-keepers remember its names. Villages begin deciding whether its
arrival means safety, extortion, or bad luck.

That creates lasting consequences:

- repeated Iron Grip work raises fear and feud faster than trust
- repeated Compact work raises credibility and contract value, but also
draws the band into trade wars
- repeated Whispering Circle work improves access to secrets while
steadily poisoning public legitimacy
- protecting neutrals like Ashmark can make the band respected, but also
turns it into an obstacle both sides may wish removed
- once the band is known to carry political truth, employers stop buying
only swords and start buying silence

### The Real Risk

The band does not drive the politics. The politics drive the band. The
world moves whether Voss acts or not. But once the band has taken enough
contracts, even refusing a job becomes a statement, and even neutrality
starts to look like a side.

That is the real danger of success in the Rimevegr. The band may begin as
hired axes. If it survives long enough, it becomes something much harder to
remain: a mobile political fact everyone must account for.
