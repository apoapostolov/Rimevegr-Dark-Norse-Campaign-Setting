# Villages and Settlements

<!-- notion-export:toc -->


**Project:** Iron Ledger -- Mercenaries of the Rimevegr
**Purpose:** Settlement simulation framework. YAML-structured for persistent AI tracking.

---

## 1. Settlement Template

```yaml
settlement_name: "Frostfjord Hollow"
size: "Village" # Hamlet / Village / Large Village / Town
population: 87
fighters_available: 11
standing_with_band: -1 # -5 to +5
feud_track: 2 # 0 Cold -> 4 Vengeance
settlement_morale: 3 # 1-5

economy:
  treasury_silver: 45
  food_stores_days: 120
  main_trade: "Dried cod, fish oil, and basic goods"
  weekly_income: "8-15 silver"

capability:
  defensibility: 2 # 1 Weak palisade -> 5 Fortified
  forage_quality: "Good"
  blacksmith_level: "Basic"
  healer: "Herbalist (midwife)"

defenses:
  perimeter: "Split-log palisade"
  ditch: "Shallow landward ditch"
  gatehouses: 1
  towers: 0
  natural_barriers:
    - "Fjord frontage"
  special_defenses:
    - "Jetty watch post"
    - "Rune-marked threshold stones on key storehouses"

structures:
  domestic:
    longhouses: 11
    cottar_huts: 4
    byres: 5
  storage:
    granaries: 1
    root_cellars: 7
    smokehouses: 2
  productive:
    smithies: 1
    boathouses: 2
    fish_sheds: 3
    net_drying_racks: 8
  civic_religious:
    hall: "Hrothgar's hall"
    thing_site: "Shore law-stone"
    temple: null
    shrine_sites:
      - "Southern barrow rune-stone"

construction_capacity:
  laborers: 18
  carpenters: 2
  masons: 0
  smiths: 1
  build_points_per_season: 20

maintenance_burden:
  upkeep_points_per_year: 11
  vulnerable_elements:
    - "Sea-facing jetties"
    - "Salt-rotted palisade posts"

damage_state:
  overall: "Worn but functional"
  damaged_elements:
    - "South palisade warped by spray and freeze-thaw"
    - "One boathouse roof patched with scavenged sailcloth"

relationships:
  - jarl: "Hrothgar of Frostfjord"
    allegiance: 3
    notes: "Pays protection silver twice per year"
  - rival: "Ashen Reach"
    relation: "Hostile"
  - mercenary_bands:
      - band: "Voss's Black Axes"
        standing: -1
        last_interaction: "Demanded tribute 12 days ago"

extortion_history:
  - date: "Day 75, Long Dark"
    band: "Voss's Black Axes"
    amount: "15 silver + 3 thralls"
    grievance: "Medium"

internal_issues:
  - type: "Theft of winter stores"
    severity: "Low"
  - type: "Whispering rune-stone near southern barrow"
    severity: "Medium"

# Hidden events stored in Chinese via hidden_info.py
hidden_events_ref: "data/hidden/frostfjord_secrets.txt"
```

---

## 2. Canonical Village Fabric

The Rimevegr should not use generic fantasy "building slots" as its baseline. Its settlements are built from the same recurring Norse and early medieval forms, adjusted by terrain, wealth, labor, and fear.

Archaeological and historical anchors for this section:

- Norse farms and villages were built around a larger dwelling-house with a few smaller outbuildings rather than around dense masonry urban blocks.
- Longhouses could include people and stock under one roof, especially in harsher climates or poorer communities.
- Smaller outbuildings handled storage, livestock separation, and specialist work such as smithing and textile craft.
- Pit-houses or sunken-floor huts were often used for craft work; some served as smithies.
- Larger Norse settlements added halls, assembly spaces, defended gates, workshops, jetties, and harbor control rather than becoming fully urban.

### Structure Categories

| Category | Typical structures | What they do in play |
| -------- | ------------------ | -------------------- |
| Domestic | longhouse, farmhouse, cottar hut, byre, stable, thrall hut | house population, shelter labor, absorb winter pressure |
| Storage | granary, raised storehouse, root cellar, smokehouse, fish shed | preserve food, tools, seed, and trade goods |
| Productive | smithy, pit-house workshop, loom shed, kiln, tar pit, charcoal clamp, boathouse, jetty | convert labor and raw materials into usable output |
| Civic | chief's hall, guest hall, tavern, market yard, weighing shed, thing-field, law-stone | organize authority, hospitality, dispute settlement, and exchange |
| Religious/Funerary | temple, shrine, altar-stone, barrow-keeper hut, seiðr hut, grave field | maintain ritual order and social legitimacy |
| Defensive | ditch, hedge, palisade, wall, gatehouse, tower, beacon, harbor chain, watch post | slow raiders, multiply defenders, and protect stores |

### What a Typical Settlement Actually Contains

| Size | Minimum expected fabric | Usually absent | Common upgrade path |
| ---- | ----------------------- | -------------- | ------------------- |
| Hamlet | 3-8 dwellings, shared byre space, root pits, sheds, one communal meeting room or elder's house | formal smithy, temple, full perimeter wall | fence, hedge, ferry landing, boathouse, shrine |
| Village | 8-20 dwellings, dedicated byres, one granary, one smithy or specialist workshop, hall or inn, partial defense line | true stone wall, multiple towers | gatehouse, market yard, smokehouses, jetties, thing-site |
| Large Village | clustered longhouses and outbuildings, several storage buildings, multiple workshops, hall, temple or major shrine, proper gate control | full urban density | ditch plus wall, tower, harbor chain, craft quarter |
| Small Town | specialized workshops, market square, temple, fortified seat, storage surplus, permanent gate regime | none of the essentials; absence becomes a political weakness | stone enceinte, foundry quarter, archive, formal garrison works |

### Terrain and Anthropology Constraints

- Fjord and coast settlements invest early in jetties, fish sheds, boathouses, drying racks, smokehouses, and beach or harbor watch.
- Forest settlements skew toward charcoal clamps, tar pits, timber sheds, bark stores, kennels, and wider clearings rather than heavy stonework.
- Moor settlements depend on fold walls, thorn hedges, peat stacks, sheep pens, root cellars, and wind-resistant halls with fewer high roofs.
- Mountain settlements concentrate labor into retaining walls, terraces, watchtowers, defended gate approaches, mines, ore sheds, and pack-animal shelters because hauling is the real bottleneck.
- Religious structures in the Rimevegr are shaped by local canon: stone temples where institutional worship exists, altar-stones and grove or barrow-edge structures where it does not, and seiðr practitioners kept at the edge of the settlement rather than in its social center.
- The thing is not necessarily a building. Many settlements use a law-stone, cleared ring, dockside yard, or hall forecourt as their assembly space.

### Canonical Structure Tags for Rimevegr Data

- `longhouse`, `cottar_hut`, `byre`, `stable`, `barn`
- `granary`, `storehouse`, `root_cellar`, `smokehouse`, `fish_shed`
- `smithy`, `pit_workshop`, `loom_shed`, `kiln`, `tar_pit`, `charcoal_clamp`
- `boathouse`, `jetty`, `dry_dock`, `harbor_chain`, `ferry`
- `hall`, `guesthall`, `inn`, `market_yard`, `thing_site`, `law_stone`
- `temple`, `shrine`, `altar_stone`, `barrow_keeper_hut`, `seidr_hut`
- `hedge`, `ditch`, `palisade`, `wall`, `gatehouse`, `watchtower`, `beacon`

### How Settlements Usually Quote Value

- Hamlet and poor village custom is food, favors, labor, and copper first. A stranger is more likely to hear "supper and 4 copper" than a clean silver price unless the matter is legal or martial.
- Villages and large villages quote mixed dues when the work is risky or specialized: healer care, guides, room space in a guesthouse, or skilled repairs often come as food plus copper, or copper with a little silver if the buyer is an outsider.
- Market-facing settlements such as Deepholm, Thornwall, Kolvik, Ashen Reach, and Skaldhaven reduce more things to silver because they see enough strangers to price time, risk, and stock cleanly.
- Tribute is rarely "pure rent in coin." Stronger powers usually demand a mix: silver when campaigning, livestock when provisioning, transport rights at chokepoints, and labor or carts when roads, walls, or siege works matter more than loose money.

---

## 3. Starting Settlements

### Frostfjord Hollow (Village)

Population 87. Jarl Hrothgar's seat. Dried cod economy. Basic smithy. Standing with band: -1 after recent tribute pressure.

Frostfjord smells of fish oil, wet rope, and old smoke. Nets hang beside children's laundry, and every family can tell from the color of the fjord whether the catch will hold or fail. It is a hard, practical place where custom survives because custom costs less than chaos: boats are blessed, knives are counted, and every winter death is folded into the work of the next day.

Economically, Frostfjord lives on short-haul exchange. It pushes dried cod, fish oil, and pilotage down-fjord toward Kolvik and Skaldhaven, and it takes in iron fittings, tar, salt, lamp oil, and whatever Deepholm's traders have not priced beyond reason. Its rivalry with Ashen Reach is not abstract politics but daily arithmetic: whichever side controls the safer movement corridor controls winter margins.

**Existing structures and defenses:**

- Hrothgar's hall overlooking the jetty
- 11 turf-roofed longhouses and 4 poorer cottar huts
- 5 byres and animal sheds
- 1 granary, 7 root cellars, 2 smokehouses, 3 fish sheds, and 8 drying racks
- 1 basic smithy, 1 healer's hut, 2 boathouses, and a working jetty
- 1 waterfront alehouse-inn and 1 law-stone by the shore path
- Split-log palisade and shallow landward ditch, with the sea serving as the other wall

**Pressure and event hooks:**

- A run of poor catches forces Hrothgar to squeeze ferries, traders, or tenants harder than usual.
- A boat returns light, with nets cut and one rower refusing to say what he saw beyond the fog.
- The whispering rune-stone near the southern barrow is becoming part of local speech; children repeat words they should not know.

### Ashen Reach (Large Village)

Population 142. The Pale Widow rules. Pine tar and iron define the local trade. Skilled blacksmith. Quietly hostile to Frostfjord.

Ashen Reach looks productive from a distance: tar smoke, orderly yards, iron ringing on anvils, widow-black banners hanging still in the cold. Up close, everything feels slightly too controlled. People lower their voices when discussing contracts. Doors close softly. No one says the Pale Widow rules by fear, because fear in Ashen Reach wears the face of competence.

The settlement sits on a hinge between coast and interior. Charcoal and wood come from Vargheim and Ashmark. Iron and finished goods move through its works toward Kolvik, Frostfjord, and any buyer with silver in hand. Ashen Reach wants to be indispensable: the place that coats your hull, repairs your tools, buys your ore, and learns your weaknesses while the metal heats.

**Existing structures and defenses:**

- Widow's Hall, a proper gate yard, and a counting shed
- Roughly 16 longhouses with attached byres and 6 smaller huts for workers and dependents
- 2 granaries, 1 raised storehouse, 9 root cellars, and 2 smokehouses
- 1 skilled smithy, 1 smelter, 1 tar-works complex, and 2 pit-workshops
- 1 gate-inn, 1 healer's house, 1 stone temple, and a cleared thing-yard under the hall
- 1 weighing shed and trader's yard inside the gate
- Wooden wall with gatehouse, inner fighting platform, and a watch post over the road

**Pressure and event hooks:**

- Tar pits begin slumping toward older ground that should not be moving.
- A smith refuses a profitable commission after finding the buyer's name already scratched into his bench.
- A messenger carrying terms for Frostfjord is found alive, frightened, and missing only the parts of the letter that mattered.

### Feldwick (Village)

Population 61. Currently occupied by the Three Wolves. Desperate. Main trade: sheep wool and root vegetables, though little stays local now.

Feldwick is what occupation looks like after the shouting is done. Pens stand half-empty. Root cellars are re-counted at night. Women still bake, patch, spin, and send children for water because the work must continue, but the work now happens around armed men who treat every shelf as a tax source. The place has not died. It has become careful.

Before the occupation, Feldwick sat in a useful position between the moor routes and forest tracks, feeding Thornwall markets and taking tools from Ashmark and Deepholm. That exchange has been warped rather than stopped. Now goods move out at swordpoint: wool, breeding stock, dried turnips, watch-duty, sons. The village's real economy is concealment.

**Existing structures and defenses:**

- 9 longhouses and 3 cottar huts
- 6 byres and sheep sheds
- 1 communal bakehouse, 1 damaged granary, 5 root cellars, and simple sheep pens
- No real smithy, only a scavenged repair shed
- Elder's house requisitioned as an occupation hall
- Damaged wooden palisade with one warped gate, gaps patched with carts and thorn bundles

**Pressure and event hooks:**

- Hidden food caches are disappearing, which means there is either a spy inside the palisade or something else has learned the pattern.
- A village elder wants outside help to stage a quiet revolt without getting the children killed first.
- Three Wolves officers begin arguing over how much more the place can be stripped before it ceases to be worth occupying.

### Stonebay Hamlet (Hamlet)

Population 23. Remote fishing hamlet. No blacksmith. Poor defenses. Neutral mostly because it is too small to matter until it suddenly does.

Stonebay is a place of bent backs, tide tables, and weather-sense worn into the face. Its people know which gulls mean fish, which waves mean a hidden current, and which silence means everyone should come inside. They repair more than they replace because replacement requires silver and a larger world than Stonebay usually sees.

Its survival depends on nearby stronger settlements. Kolvik provides nails, rope, and hull help; Frostfjord absorbs surplus catch when the boats are lucky; Skaldhaven occasionally sends coin for whale bone, sealskin, or old things pulled from the surf. In return Stonebay offers fish, oil, storm warning, and salvage rights that become valuable only after wrecks.

**Existing structures and defenses:**

- 4 fishing longhouses and 2 lean-to huts
- 1 shared byre, 3 root pits, 1 smoke shed, and 1 crude fish rack cluster
- 1 small wharf and 2 hauled-up boat sheds made from drift timber
- No formal hall, only the elder's room used for meetings
- No perimeter wall, just beach watch and storm cairns

**Pressure and event hooks:**

- Something has begun washing ashore in pieces too regular to be driftwood.
- One family's boat does not return, but its net-floats drift in on a tide that should have carried them the other way.
- A larger power suddenly remembers Stonebay exists because its beach is the only viable landing site during a bad-weather week.

### Grimholt (Large Village)

Population 118. Warchief Ordovast's stronghold on the High Rime-Moors. Strong defenses, heavy patrol presence, iron extraction.

Grimholt is a village built like a warning. Fires burn hot, gates open on command, and the garrison's discipline is visible even from the road. Ordovast's rule has produced what harsh men call order: fewer raids, faster punishments, steady iron output, and a settlement where nobody can pretend not to know who is in charge. The price of this order is paid in levies, requisitions, and the slow normalization of fear.

The economy is war-shaped. Ore, ingots, nails, fittings, and spearheads go out; food, wool, peat, leather, and unwilling labor come in. Grimholt can extract iron, but it cannot eat iron, so it leans hard on Thornwall, Moor's End, and whatever traffic it can force through its orbit toward Deepholm. Proximity gives it leverage. Distance gives its enemies time.

**Existing structures and defenses:**

- Ordovast's war-hall, barracks hall, and levy yard
- 13 longhouses, 5 dependent huts, and 7 byres and pack-animal sheds
- 2 granaries, 10 root cellars, 1 smokehouse, 1 ore store, and 1 armory
- 1 hard-used garrison inn, 1 market yard for levy and ore traffic
- 1 skilled smithy, 1 healer's lodge, 1 bloomery, 1 repair forge, mine-head sheds, and timbered ore ramps
- 1 stone temple, 1 beacon tower, and a thing-stone under guard
- Stone-faced earthwork with timber fighting walk, ditch, strong gate, and high watchtower

**Pressure and event hooks:**

- A mining tunnel produces less ore than expected and more bodies than can be explained by ordinary collapse.
- Ordovast's quartermasters are taking seed grain, not just tax grain, which means next season is already being stolen.
- A patrol disappears on a familiar moor route, leaving only dropped iron tags and one dead raven nailed to a marker stone.

---

## 4. Expansion Settlements

### Raven's Perch (Village)

Population 74. Thane Egil Raven-Eye rules from a mountain lookout with a narrow approach and stone walls. Mountain goat hides and ore keep it fed. No healer. Iron Tide Remnant winters here.

Raven's Perch survives because it sees trouble before trouble arrives. It is all sharp wind, steep steps, and people who speak as though breath were scarce and words should be saved. The place is proud in the way exposed settlements often are: not because life is good there, but because nobody can survive the climb without becoming stubborn.

Its economic role is part toll-house, part warning bell. Ore and hides move down toward Deepholm and Grimholt; grain, salt, lamp oil, and cloth must come back up. Whoever holds Raven's Perch does not become rich, but they do become difficult to surprise. That has a market value of its own.

**Existing structures and defenses:**

- Egil's hall
- 8 longhouses and 3 cottar huts
- 4 goat byres and 1 pack stable
- 1 granary, 6 root cellars, 1 smoke shed, and 1 ore shed
- 1 basic smithy, 2 store terraces, 1 beacon platform, and 1 raven rookery
- 1 steep-roofed guesthouse for caravans and messengers
- 1 law-stone shelf beside the inner gate
- Stone walls on the exposed side, timber breastworks on the less steep approach, narrow gate turn, and rolling-stone positions above the path

**Pressure and event hooks:**

- The ravens are gathering in numbers large enough to interrupt watch rotations and unnerve even seasoned guards.
- A caravan reaches the lower approach with all its mules and only half its handlers.
- Egil wants the path fortified further, but every extra stone hauled uphill means one less sack of grain hauled in.

### Vargheim (Large Village)

Population 165. Jarl Ulf Vargson's deep-forest hold. Wolf-warden kennels, charcoal kilns, and a skilled smithy give it real leverage.

Vargheim is a village of smoke, bark, and teeth. Children learn to read tracks before letters. Charcoal burners come home looking half-buried in soot. Wolf-wardens walk with the calm of people who know their animals are better listeners than most men. Tradition here feels older than the halls: grove offerings, hunting taboos, and a deep dislike of outsiders who treat the forest like empty timber.

Economically, Vargheim is essential to everyone who uses fire seriously. Its charcoal feeds smithies in Ashen Reach and Deepholm; its hides and pelts move toward Skaldhaven and Kolvik; its timber and pitch help keep wagons, halls, and kiln frames standing. In return it needs salt, metal fittings, milling, and those irritating luxuries the forest does not make.

**Existing structures and defenses:**

- Ulf's long-hall and kennel yard
- 18 longhouses, 5 bark-roof huts, and 8 byres
- 2 granaries, 8 root cellars, and 2 smokehouses
- 1 skilled smithy, 4 charcoal clamp sites, 2 tar pits, hide sheds, timber stacks, and wolf-pen kennels
- 1 guesthall-inn for charcoal crews and traders
- 1 healer's lodge
- 1 timber temple by the grove and a law-stone clearing
- Stake ditch, timber wall, wolf runs outside the gate, and tree-platform watches

**Pressure and event hooks:**

- A trusted wolf-warden claims one of the packs is avoiding a grove it has crossed for years.
- Charcoal output drops after a kiln crew vanishes between dusk and dawn.
- Ulf's men suspect someone is marking trees to guide raiders through the outer belts without detection.

### Kolvik (Village)

Population 95. Harbour-Master Inga's coastal logistics node. The only shipwright between Frostfjord and the mountain interior.

Kolvik is less romantic than the songs claim and more valuable than most jarls admit. It stinks of salt, pitch, bilge-water, and hot iron. The shipyard is noisy even in bad weather, because hulls do not wait for a kind season to split. Harbor law is practical and rude: pay your berth, mend what is broken, and do not start a feud on a wharf where everyone carries a hook-knife.

Its trade web is dense because it sits between sea need and inland need. Ashen Reach supplies tar and iron fittings. Frostfjord and Stonebay land fish, oil, and coastal news. Deepholm's merchants want repaired hulls, moving cargo, and secure passage for silver, bronze, and high-value forge work coming down from the mountain. Skaldhaven wants people and manuscripts carried safely. Kolvik turns all of that movement into fees, repair bills, and access control.

**Existing structures and defenses:**

- Harbour-master's hall, berth hut, and repair yard
- 12 longhouses, 4 dockside huts, and 4 byres
- 1 granary, 7 root cellars, 2 smokehouses, and 3 fish sheds
- 1 shipwright's shed, 1 ropewalk, 1 pitch store, 1 dry-dock, 2 boathouses, and 2 jetties
- 1 harbor inn-alehouse, 1 weighing shed, and dockside thing-yard used for contracts
- Low stone wall inland, harbor chain, gate on the warehouse lane, and night watch on the piers

**Pressure and event hooks:**

- The harbor chain is found nicked through in three places, too cleanly to be accident.
- A repaired boat returns with the same hull damage it left with, as if the sea were repeating itself.
- Inga is asked to choose between profit and neutrality when two hostile employers demand the same berth space on the same tide.

### Moor's End (Hamlet)

Population 31. Elder Brosa's isolated moor hamlet. Sheep and peat keep it barely standing. The standing stones hum at night.

Moor's End is not poor in the abstract. It is poor in the counted, intimate way: one broken ankle means a field goes uncut; one dead ewe means a family changes what it eats for a month; one storm can tear the roof from the same house twice in a year. The people still keep the old courtesies, still pass hot broth to strangers, still count births and funerals against the same wooden post, because when a place gets this small custom becomes structure.

It survives by leaning on Thornwall and, when roads hold, on Bleakwater and Deepholm's outer markets. Peat bricks, rough wool, lambs, and whatever can be carried in a cart go outward. Grain, iron tools, lamp grease, and seed come back in. The trade is humiliatingly local because distance kills profit before profit arrives.

**Existing structures and defenses:**

- 5 longhouses and 2 peat huts
- 3 sheep byres and folds
- 1 raised storehouse, 4 root cellars, and peat stacks ringed with stone
- 1 elder's hall-room
- 1 standing-stone ring used as assembly and rite site
- Thorn hedge and ditch fragments, with most defense supplied by distance and watch fires

**Pressure and event hooks:**

- The standing stones are humming often enough that the sheep avoid the pasture nearest them even in hunger.
- Brosa wants help escorting a winter peat train that would not matter to a large settlement but means survival here.
- A young woman has started sleepwalking toward the stones and waking with peat under her nails and no memory of leaving bed.

### Ashmark (Village)

Population 82. Reeve Torsten's buffer settlement between forest power, coastal money, and moor coercion. Pine tar, herbs, and healing keep it open.

Ashmark feels busy in a thin, anxious way. Tar pits bubble. Herbal bundles dry from rafters. Teamsters stop for broth, gossip, and poultices before moving on. The place survives by being useful to stronger neighbors without looking rich enough to invite immediate confiscation. Its neutrality is not idealism. It is camouflage.

Because it sits near Vargheim, Feldwick, Ashen Reach, and Deepholm, Ashmark functions as a small exchange basin. Tar, herbs, wagon grease, charcoal, messages, and rumor all move through it. Sick animals are brought here. Wounded men are patched here. Quiet deals get made here because everyone can claim they were only stopping for medicine.

**Existing structures and defenses:**

- Reeve's house used as meeting hall
- 10 longhouses, 4 cottar huts, and 4 byres
- 1 granary, 6 root cellars, and herb drying racks under the eaves
- 1 roadside inn, 1 healer's lodge, 1 brew shed, 1 wagon shed, 1 tar pit, and 1 small market yard
- 1 shrine post cluster near the healer's store
- Modest wooden palisade with one gate, roadside watch stage, and threshold wards on the healer's store

**Pressure and event hooks:**

- The healer's lodge is overfull and people are beginning to ask whether a sickness is traveling the road faster than rumor.
- The Bone Pack wants winter shelter, which means someone else will soon object.
- Torsten's neutrality becomes expensive the moment two rival employers ask him to close the same gate to different people.

### Deepholm (Small Town)

Population 520. Jarl Sigrun's industrial and political gravity well. Stone fortress, iron gate, market square, barrow archive, galdr workshop. Best contracts in the region and standards to match.

Deepholm is what happens when hardship becomes organized. It is louder, richer, dirtier, and more disciplined than the villages around it. The market square runs on weighing, tallying, shouting, and suspicion. Beneath that bustle lies the truth that keeps the town alive: everybody needs what Deepholm can make, and Deepholm needs nearly everything everybody else can grow, cut, burn, or haul.

Its near-neighbor network is unusually dense. Within a day or two it can reach Grimholt for ore pressure, Vargheim for charcoal, Thornwall for wool and meat, Skaldhaven for archival and rune expertise, Kolvik for coastal shipping, and Bleakwater for marginal river access. Deepholm exports metal, weapons, tools, coin flow, and contracts. It imports the calories and raw materials without which the furnaces go cold and the soldiers start asking questions.

The town's silver matters almost as much as its iron. Deepholm's mining halls yield silver alongside deeper metal work, and Sigrun's foundry also re-smelts trade silver and old hack-silver into stock fit for fine drawing. What makes Deepholm strategically unique is not raw silver alone but process: the galdr workshop and foundry collaborate to produce the only dependable galdr-grade silver wire in the Rimevegr. Higher ward repairs, rune inlay, and certain protective bindings all bottleneck there, which is one reason every serious power watches Deepholm so closely.

**Existing structures and defenses:**

- Sigrun's keep, market square, counting hall, and archive quarter
- 38 longhouses and townhouses
- 16 workshops, 6 granaries or storehouses, 20 root cellars, 3 smokehouses, and a proper inner warehouse lane
- Master smithy, foundry, minting room, galdr workshop, ship-repair basin, mine-head halls, and multiple cart sheds
- 2 inns and guesthouses, 1 leech-house, 1 stone temple, 1 formal thing-yard, and 1 guarded barrow archive
- 1 weighing house and toll office opening onto the market square
- Stone enceinte, iron gate, ditch on the vulnerable side, two towers, and a permanent gate watch

**Pressure and event hooks:**

- A tunnel collapse is publicly blamed on bad timber, but everyone in the lower halls is suddenly wearing amulets.
- A shipment of iron arrives underweight and nobody can prove where the loss occurred between mine mouth and market scale.
- Sigrun offers a lucrative contract that sounds clean until one notices how many factions benefit if it fails quietly.

### Bleakwater Landing (Hamlet)

Population 18. Ferryman Olaf's river bottleneck. Ferry tolls and fish are all that keep the mud from swallowing the place entirely.

Bleakwater is a settlement built around the fact that some crossings are too important to abandon, even when the ground itself seems to object. The ferry is patched more often than painted. The huts lean. Reed smoke hangs low over black water. People here are polite in the tired way of those who know every stranger might be coin, danger, or both.

Its economy is tiny but strategic. Moor traffic, message-runners, stray drovers, and Deepholm-bound carriers all sometimes need Olaf's crossing. Bleakwater sells fish, passage, and local knowledge. In return it receives salt, grain, nails, lamp grease, and the illusion that staying matters. Without nearby stronger settlements it would go empty inside a season.

**Existing structures and defenses:**

- Ferryman's house, 3 family huts, and 1 byre
- 3 root pits, 1 smoke shed, 1 ferry landing, and 1 reed-roof gear hut
- No hall except Olaf's room used for deals
- No fixed wall, only a watch post by the rope and mud banks that hinder a direct rush

**Pressure and event hooks:**

- More bodies than usual are coming downriver, and Olaf is beginning to charge differently depending on who asks about them.
- The ferry rope frays twice in one week, which should be impossible.
- Something in the bog is spoiling stored food faster than mildew should.

### Skaldhaven (Village)

Population 110. Lore-Keeper Audun's cliffside centre of learning. Hall of Sagas, rune archive, relic traffic, and paid memory.

Skaldhaven is one of the few places in the Rimevegr where people make a living from words without apologizing for it. Scribes, singers, copyists, and relic-appraisers move around the same hall as fishmongers and laborers, and the tension between prestige and hunger is visible in every conversation. The place is cultured by local standards, which mostly means it can name its fears more precisely.

Its economy rests on knowledge being worth transport. Barrow relics come in from mercenaries. Coin comes in from jarls who want lineages remembered, runes copied, disputes framed, or reputations polished. Food, wool, lamp oil, and ordinary necessities still have to arrive from Frostfjord, Kolvik, Ashen Reach, and Deepholm. Memory may be noble, but it still eats bread.

**Existing structures and defenses:**

- Hall of Sagas, rune archive, and guest hall
- 13 longhouses, 4 small scholars' huts, and 5 byres
- 1 granary, 8 root cellars, and 1 relic store
- 1 basic smithy, 2 scriptoria rooms, 1 copy shed, and cliffside drying racks for vellum and fish
- 1 inn for patrons and pilgrims, 1 healer-scribe's chamber
- 1 stone temple, 1 law-stone court, and shrine posts near the archive
- Wooden palisade inland, sea-cliff edge on the other faces, and alarm horns on two watch platforms

**Pressure and event hooks:**

- The sealed archive is drawing the wrong sort of interest from buyers who claim to be mere collectors.
- Audun wants escorts for a relic transfer that is officially modest and unofficially anything but.
- A new saga circulating in the hall includes details from a private death no outsider should know.

### Thornwall (Large Village)

Population 180. Jarl Helga Thornwall's moor bulwark. Thorn-hedge walls, stone gatehouse, sheep market, wool and mutton trade.

Thornwall feels less like a village than a working defensive argument. Every hedge is maintained, every gate checked, every flock counted against both weather and thieves. Helga's people are not soft, but they are stretched: repairing walls, watching routes, lambing in bad weather, and pretending they have enough hands for all of it. They keep festivals anyway, though the music usually stops earlier than it used to.

Economically, Thornwall anchors the southern moor circuit. It takes peat and smaller flocks from Moor's End, sells wool, mutton, and hedge craft toward Deepholm and the coast, and buys iron, salt, leather fittings, and whatever luxury a good year briefly permits. Its closeness to Deepholm makes trade possible; its closeness to danger makes that trade expensive.

**Existing structures and defenses:**

- Helga's hall, wool market lane, and lamb yard
- 17 longhouses and 6 shepherd huts
- 10 byres and sheep folds
- 2 granaries, 9 root cellars, 1 smokehouse, and extensive thorn nurseries
- 1 skilled smithy, 1 felting shed, 1 tannery yard, and 1 healer's house
- 1 gate-inn for drovers, 1 stone temple, and 1 thing-field beside the gatehouse
- Layered thorn hedge, ditch, stone gatehouse, and sheep alarm towers built from timber stages

**Pressure and event hooks:**

- Red Tide scouts have been seen far enough east to suggest interest, not accident.
- A sheep sickness threatens to turn Helga's best market season into a year of culling.
- Someone is cutting gaps into the outer thorn belts at night and leaving no track worth trusting.

### Icebreak (Hamlet)

Population 12. Hermit Ragnhild's Northern Ice-Reach outpost at the edge of inhabitable land. No real market, only survival and the occasional blood-paid consultation.

Icebreak is not self-sustaining in any comfortable sense. It endures on seal-fat, salvage, stubbornness, and whatever rare supplies can be pushed north from Bleakwater or carried by those desperate enough to seek Ragnhild. The people here live close to the edge where hunger and devotion start using similar language.

Its economy is mostly negative space. It does not export much beyond rumor, warning, and the terrible prestige of being able to say one has been there. Yet coin and offerings still reach it, because people will travel absurd conditions for answers, absolution, or one last bargain with a woman who speaks to what waits in the ice.

**Existing structures and defenses:**

- 3 sod-walled dwellings
- 1 communal store hut, 1 seal-fat shed, and 1 snow-dug cache field
- Ragnhild's ice cave shrine
- No formal hall, smithy, or market
- Low ice walls and cut snow berms protect against wind more than men, while visibility and terror do the rest

**Pressure and event hooks:**

- A supply run is late enough that everyone is starting to count the seal stores aloud.
- Ragnhild's price for divination changes from blood to something harder to measure.
- Travelers report wrong shadows moving across the ice before dawn, always at the edge of sight and always closer on the return journey.

---

## 5. Settlement Decay and Recovery

Repeated tribute or occupation causes decay:

| Stage          | Population | Economy      | Defenses  |
| -------------- | ---------- | ------------ | --------- |
| Town           | 200+       | Strong trade | Level 3-5 |
| Large Village  | 100-200    | Active trade | Level 2-4 |
| Village        | 40-100     | Basic trade  | Level 1-3 |
| Hamlet         | 10-40      | Subsistence  | Level 0-1 |
| Deserted Ruins | 0          | None         | None      |

Each forced tribute or occupation step pushes one stage down over a season. Recovery takes 2+ seasons of peace.

---

## 6. Village Economics (Detailed)

Each settlement maintains economic state tracked in `data/political_state.yaml` and simulated by `village_politics.py`.

### Local Trade Webs and Dependency Chains

No settlement in the Rimevegr is truly self-sufficient. Travel is too slow, weather windows are too narrow, and the margin between subsistence and ruin is too small. Most economic life therefore happens in short-haul circuits between places that can reach each other within one to two hard days.

| Trade web                 | Nearby settlements                                                 | Main flows                                                     | Typical pressure points                                   |
| ------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------- | --------------------------------------------------------- |
| Inner Fjord chain         | Frostfjord Hollow, Kolvik, Stonebay, Skaldhaven, Ashen Reach       | fish, tar, hull repair, salt, cliff-path traffic, relic buyers | storms, sea-fog, harbor fees, feud spillover              |
| Forest-border belt        | Vargheim, Ashmark, Feldwick, Ashen Reach                           | charcoal, tar, hides, herbs, root stores, wagon timber         | wolf losses, occupation drain, ambush routes              |
| Deepholm short-haul basin | Deepholm, Thornwall, Raven's Perch, Skaldhaven, Vargheim, Grimholt | metal out; food, wool, charcoal, ore, labor, contracts in      | tolls, price squeezes, tunnel delay, military requisition |
| Moor survival circuit     | Thornwall, Moor's End, Bleakwater Landing, Grimholt                | wool, mutton, peat, ferries, levy traffic, poor grain exchange | exposure, flock disease, slavers, road attrition          |
| Northern desperation line | Bleakwater Landing, Icebreak, Deepholm-backed carriers             | ferry access, seal fat, fish, occult services, salvage         | thin ice, vanishing couriers, permanent scarcity          |

**Core economic truth:** villages trade most intensely with the places close enough to hurt them quickly. A nearby stronghold can be a market, protector, creditor, or parasite depending on the season and who is hungry.

### Economic Profile Template

```yaml
economy_detail:
  food_production_base: 12 # food units/week in Long Summer
  crop_fields: 8 # number of tended fields
  livestock:
    sheep: 45
    goats: 20
    cattle: 5
    pigs: 8
  food_stores_days: 140 # current stored food in person-days
  food_stores_max: 200 # granary capacity
  silver_treasury: 85
  weekly_trade_income: 12 # silver/week average
  weekly_expenses: 8 # garrison, maintenance, tribute
  labor_allocation:
    farming: 0.50
    building: 0.10
    defense: 0.20
    crafting: 0.10
    idle: 0.10
  buildings_under_construction: []
  damaged_buildings: []
```

### Settlement Economic Profiles

| Settlement         | Fields | Sheep | Goats | Cattle | Pigs | Stores | Treasury | Trade/wk |
| ------------------ | ------ | ----- | ----- | ------ | ---- | ------ | -------- | -------- |
| Frostfjord Hollow  | 6      | 30    | 15    | 3      | 5    | 120    | 45       | 10       |
| Ashen Reach        | 10     | 20    | 10    | 8      | 12   | 160    | 110      | 20       |
| Feldwick           | 4      | 40    | 10    | 2      | 3    | 40     | 8        | 4        |
| Stonebay Hamlet    | 1      | 5     | 3     | 0      | 1    | 30     | 6        | 2        |
| Grimholt           | 8      | 25    | 15    | 10     | 8    | 200    | 180      | 30       |
| Raven's Perch      | 3      | 15    | 25    | 2      | 2    | 80     | 30       | 7        |
| Vargheim           | 8      | 10    | 8     | 6      | 10   | 140    | 75       | 15       |
| Kolvik             | 5      | 8     | 5     | 2      | 4    | 100    | 60       | 12       |
| Moor's End         | 2      | 30    | 12    | 1      | 0    | 50     | 8        | 2        |
| Ashmark            | 5      | 12    | 8     | 3      | 5    | 90     | 35       | 7        |
| Deepholm           | 15     | 40    | 20    | 15     | 20   | 350    | 400      | 55       |
| Bleakwater Landing | 1      | 2     | 2     | 0      | 1    | 20     | 10       | 2        |
| Skaldhaven         | 6      | 15    | 10    | 4      | 6    | 110    | 50       | 10       |
| Thornwall          | 12     | 80    | 30    | 10     | 8    | 180    | 90       | 15       |
| Icebreak           | 0      | 0     | 2     | 0      | 0    | 10     | 0        | 0        |

---

## 7. Demographics

### Settlement Population Breakdown

| Settlement         | Children | Elderly | Women | Men | Fighters | Total |
| ------------------ | -------- | ------- | ----- | --- | -------- | ----- |
| Frostfjord Hollow  | 16       | 9       | 24    | 26  | 11       | 87    |
| Ashen Reach        | 25       | 14      | 40    | 42  | 18       | 142   |
| Feldwick           | 10       | 7       | 18    | 19  | 5        | 61    |
| Stonebay Hamlet    | 4        | 3       | 7     | 7   | 2        | 23    |
| Grimholt           | 18       | 10      | 33    | 35  | 40       | 118   |
| Raven's Perch      | 12       | 8       | 21    | 22  | 8        | 74    |
| Vargheim           | 28       | 16      | 48    | 50  | 20       | 165   |
| Kolvik             | 16       | 10      | 27    | 28  | 9        | 95    |
| Moor's End         | 5        | 4       | 9     | 10  | 3        | 31    |
| Ashmark            | 14       | 8       | 23    | 24  | 8        | 82    |
| Deepholm           | 85       | 50      | 150   | 155 | 40       | 520   |
| Bleakwater Landing | 3        | 2       | 5     | 6   | 2        | 18    |
| Skaldhaven         | 18       | 12      | 31    | 32  | 12       | 110   |
| Thornwall          | 30       | 18      | 52    | 55  | 22       | 180   |
| Icebreak           | 1        | 2       | 4     | 4   | 1        | 12    |

**Note:** Grimholt's fighter count (40) is abnormally high — Ordovast maintains a permanent garrison drawn from conquered or coerced villages. Deepholm's 40 fighters include a trained garrison funded by Sigrun's iron wealth. Most villages have fighters = 10-15% of population.

---

## 8. Political Unions

Three alliances are forming across the Rimevegr. Each represents a different approach to power: force, wealth, and cunning.

### The Iron Grip (Ordovast's Military Union)

**Overjarl:** Warchief Ordovast the Iron-Grip
**Seat:** Grimholt
**Type:** Military — obedience through force and iron control

**Members:**

| Settlement         | Role        | Loyalty | Tribute term | Notes                   |
| ------------------ | ----------- | ------- | ------------ | ----------------------- |
| Grimholt           | Core        | 5       | 0            | Ordovast's seat         |
| Raven's Perch      | Subordinate | 3       | 6 silver/month in campaign season, 18 silver/season, plus lookout service and winter stores on demand | Thane Egil, coerced |
| Bleakwater Landing | Vassal      | 2       | 2 silver/month, ferry priority, and forced crossings for Iron Grip traffic | Olaf, no choice (water) |
| Moor's End         | Tributary   | 1       | 1 sheep/month, 4 silver/season, peat carts, and labor drafts when called | Elder Brosa, reluctant |

**Combined:** Pop 241, Fighters 53, campaign-season silver equivalent about 4/week plus livestock, transport, and labor dues, Food stores 350d

**Cohesion:** 4 (Strong). Ordovast's personal authority holds it.

**War Readiness:** 2 (Mobilizing). Ordovast is calling in levies and recruiting Svarthird bands. Six months to full war footing.

<!-- SPOILER_START -->

义书丠乨乥丠乤乩乥乳丬丠乍乯乯乲丧乳丠久乮乤丠乤乥书乥乣乴乳丠乩乭乭乥乤乩乡乴乥乬乹丠丨乄乡乹丠丱丩丬丠乂乬乥乡乫乷乡乴乥乲丠乳乥乬乬乳丠乡乣乣乥乳乳丠丨乄乡乹 丠丳丩丬丠乒乡乶乥乮丧乳丠乐乥乲乣乨丠乣乬乯乳乥乳丠乧乡乴乥乳丠丨乄乡乹丠丷丩丮上上乔乲乡乪乥乣乴乯乲乹为丠乏乲乤乯乶乡乳乴丠乷乡乮乴乳丠乔乨乯乲乮乷乡乬乬丧乳 丠买乡乳乴乵乲乥乬乡乮乤丠乡乮乤丠乄乥乥买乨乯乬乭丧乳丠乳乭乩乴乨乩乥乳丮丠么乥丠乷乩乬乬丠乭乡乲乣乨丠乷乨乥乮丠乷乡乲丠乲乥乡乤乩乮乥乳乳丠乲乥乡乣乨乥乳丠临 丮丠乌乩乫乥乬乹丠乴乡乲乧乥乴丠书乩乲乳乴为丠乔乨乯乲乮乷乡乬乬丠丨乷乥乡乫乥乲丬丠乩乳乯乬乡乴乥乤丠乯乮丠乴乨乥丠乭乯乯乲乳丩丮丠义书丠乔乨乯乲乮乷乡乬乬丠书 乡乬乬乳丬丠乏乲乤乯乶乡乳乴丠乣乯乮乴乲乯乬乳丠乴乨乥丠乥乮乴乩乲乥丠乥乡乳乴乥乲乮丠乡买买乲乯乡乣乨丠乴乯丠乄乥乥买乨乯乬乭丮

<!-- SPOILER_END -->

### The Fjord Compact (Sigrun's Economic Union)

**Overjarl (de facto):** Jarl Sigrun of Deepholm
**Seat:** Deepholm
**Type:** Economic — loyalty through shared prosperity

**Members:**

| Settlement | Role     | Loyalty | Contribution        | Notes                       |
| ---------- | -------- | ------- | ------------------- | --------------------------- |
| Deepholm   | Core     | 5       | Defense funding     | Sigrun's seat, wealthiest   |
| Thornwall  | Ally     | 4       | 15 fighters/levy    | Jarl Helga, proud but loyal |
| Kolvik     | Partner  | 3       | Ship repair/trade   | Inga, commerce-driven       |
| Skaldhaven | Cultural | 3       | Rune services       | Audun, knowledge exchange   |
| Ashmark    | Buffer   | 2       | Info + safe passage | Torsten, hedging his bets   |

**Combined:** Pop 987, Fighters 91, Weekly silver 99, Food stores 830d

**Cohesion:** 3 (Functional). Requires active diplomacy. Sigrun maintains it through subsidies and fair dealing.

**War Readiness:** 1 (Alert). Sigrun prefers economics to war. She is fortifying the Grimholt-Deepholm pass and arming Thornwall. She will fight only if attacked.

<!-- SPOILER_START -->

乔乲乡乪乥乣乴乯乲乹为丠乄乥书乥乮乳乩乶乥丠乣乯乮乴乡乩乮乭乥乮乴丮丠乓乩乧乲乵乮丠乷乡乮乴乳丠乴乯丠乳乴乡乲乶乥丠乏乲乤乯乶乡乳乴丠乥乣乯乮乯乭乩乣乡乬乬乹丮 丠乓乨乥丠乩乳丠乵乮乤乥乲乳乥乬乬乩乮乧丠乇乲乩乭乨乯乬乴丧乳丠乩乲乯乮丠乩乮丠乳乯乵乴乨乥乲乮丠乭乡乲乫乥乴乳丮丠义书丠乔乨乯乲乮乷乡乬乬丠乩乳丠乡乴乴乡乣乫 乥乤丬丠乴乨乥丠乃乯乭买乡乣乴丠乭乯乢乩乬乩乺乥乳丠书乵乬乬乹丠仢亀五丠乓乩乧乲乵乮丠乣乡乮乮乯乴丠乬乯乳乥丠乔乨乯乲乮乷乡乬乬丠乷乩乴乨乯乵乴丠乬乯乳乩乮乧丠 乴乨乥丠乥乡乳乴乥乲乮丠书乬乡乮乫丮

<!-- SPOILER_END -->

### The Whispering Circle (Pale Widow's Covert Union)

**Overjarl:** The Pale Widow
**Seat:** Ashen Reach
**Type:** Covert — control through intelligence and dark arts

**Members:**

| Settlement        | Role      | Loyalty | Arrangement           | Notes                         |
| ----------------- | --------- | ------- | --------------------- | ----------------------------- |
| Ashen Reach       | Core      | 5       | Widow's seat          | Pine tar, iron smelting       |
| Frostfjord Hollow | Nominal   | 2       | Mutual convenience    | Hrothgar hedging              |
| Vargheim          | Reluctant | 2       | Defense pact (secret) | Ulf suspects seidr, distrusts |

**Combined:** Pop 394, Fighters 49, Weekly silver 45, Food stores 420d

**Cohesion:** 2 (Fragile). One exposure of dark arts loses Vargheim.

<!-- SPOILER_START -->

么乲乯乴乨乧乡乲丠乤乥书乥乣乴乳丠乴乨乥丠乭乯乭乥乮乴丠乴乨乥丠乗乩乤乯乷丠乩乳丠乴乨乲乥乡乴乥乮乥乤丮

<!-- SPOILER_END -->

**War Readiness:** 1 (Alert — but misleading). The Widow does not intend to fight conventionally.

**Dark Arts Level:** 2 (Active curse-carving). The Widow employs:

- **Seidr-worker:** "The Cave-Woman" — unnamed, lives outside Ashen Reach. Communes with the dead. Sends dream-visions. WYR 5, WIL 7. Deteriorating — has not eaten solid food in two months.
- **Curse-carver:** "Grim" — real name unknown. Carves nithing-poles and ill-runes. Can thin the Veil at specific locations. WYR 4, WIL 6. Hands shake. Eyes gone pale. Aging fast.
- **Whisper-agents:** 4-6 agents placed in Grimholt, Deepholm, Thornwall, and at Allthing gatherings. Servants, traders, healers. Report to the Widow through dead-drop rune-marks.

<!-- SPOILER_START -->

乔乨乥丠乗乩乤乯乷丧乳丠乳乴乲乡乴乥乧乹丠乩乳丠乥乲乯乳乩乯乮丮丠乓乨乥丠书乥乥乤乳丠乓乩乧乲乵乮丠乩乮乴乥乬乬乩乧乥乮乣乥丠乡乢乯乵乴丠乏乲乤乯乶乡乳乴丮丠乓 乨乥丠书乥乥乤乳丠乏乲乤乯乶乡乳乴丠书乡乬乳乥丠乲乥买乯乲乴乳丠乡乢乯乵乴丠乓乩乧乲乵乮丧乳丠乷乥乡乫乮乥乳乳丮丠乓乨乥丠乤乥乧乲乡乤乥乳丠乇乲乩乭乨乯乬乴丧乳 丠书乯乯乤丠乳乵买买乬乩乥乳丠乴乨乲乯乵乧乨丠乡乧乥乮乴乳丠乡乴丠乂乬乥乡乫乷乡乴乥乲丮丠乓乨乥丠乥乮乣乯乵乲乡乧乥乳丠么乥乬乧乡丧乳丠乡乭乢乩乴乩乯乮乳丠乴乯 丠书乲乡乣乴乵乲乥丠乴乨乥丠乆乪乯乲乤丠乃乯乭买乡乣乴丮上上义书丠乢乯乴乨丠乵乮乩乯乮乳丠乷乥乡乫乥乮丠乥乮乯乵乧乨丬丠乴乨乥丠乗乩乤乯乷丠乯书书乥乲乳丠乨乥乲 乳乥乬书丠乡乳丠乭乥乤乩乡乴乯乲丮丠义书丠乴乨乡乴丠书乡乩乬乳丬丠乴乨乥丠乣乵乲乳乥中乣乡乲乶乥乲丠乨乡乳丠乡丠书乩乮乡乬丠乯买乴乩乯乮为丠乩乮乶乯乣乡乴乩乯乮 丠乯书丠乳乯乭乥乴乨乩乮乧丠书乲乯乭丠乢乥乹乯乮乤丠乴乨乥丠乖乥乩乬丮丠乔乨乥丠买乲乥买乡乲乡乴乩乯乮乳丠乡乲乥丠乵乮乤乥乲乷乡乹丮上上乔乨乥丠乗乩乬乤乣乡乲乤 为丠乔乨乥丠乗乨乩乳买乥乲乩乮乧丠乃乩乲乣乬乥丠乩乳丠乴乨乥丠乳乭乡乬乬乥乳乴丠乵乮乩乯乮丠乡乮乤丠乴乨乥丠乭乯乳乴丠乬乩乫乥乬乹丠乴乯丠乢乥丠乤乥乳乴乲乯乹乥 乤丠乩书丠乤乩乳乣乯乶乥乲乥乤丮丠乂乵乴丠乩乴丠乨乡乳丠乳乯乭乥乴乨乩乮乧丠乴乨乥丠乯乴乨乥乲乳丠乤乯丠乮乯乴丠仢亀五丠乡乣乣乥乳乳丠乴乯丠书乯乲乣乥乳丠乴乨乡 乴丠乤乯丠乮乯乴丠乣乡乲乥丠乡乢乯乵乴丠乮乵乭乢乥乲乳丮丠乁丠乳乵乣乣乥乳乳书乵乬丠乩乮乶乯乣乡乴乩乯乮丠乣乯乵乬乤丠乳乨乡乴乴乥乲丠乡丠乧乡乲乲乩乳乯乮丮丠乁 丠乳乵乣乣乥乳乳书乵乬丠乖乥乩乬中乴乨乩乮乮乩乮乧丠乣乯乵乬乤丠乥乭买乴乹丠乡丠乳乥乴乴乬乥乭乥乮乴丠乯书丠买乥乯买乬乥丠乴乯乯丠乴乥乲乲乩书乩乥乤丠乴乯丠乳乴 乡乹丮丠乔乨乥丠乣乯乳乴丠乩乳丠乵乮买乲乥乤乩乣乴乡乢乬乥丠乡乮乤丠买乯乳乳乩乢乬乹丠乣乡乴乡乳乴乲乯买乨乩乣丮丠乔乨乥丠乐乡乬乥丠乗乩乤乯乷丠乣乯乮乳乩乤乥乲 乳丠乴乨乩乳丠乡乮丠乡乣乣乥买乴乡乢乬乥丠乲乩乳乫丮丠乓乨乥丠乨乡乳丠乬乥乳乳丠乴乯丠乬乯乳乥丮

<!-- SPOILER_END -->

---

## 9. Independent Settlements

Three settlements remain outside any union:

- **Feldwick** (occupied by Three Wolves — no capacity for alliance)
- **Stonebay Hamlet** (too small and remote to interest anyone)
- **Icebreak** (too dangerous and isolated — Veil territory)

Feldwick is the most politically relevant. If liberated, its location on the moors makes it a buffer between Ordovast's territory and the Fjord Compact. Both unions would want it. The Three Wolves' occupation prevents this question from being answered — for now.

---

## 10. Projected Political Timeline

> Encoded to prevent spoilers. Decode with:
> `python scripts/spoiler_codec.py decode-file 11_VILLAGES_AND_SETTLEMENTS.md`

<!-- SPOILER_START -->

乙丳丱串丠乓乥乡乳乯乮丠丱为丠乕乮乥乡乳乹丠买乥乡乣乥丮丠乕乮乩乯乮乳丠乣乯乮乳乯乬乩乤乡乴乩乮乧丮丠乒乡乩乤乳丠乳买乯乲乡乤乩乣丮上乙丳丱串丠乓乥乡乳乯乮丠串 为丠乏乲乤乯乶乡乳乴丠买乲乥乳乳乵乲乥乳丠乔乨乯乲乮乷乡乬乬丠乢乯乲乤乥乲丮丠乓乣乯乵乴乳丠买乲乯乢乥丮上乙丳丱串丠乓乥乡乳乯乮丠丳为丠乁乬乬乴乨乩乮乧丮丠乌乡 乳乴丠乤乩买乬乯乭乡乴乩乣丠乷乩乮乤乯乷丮上乙丳丱串丠乓乥乡乳乯乮丠临为丠乄乥乥买丠乷乩乮乴乥乲丮丠乐乯乬乩乴乩乣乡乬丠乭乡乮乥乵乶乥乲乩乮乧丮丠乗乩乤乯乷丠乡 乣乴乳丮上乙丳丱丳丠乓乥乡乳乯乮丠丱为丠乏乲乤乯乶乡乳乴丠乭乡乲乣乨乥乳丠乩书丠乲乥乡乤乩乮乥乳乳丠临丫丮丠乔乡乲乧乥乴为丠乔乨乯乲乮乷乡乬乬丮上乙丳丱丳丠乓乥 乡乳乯乮丠串中丳为丠乒乥乧乩乯乮乡乬丠乷乡乲丮丠乃乯乭买乡乣乴丠乭乯乢乩乬乩乺乥乳丮丠乗乩乤乯乷丠乷乡乴乣乨乥乳丮上乙丳丱丳丠乓乥乡乳乯乮丠临为丠乗乨乩乳买乥乲 乩乮乧丠乃乩乲乣乬乥丠乤乡乲乫丠乧乡乭乢乩乴丠乩书丠乢乯乴乨丠乷乥乡乫乥乮丮上乙丳丱临丫为丠乁书乴乥乲乭乡乴乨丠仢亀五丠乯乮乥丠乵乮乩乯乮丠乤乯乭乩乮乡乮乴丠乯 乲丠乡乬乬丠乳乨乡乴乴乥乲乥乤丮上上乔乨乥丠乢乡乮乤丠乯买乥乲乡乴乥乳丠乷乩乴乨乩乮丠乴乨乩乳丠乴乩乭乥乬乩乮乥丮丠乔乨乥乩乲丠乣乯乮乴乲乡乣乴乳丬丠乡乬乬乩乡 乮乣乥乳丬丠乡乮乤丠乣乨乯乩乣乥乳丠乡书书乥乣乴丠乴乨乥丠买乡乣乥丠乡乮乤丠乯乵乴乣乯乭乥丠乯书丠乥乶乥乮乴乳丠乴乨乥乹丠乤乯丠乮乯乴丠乣乯乮乴乲乯乬丮

<!-- SPOILER_END -->
