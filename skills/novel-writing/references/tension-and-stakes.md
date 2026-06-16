# Tension and Stakes — Iron Ledger

**Purpose:** The specific tension sources available in mercenary
fiction and how the simulation generates them automatically. Tension
in the Iron Ledger is not manufactured by the author — it is an
emergent property of the band's arithmetic. When food is at three
days and the nearest settlement is five days away, the tension
exists before a word is written. The author's job is to render
it as lived experience.

---

## Tension Sources

### 1. The Ledger Gap

**What it is:** The difference between what the band needs and
what the treasury holds. When income stops and expenses continue,
the gap widens. The gap is Gest's constant companion — the number
he carries that determines every decision.

**How it creates tension:** The reader learns to read the ledger
the way Gest reads it. When the treasury drops below two weeks of
operating costs, every scene carries the weight of the gap. A
camp scene where Dalla serves thinner stew is not a camp scene —
it is a scene about the gap made physical.

**Simulation trigger:** Treasury below 14 silver (two weeks of
base costs at 1 silver/day).

**Rendering:** Through Gest's precision. He does not say "we're
running low." He says "Down to nine." The number is the tension.
Through Voss's decisions — the contracts he takes because he
cannot afford to refuse. Through the men — watch their behavior
when pay is late.

---

### 2. The Morale Cliff

**What it is:** The threshold where the band stops functioning
as a unit. Above the cliff, complaints are individual. Below
it, complaints become collective. Below the cliff, desertion
becomes rational.

**How it creates tension:** The reader feels the cliff through
the band's behavior. The jokes stop. The spacing at the fire
widens. Men eat alone. Watch shifts get sloppy. The band is
still the band, but the adhesive is failing.

**Simulation trigger:** Morale at 3 or below (on the 1-5 scale:
Keen / Steady / Shaken / Wavering / Broken — see
`simulation-rendering-guide.md`).

**Rendering:** Never state morale as a number. Show it through:
silence where there should be noise, complaints that used to
stay private going public, the way men look at Voss when he
gives an order — compliance with a fraction-of-a-second delay
that did not used to be there. The delay is the cliff made
visible.

---

### 3. The Supply Countdown

**What it is:** Food, water, and essential supplies expressed
as days remaining. The countdown is always running. The band
eats every day whether it fights or not.

**How it creates tension:** The countdown creates inexorable
pressure. Unlike combat (which is sudden) or politics (which
can be deferred), the food supply degrades by one unit per
day. It cannot be argued with. It cannot be postponed. It is
the most democratic threat the band faces — everyone starves
at the same rate.

**Simulation trigger:** Food below 7 days of supply for the
current roster.

**Rendering:** Through physical detail. Pack weight (lighter
packs mean less food). The stew (thinner, more water, fewer
vegetables). Gest's count — precise and unsparing. The
foraging parties — Petra out longer, coming back with less.
The conversation the men do not have but think about: who
eats first if it comes to that.

---

### 4. The Rival Band

**What it is:** Another mercenary company operating in the
same territory. Competition for the same contracts, the same
employers, the same settlements. The rival band is a mirror
that shows the reader what the band could become or what
it is trying to avoid becoming.

**How it creates tension:** The rival band compresses the
economic margin. If the rival undercuts the band's price,
Voss must decide: match the price (and eat the margin) or
lose the contract (and eat nothing). The rival also creates
physical danger — mercenary companies that compete for
territory sometimes solve the competition directly.

**Rendering:** Through reputation. The settlements talk about
the rival the way they talk about weather — as a fact of the
landscape. Through pricing pressure — Gest's numbers getting
worse because the market has more swords than it needs.
Through direct encounter if it comes to that — but mainly
through the economic shadow the rival casts.

---

### 5. The Employer's Betrayal

**What it is:** The contract is not what it appeared. The
employer lied about the danger, the target, the payment, or
the opposition. The band discovers mid-contract that the terms
have changed — but the band is already deployed.

**How it creates tension:** The band is committed. Walking away
mid-contract costs reputation (future employers hear about it).
Finishing a poisoned contract costs blood. Renegotiating
mid-contract costs leverage. Every option has a price and Voss
must choose which price to pay.

**Rendering:** Through the gap between what was promised and
what is found. The employer said bandits — it is a war band.
The employer said escort — it is a siege. The employer said
twenty silver — the steward's face when Gest presents the
bill says the twenty silver does not exist. The betrayal is
revealed through observable facts, not through dramatic
exposure.

---

### 6. The Internal Grievance

**What it is:** A complaint within the band that festers. Pay
distribution. Workload. A personal conflict between two men.
A decision by Voss that some men disagree with. The grievance
is the political arc's smallest unit — it affects only the
band, not external factions.

**How it creates tension:** The grievance threatens cohesion.
A band that fights itself cannot fight its contracts. The
grievance creates scenes where men who should be cooperating
are instead maneuvering — around the fire, in the march order,
in the loot division. The reader feels the friction in the
small spaces.

**Simulation trigger:** Morale below 4 combined with an
unresolved grievance event (pay dispute, death blame, loot
complaint).

**Rendering:** Through proximity changes. Who stops sitting
next to whom. Who speaks and who does not. The grievance is
never stated as "the men are unhappy about X." It is shown
as behavior — the look Ubbe gives when Voss announces the
march order, the way the commons eat separately from the
Named Men, the silence where there used to be jokes.

---

### 7. The Supernatural Debt

**What it is:** Something the band took or did that the
supernatural world has not forgotten. A barrow looted. A
rite interrupted. A ward broken. The debt does not announce
itself — it manifests as consequences that arrive later,
disconnected from the original act in time but not in
causation.

**How it creates tension:** The reader knows (or suspects) a
debt exists before the characters do. The barrow they looted
in Chapter 4 begins paying its bill in Chapter 12 — not as a
monster attack but as sleep that goes wrong, a wound that will
not close, a settlement that refuses them entry because "the
dead are restless since you came."

**Rendering:** Through physical symptoms that the band cannot
explain. Through Thorne, who connects the symptoms to the
cause but cannot fix it — only warn. Through the accumulation
of small wrongnesses that the practical men attribute to bad
luck but that the reader attributes to the debt.

---

## Simulation-Driven Tension

### The Automatic Tension Engine

The simulation generates tension without authorial intervention.
When the numbers cross thresholds, the prose reflects it. The
author does not decide "this chapter should be tense." The
author reads the simulation state and renders what the numbers
mean for bodies.

| Simulation State                 | Tension Level | What the Prose Feels Like                                             |
| -------------------------------- | ------------- | --------------------------------------------------------------------- |
| Treasury adequate, food adequate | Baseline      | The band's routine. The metronome. Normal operations.                 |
| Treasury low OR food low         | Elevated      | One system under pressure. Decisions have visible cost.               |
| Treasury low AND food low        | High          | Multiple systems under pressure. Every decision is a tradeoff.        |
| Morale below cliff               | Critical      | The band's cohesion is failing. Individual survival calculus emerges. |
| Wounded Named Man                | Elevated+     | A capability gap. Someone must fill it. The filler is stretched.      |
| Death in the band                | Spike         | Immediate impact: roster, morale, economics. Cascading adjustments.   |
| Supernatural event active        | Elevated+     | A pressure the band cannot manage with competence alone.              |
| Multiple systems critical        | Maximum       | Everything is failing simultaneously. The prose should feel airless.  |

### Tension Without Events

The most effective tension in the Iron Ledger comes from states,
not events. A band with 4 days of food and 6 days of march ahead
is tense before anything happens. A chapter that is just the march
— footsteps, pack weight, the stew getting thinner — is a tension
chapter without a single dramatic event.

This is the Cook inheritance: the daily grind as suspense. The
reader knows the numbers (through Gest's reports, through the
physical rendering of scarcity) and the numbers themselves
generate the question: will they make it?

---

## Escalation Patterns

### Stacking Tensions Within a Single Arc

Effective escalation is not one big thing getting bigger. It is
multiple small things converging until the margin disappears.

### Pattern: The Narrowing Margin

1. One system under pressure (food running low).
2. A second system joins (morale dropping because food is low).
3. A complication arrives (employer changes the terms, weather
   turns, a man is wounded).
4. The margin between survival and failure narrows to the width
   of one decision.
5. The decision is made. The cost is counted.

### Pattern: The Slow Boil

1. A minor tension is introduced and left unresolved (a
   grievance, a debt, a suspicious employer).
2. The tension is buried under active events (the contract, the
   march, the fight).
3. The buried tension resurfaces at the worst possible moment —
   when another tension is already active.
4. The two tensions interact. The grievance becomes a desertion
   threat during a supply crisis. The debt comes due during a
   fight.

### Pattern: The False Resolution

1. A tension is apparently resolved (the contract pays, the food
   is resupplied, the grievance is addressed).
2. The resolution had a hidden cost (the payment came from a
   faction that now considers the band indebted, the food
   resupply required a detour that burned time, the grievance
   was suppressed not resolved).
3. The hidden cost generates a new tension that is worse than the
   original because the band thought it was safe.

### Escalation Across the Novel

The novel's macro-escalation follows a simple rule: the margin
gets thinner.

- **Early chapters:** The band operates with adequate margin.
  Mistakes are absorbable. A bad contract costs silver but not
  lives. Tensions are individual and manageable.
- **Middle chapters:** The margin has thinned. Mistakes cost more.
  Tensions stack. The band can still recover, but recovery takes
  longer and costs more than it used to.
- **Late chapters:** The margin is gone. Every decision is existential.
  Tensions are simultaneous. The band cannot recover from a mistake
  because there is no reserve to absorb it.

The reader should feel the thinning the way Gest feels it — not
as dramatic escalation but as the numbers getting slowly,
inexorably worse.
