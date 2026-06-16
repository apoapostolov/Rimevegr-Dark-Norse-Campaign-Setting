# Weather, Seasons, and Hazards

**Project:** Iron Ledger -- Mercenaries of the Rimevegr
**Purpose:** Environmental simulation rules. Resolved by `scripts/weather.py`
and `scripts/foraging.py`.

---

## 1. The Two Great Seasons

### Long Summer (Days 1-60)

- Pale grey skies, damp cold, short days.
- Foraging: normal output.
- Travel: easier but mud and fog slow columns.
- Morale: neutral to slightly positive.

### The Long Dark (Days 61-360)

- Perpetual twilight or full darkness.
- Heavy rime, deep snow, freezing winds.
- The Veil is thickest. The Hush occurs more often.
- Food consumption +20%.
- Foraging: all terrain output reduced by 30%.
- Travel: extremely dangerous and slow.
- Morale: -1 per month without secure winter hall.

---

## 2. Weather Types

| Weather       | Freq (Dark)  | Forage     | Travel | Combat       | Special           |
| ------------- | ------------ | ---------- | ------ | ------------ | ----------------- |
| Clear Grey    | Common       | +0%        | x1.0   | +0           | None              |
| Rime-Fog      | Very Common  | -20%       | x0.7   | -10 ranged   | Hush likely       |
| Driving Snow  | Common       | -50%       | x0.5   | -20 all      | Frostbite risk    |
| Rime Storm    | Uncommon     | Impossible | x0.2   | -30 all      | High frostbite    |
| The Hush      | Rare         | +0%        | x1.0   | -20 surprise | Fear, weirdness   |
| Veil-Thinning | Very Rare    | +10%       | x1.0   | +0           | Omen, Wyrd checks |
| Blood Sun     | Extreme Rare | +0%        | x0.5   | -10 all      | Terror event      |

---

## 3. Environmental Hazards

**Black Pine Wilds (Outvegr)**
Dense trees muffle sound. Hidden roots and crevices. Occasional
whispering rune-stones or barrow entrances.

**Frozen Fjords**
Thin ice risk. Sudden rime-fog hides approaching threats. Cold water
shock if someone falls in.

**High Rime-Moors**
Treeless, endless wind. Exposure lethal without shelter. Barrows common
and more active.

**Restless Barrows**
Camping too close: nightly chance of undead stirring. Whispering runes
may give warnings or lies.

**The Hush**
Total silence (1-30 minutes). All sound-based actions fail.
Psychological fear. Morale check for superstition.

---

## 4. Foraging Tables

| Terrain           | 1-2 Foragers | 3-5 | 6-10 | 11+ |
| ----------------- | ------------ | --- | ---- | --- |
| Inner Fjords      | 4            | 10  | 18   | 30  |
| Black Pine Wilds  | 3            | 8   | 16   | 28  |
| High Rime-Moors   | 1            | 3   | 7    | 12  |
| Frozen Rivers/Ice | 0            | 2   | 4    | 8   |

Long Dark: multiply output by 0.7.
Skill bonus: average Forage skill x 8% added to output.

---

## 5. Travel and March

- Base speed: 25 km/day.
- Terrain multipliers: Coast x1.0, Forest x0.6, Moors x0.7, Mountain
  x0.4.
- Weather and season multipliers stack.
- Weak link penalty: x0.85 if band has members with NIM < 3.

---

## 6. Health Hazards

- **Frostbite:** 15% + 10% per day exposed, minus Toughness x 2%. Extra
  risk if no cloak or wounded.
- **Exhaustion:** After 3+ days deficit or forced march, -10 all rolls.
- **Infection:** 20% per day for untreated wounds in cold/wet.
- **Long Dark Madness:** Weeks without shelter causes hearing voices,
  seeing things. Morale erosion.

---

## 7. AI Rules

- Check weather daily via `weather.py`.
- Apply all modifiers to foraging, travel, morale automatically.
- Track cumulative exposure per member (especially new or weakened members).
- Hidden events can be triggered or worsened by bad weather.
