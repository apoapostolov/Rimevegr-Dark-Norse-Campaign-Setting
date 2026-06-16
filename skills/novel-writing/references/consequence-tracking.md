# Consequence Tracking — Iron Ledger

**Purpose:** The systems for ensuring that decisions, events, and
costs persist across chapters. In the Iron Ledger, consequences
are permanent. Settlements do not quietly restore. The dead stay
dead. Debts remember themselves. This document provides the tools
for tracking consequences so the novel's world behaves like a
world that keeps records — because Gest does, and the narrative
must match his ledger.

---

## The Long-Term Consequence Registry

Every major decision generates consequences that pay out across
chapters. The registry tracks what was decided, when, and when
the consequence is expected to surface.

### Registry Format

```text
DECISION: [what was done, one sentence]
CHAPTER: [chapter number where the decision was made]
CONSEQUENCE TYPE: economic | political | supernatural | personal
EXPECTED PAYOFF: [chapter range where the consequence should surface]
STATUS: pending | active | resolved | compounded

FIRST-ORDER: [immediate effect — what changed right now]
SECOND-ORDER: [what the immediate effect causes later]
THIRD-ORDER: [what the second-order effect causes — if applicable]
```

### Registry Rules

1. **Every contract generates at least one pending consequence.**
   The contract's terms, the employer's satisfaction, the
   settlement's standing change — something from every contract
   persists beyond the final payment.

2. **Consequences compound.** If the band burns a village's trust
   and later needs that village for resupply, the burned trust
   and the supply need interact. The registry tracks both — the
   original consequence and the compounding event.

3. **Consequences have payoff windows.** A consequence that never
   surfaces is wasted setup. A consequence that surfaces too
   quickly lacks weight. Target payoff windows:
   - Economic consequences: 2-5 chapters
   - Political consequences: 5-15 chapters
   - Supernatural consequences: 8-20 chapters
   - Personal consequences: variable (arc-dependent)

4. **Not all consequences are negative.** A contract completed
   well generates positive standing. A fair deal at a settlement
   generates willingness to trade again. The registry tracks
   positive consequences with the same precision as negative ones.

5. **Review the registry before planning each chapter.** Check
   which consequences are inside their payoff window. If a
   consequence's window is closing, surface it or extend the
   window with justification.

---

## Settlement Standing

Settlements are the novel's memory. Every time the band interacts
with a settlement, the interaction changes the standing. Standing
determines what the band can access next time: trade, shelter,
contracts, hostile gates, or closed gates.

### Standing Scale

| Standing | Access                                                  | How Earned                                                 |
| -------- | ------------------------------------------------------- | ---------------------------------------------------------- |
| Friendly | Full trade, shelter, contract offers, information       | Multiple fair dealings, protection provided, debts paid    |
| Neutral  | Basic trade at market prices, no extras                 | Default for first contact                                  |
| Wary     | Trade at inflated prices, no shelter, no contracts      | Rumor of bad behavior, association with a distrusted party |
| Hostile  | Refused entry, possible armed response                  | Theft, violence, broken promises, unpaid debts             |
| Closed   | Gates shut. The band does not exist to this settlement. | Severe betrayal, death caused, supernatural contamination  |

### Standing Change Rules

1. **Standing changes are permanent within the novel's timeline.**
   A settlement that drops from Neutral to Hostile does not return
   to Neutral in three chapters. Recovery requires active effort
   across multiple interactions (if recovery is possible at all).

2. **Standing changes spread.** Settlements talk to each other.
   A Hostile standing in one village degrades standing in nearby
   villages by one step within 5-10 chapters (the time it takes
   for word to travel).

3. **Standing is tracked per settlement.** Each named settlement
   in the novel has its own standing entry. The reader may not see
   the ledger, but the narrative reflects it — the elder's face
   when the band arrives tells the reader the standing before
   anyone speaks.

4. **The band can sense standing.** Voss reads a settlement's
   disposition the way he reads the weather — through observable
   facts. The quality of the bread served. Whether the elder
   meets them outside the gate or inside the hall. The number
   of armed men visible. The band adjusts its behavior to the
   standing it reads.

### Standing Tracking Format

```text
SETTLEMENT: [name]
CURRENT STANDING: [Friendly/Neutral/Wary/Hostile/Closed]
LAST INTERACTION: Chapter [N] — [what happened, one sentence]
STANDING HISTORY:
- Chapter [N]: Neutral → [change] — [reason]
- Chapter [N]: [previous] → [current] — [reason]
PENDING CONSEQUENCES: [what the band did that has not yet surfaced]
NEARBY SETTLEMENTS AFFECTED: [which settlements will hear about this]
```

---

## Character Relationship Drift

Small moments accumulate into arc-level changes. A single fire-circle
scene does not change a relationship. Twenty fire-circle scenes —
each with one small shift in proximity, speech, or gesture — change
it completely. The drift is the Iron Ledger's primary tool for
showing character change without announcing it.

### Drift Tracking Format

```text
RELATIONSHIP: [Character A] → [Character B]
BASELINE: [how the relationship started — one sentence]
CURRENT: [how the relationship stands now — one sentence]

DRIFT LOG:
- Chapter [N]: [specific small moment — who did what]
- Chapter [N]: [specific small moment]
- Chapter [N]: [specific small moment]

DIRECTION: warming | cooling | stable | complicated
ARC RELEVANCE: [which character arc does this drift serve]
```

### Drift Rules

1. **Track through physical proximity.** Who sits next to whom at
   the fire. Who marches near whom. Who shares a watch shift. These
   are the primary relationship signals. A character who was six
   seats away in Chapter 3 and three seats away in Chapter 15 has
   drifted closer. The reader may not count the seats but will feel
   the change.

2. **Track through speech patterns.** Who speaks to whom, how often,
   in what register. A named man who ignored a common in Chapter 2
   and nods at him in Chapter 20 has drifted. The nod is the
   evidence. The drift log records the nod.

3. **Track through shared work.** Who carries whose gear when a man
   is wounded. Who fills whose gap in the column. Shared labor is
   the band's language for trust.

4. **Maximum one drift beat per relationship per chapter.** Two
   drift beats in the same chapter for the same pair reads as a
   scene about the relationship rather than a scene where the
   relationship happens to be present.

5. **Drift can reverse.** A relationship that warmed across five
   chapters can cool in one — a single betrayal, a single failure.
   The reversal is more powerful because the drift log shows what
   was lost.

---

## The Empty Hex Principle

Consequences are permanent. The world does not restore itself
between chapters.

### What This Means in Practice

1. **A looted barrow stays looted.** If the band takes the silver
   and the grave goods, the barrow is empty the next time anyone
   looks. There is no respawning treasure. The consequence of
   looting is that the resource is gone — and possibly that the
   dead are angry.

2. **A burned village stays burned.** If the band — or the band's
   employer — destroys a settlement, that settlement is gone. The
   road that used to have a resupply point no longer has one. The
   tactical map has changed.

3. **A dead man stays dead.** When a Named Man dies, the gap he
   leaves is permanent. The band adapts — someone fills the
   function — but the dead man's specific contribution is gone.
   Refer to the dead man's file in the character bible. Track
   post-death references.

4. **Reputation persists.** What the band did three contracts ago
   is still known. The reputation travels ahead of the band the
   way weather travels — by the time the band arrives at a new
   settlement, the settlement has already heard something.

5. **Wounds heal on a timeline, not instantly.** A man who took a
   sword cut in Chapter 8 is not fully recovered in Chapter 9. The
   wound follows its simulation timeline — weeks for a clean cut,
   months for a deep one, complications if the conditions are bad.
   The wound is in every scene until it heals: the stiffness, the
   compensation, the man's reduced capacity.

### The Narrative Function of Permanence

Permanence gives the novel weight. If the reader knows that
decisions persist — that a village burned is a village gone, that
a man killed is a man absent — then every decision matters. The
reader does not need dramatic stakes if the ordinary stakes are
permanent. A choice to take a bad contract matters because the
cost cannot be undone.

Permanence is the reason the ledger exists. Gest records everything
because everything persists. The ledger is the novel's memory.
The consequence registry is the author's version of the ledger.
