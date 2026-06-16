# Band Simulation

<!-- notion-export:toc -->


**Project:** Iron Ledger -- Mercenaries of the Rimevegr
**Purpose:** Central simulation database for any Svarthird. Provides parseable YAML structures for band state tracking. The AI reads this at session start and maintains persistent state.

---

## 1. Band Overview Template

```yaml
band_name: "Voss's Black Axes"
tier: "Warband" # Skirmishers / Warband / Company / Host
current_size: 14
captain: "Voss Cold-Eye"
sergeant: "Gest Ledger"
current_location: "Black Pine Wilds, near Frostfjord"
morale: 4 # 1 Broken -> 5 Keen
feud_track: 1 # 0 Cold -> 4 Vengeance
standing_reputation: 3 # 0-5
last_pay_date: "Day 83, Ironmoon"
last_foraging_result: "Deficit of 3 FOOD units"
```

---

## 2. Allegiances and Contracts

```yaml
allegiances:
  - employer: "Jarl Hrothgar of Frostfjord"
    level: 2 # 0 Unknown -> 4 Sworn
    notes: "Supplied winter hall last season"
    expiry: "End of current Long Dark"

active_contracts:
  - title: "Clear the Whispering Barrow north of Frostfjord"
    employer: "Jarl Hrothgar"
    payment: "80 silver on proof of clearing + 1 thrall"
    advance_received: 25
    deadline: "Day 100, Ironmoon"
    status: "In progress"
    risk_level: "High (restless dead reported)"

completed_contracts_log: []
pending_contract_offers: []
```

---

## 3. Detailed Ledger

```yaml
treasury_silver: 47
treasury_goods_value: 32
total_debts_owed: 0
credits_to_collect: 55

weekly_retainer_cost: 38
daily_mission_cost: 9

forage_surplus_days: 2
food_stores: 11 # Current food units

grievances:
  - type: "Late wages (4 days)"
    difficulty_mod: 0
    severity: "Medium"
  - type: "Named Man (Kell) wounded"
    difficulty_mod: 0
    severity: "Low"
```

### Economy Rules (AI enforced via scripts)

- Daily FOOD consumption = 1 unit per fighter (1.2 in Long Dark).
- Foraging: run `foraging.py` with terrain, forager count, season.
- Deficit 3+ days = Morale -1, desertion risk.
- Pay cycle: retainer every 7 days, mission pay daily during work.
- Loot divided by band archetype.
- Reputation affects contract availability and payment.

---

## 4. Member Roster (Summary)

```yaml
members:
  - name: "Voss Cold-Eye"
    rank: "Captain"
    tier: "Named Man"
    loyalty: null
    condition: "Healthy"
    key_items: "Iron axe, rune-amulet, personal ledger"

  - name: "Gest Ledger"
    rank: "Sergeant"
    tier: "Named Man"
    loyalty: 4
    condition: "Healthy"
    key_items: "Charcoal ledger, ritual knife, purse"

  - name: "Kell Hook"
    rank: "Line Fighter"
    tier: "Veteran"
    loyalty: 3
    condition: "Wounded (minor axe cut)"
    key_items: "Hand axe, shield"

  - name: "Lump"
    rank: "Common Recruit"
    tier: "Common"
    loyalty: 1
    condition: "Healthy but exhausted"
    key_items: "Tin cup, small knife, threadbare blanket"
```

Full statblocks in 22_MEMBER_STATBLOCKS.md.

---

## 5. Simulation Cycle (AI Runs Each Week)

1. Calculate foraging outcome (terrain, foragers, weather).
2. Apply pay or trigger non-payment consequences.
3. Update Morale triggers and grievances.
4. Check Named Men Triggers and Agenda progress.
5. Generate new contract offers based on reputation and location.
6. Decode and check hidden events from `data/hidden/`.
7. Write updated state to `data/band_state.yaml`.
