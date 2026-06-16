# POV Selection Logic — Iron Ledger

**Purpose:** Systematic decision framework for choosing which POV
character narrates each chapter. The Iron Ledger is a multi-POV
novel with Voss as the primary narrator and Gest and Kell as
secondary narrators. This file defines when to switch, what
triggers a non-Voss chapter, and how to maintain reader orientation
across POV changes.

> **Cross-reference:** Chapter types and their POV recommendations
> are in `chapter-structure.md`. Character voices and internal
> patterns are in `character-bible.md`. This file covers the
> selection logic itself.

---

## The Three Narrators

### Voss (Primary — ~65-75% of chapters)

**What Voss sees:** Command decisions, threat assessment, personnel
management, tactical positioning, the weight of keeping men alive.
Voss processes the world as a series of problems that need solving
before they kill someone. His attention moves from the most
dangerous thing in the room to the second most dangerous thing.

**What Voss misses:** Financial details (he trusts Gest's numbers
without checking them). Emotional undercurrents between men (he
sees loyalty and disloyalty, not the feelings that cause them).
The physical cost of what he orders (he knows a march is hard but
does not feel it the way a common does).

**Voss chapters feel like:** Controlled tension. The reader sees
the whole board through a mind that is always calculating odds.
The prose is spare, direct, tactical. Emotions exist as
complications to be managed, not experiences to be explored.

### Gest (Secondary — ~15-20% of chapters)

**What Gest sees:** Numbers, supply states, contract terms, social
dynamics, the health of individuals, patterns over time. Gest
notices what things cost. He notices who is talking to whom and
what that means for next week's roster. He notices the gap between
what Voss promises and what the ledger can deliver.

**What Gest misses:** Combat reality (he understands fighting as
a cost center, not as an experience). The supernatural (he does
not register Veil-thinning the way Voss does -- to Gest, a cold
barrow is a cold barrow). The band's mythology about itself (he
sees the ledger, not the legend).

**Gest chapters feel like:** Quiet dread. The reader sees the
numbers that predict the future while the characters do not. The
prose is precise, detail-oriented, slightly detached. Gest loves
these men but understands their mortality as a line item.

### Kell (Secondary — ~10-15% of chapters)

**What Kell sees:** Physical sensation, fear, confusion, the
experience of being at the bottom of the hierarchy. Kell is the
body in the machine. He sees the veterans from below -- their
competence, their contempt, their rituals that make no sense
until they save his life. He sees the world as a series of things
that might kill him.

**What Kell misses:** Strategy (he does not know why the band
marches where it marches). Politics (he does not know which jarl
hired them or why). The band's history (every veteran reference
to past campaigns is a gap in his knowledge that the reader
shares).

**Kell chapters feel like:** Immediacy and vulnerability. The
reader is inside a body that is cold, scared, confused, and
trying to survive. The prose is physical, present-tense in feel
even when past-tense in grammar. Kell does not analyze -- he
endures.

---

## When to Switch POV

### Switch Triggers (Use Voss Unless One of These Fires)

| Trigger                              | Switch To | Reason                                                                                          |
| ------------------------------------ | --------- | ----------------------------------------------------------------------------------------------- |
| Financial crisis or decision         | Gest      | The reader needs to see the numbers behind the command decision                                 |
| Contract negotiation (detailed)      | Gest      | Gest understands what the terms mean; Voss sees only the handshake                              |
| Supply countdown reaching critical   | Gest      | Gest's awareness of the exact state creates dramatic irony                                      |
| Voss is absent or unconscious        | Gest/Kell | The story must continue; pick the narrator who can see the most relevant information             |
| Combat from the line (not command)   | Kell      | The reader needs the ground-level experience, not the tactical overview                         |
| First encounter with new environment | Kell      | Kell's ignorance matches the reader's; his confusion becomes orientation                        |
| Emotional cost of a command decision | Kell      | Show the impact of Voss's order on the body that executes it                                    |
| Band morale from the bottom          | Kell      | Kell hears what commons say when Named Men are not listening                                    |
| Parallel events (band split)         | Gest/Kell | Whoever is not with Voss narrates what happens in the other group                               |
| Dramatic irony needed                | Gest      | Gest knows something Voss does not (a supply issue, a contract clause, a man about to desert)   |
| Physical ordeal as the point         | Kell      | When the chapter is about endurance, not decision -- the body, not the mind                     |

### Anti-Triggers (Stay with Voss)

- **Combat command decisions:** Voss narrates all tactical
  chapters. Even if Kell is more physically present, the reader
  needs the decision-maker's perspective during fights where
  command matters.
- **Supernatural encounters:** Voss narrates all Veil events.
  His flat, pragmatic processing of the uncanny is the novel's
  signature tone. Kell would panic. Gest would rationalize.
  Voss observes and acts.
- **Character confrontations:** When two Named Men clash, Voss
  narrates. He is the one who must decide what the clash means
  for the band. His judgment frames the reader's.
- **Arc climaxes:** Major turning points stay with Voss. The
  reader has spent the most time in his head and trusts his
  assessment of what moments matter.

---

## POV Distribution Rules

### Rule 1: Never Switch for Convenience

A POV switch must serve the reader's understanding, not the
writer's logistics. If information needs to reach the reader and
Voss could plausibly know it, stay with Voss. Switch only when
another narrator sees something Voss structurally cannot.

### Rule 2: Cluster, Do Not Alternate

Avoid strict rotation (Voss-Gest-Kell-Voss-Gest-Kell). Instead,
run Voss chapters in sequences of 3-5, then break for a Gest or
Kell chapter when a trigger fires. The rhythm is: Voss baseline,
then a targeted interruption that shows the reader something
different, then back to Voss.

### Rule 3: The First and Last Chapters Are Voss

Book-level framing belongs to the primary narrator. The reader
enters and exits through Voss's perspective. The first chapter
establishes his voice as the default. The last chapter returns
to it as the final word.

### Rule 4: No Solo Gest or Kell Arcs

Gest and Kell do not sustain multi-chapter sequences on their
own. Maximum two consecutive chapters from a secondary narrator
before returning to Voss. Three consecutive non-Voss chapters
make the reader forget whose story this is.

**Exception:** A band-split scenario where Voss is physically
separated from the secondary narrator. In this case, alternate
Voss and the secondary across the split, keeping each sequence
to 1-2 chapters before cutting back.

### Rule 5: Signal the Switch

The first sentence of a non-Voss chapter must signal the new
narrator within the first clause. The reader should know whose
head they are in before finishing the first sentence.

**Gest signal:** Numbers, observations, physical details about
objects or records. *The ledger's last entry was three days old.*

**Kell signal:** Body sensation, discomfort, physical labor.
*The pack strap had worn a raw line across Kell's shoulder.*

**Voss signal (returning):** Environmental scan, threat
assessment. *The ridge gave a clean view of the valley floor.
Nothing moved.*

---

## POV and Chapter Type Matrix

| Chapter Type     | Default POV | Switch Condition                            |
| ---------------- | ----------- | ------------------------------------------- |
| March            | Voss        | Kell if the march is ordeal-focused          |
| Camp             | Voss        | Gest if supply/financial crisis is the point |
| Negotiation      | Voss        | Gest for detailed contract chapters          |
| Combat (command) | Voss        | Never switch                                 |
| Combat (line)    | Kell        | When ground-level chaos is the point         |
| Settlement       | Voss        | Gest for trade/supply chapters               |
| Barrow/dungeon   | Voss        | Never switch (supernatural stays with Voss)  |
| Aftermath        | Voss        | Kell for physical cost, Gest for financial   |
| Interlude        | Any         | Whichever narrator reveals the most          |

---

## Handling POV Awareness Gaps

Each narrator creates intentional blind spots. These gaps are
features, not problems.

### What the Reader Learns from Gaps

| Voss does not see          | Reader effect                         |
| -------------------------- | ------------------------------------- |
| The exact supply state     | Anxiety about whether the band can    |
|                            | afford what Voss plans                |
| Commons' resentment        | Surprise when loyalty breaks          |
| His own emotional patterns | Reader sees what Voss cannot admit    |

| Gest does not see           | Reader effect                              |
| --------------------------- | ------------------------------------------ |
| Combat reality              | The numbers do not capture the experience  |
| Supernatural significance   | Rational gap the reader can fill           |
| Voss's tactical reasoning   | Gest's worry is sometimes misplaced        |

| Kell does not see         | Reader effect                         |
| ------------------------- | ------------------------------------- |
| Strategic context         | Reader shares his confusion           |
| The band's history        | Past references are mysterious        |
| Why orders are given      | Obedience without understanding       |

### The Gap Payoff

Information the reader gets from one narrator should recontextualize
what they learned from another. A Gest chapter that reveals the
supply state explains why Voss made a decision that seemed harsh
two chapters earlier. A Kell chapter that shows the march's
physical cost explains why the morale number in Gest's ledger
dropped. The three narrators together see the whole picture. None
of them sees it alone.

---

## Cross-References

| Topic               | Canonical File         |
| -------------------- | ---------------------- |
| Chapter types        | `chapter-structure.md` |
| Character voices     | `character-bible.md`   |
| Arc interlacing      | `plot-planning.md`     |
| Simultaneous stories | `storyline-management.md` |
| Scene transitions    | `scene-transitions.md` |
