# Economy State Authority Map

Date: `2026-04-17`

## Summary

The current economy simulation has one real mutable state owner:
`data/political_state.yaml` under the `economies` map. Almost everything else
that makes the Rimevegr economy interesting is still authored as static source
data and only partially consumed.

The current stack breaks down like this:

- `scripts/village_politics.py` is the only weekly economy tick owner.
- `data/political_state.yaml` is the only live treasury, food-store, labor, and
  demographic state file.
- `data/economy/settlement_economies.yaml` is the richest authored settlement
  economy source, but only a thin slice is used in code.
- `data/settlements.yaml` is canonical for settlement identity, terrain,
  services, built infrastructure, and defensibility, but not yet for weekly
  economy mutation.
- `data/wolfshead_bands.yaml` and `data/contracts/*.yaml` are economically rich
  authored datasets with almost no weekly-state integration.
- `scripts/ledger.py`, `scripts/contracts.py`, and
  `scripts/contract_manager.py` model band finance and contract browsing, but
  do not mutate faction or settlement treasuries.

The main structural gap is not lack of data. It is lack of transfer from
authored data into weekly state variables that can be ticked, inspected, and
depleted.

## Authority Table

| Domain | Canonical authored source | Live mutable state | Active consumer | What is actually simulated now | Main gap |
| ------ | ------------------------- | ------------------ | --------------- | ------------------------------ | -------- |
| Settlement identity and baseline features | `data/settlements.yaml` | none | `settlement.py`, `village_politics.py` | size, terrain, feud level, defensibility, infrastructure lookup | no weekly mutation of structure or service capacity from economy outcomes |
| Detailed settlement economy profile | `data/economy/settlement_economies.yaml` | none | `village_politics.py`, `settlement.py`, `ledger.py` | route throughput bonus, some import cost pressure, market price modifier lookup | production, exports, vulnerabilities, strategic resources, and wartime endurance are mostly not stateful |
| Route network | `data/geography/routes.yaml` | none | `village_politics.py` | seasonal access and traffic folded into a route-throughput scalar | no route stock flow, blockade state, or partner-specific commodity loss |
| Settlement weekly treasury and stores | `data/political_state.yaml` under `economies` | `data/political_state.yaml` | `village_politics.py` | food stores, treasury, crop fields, livestock, labor allocation, flat trade income/expense | state is too flat and disconnected from authored goods and dependencies |
| Demographics and fighters | `data/political_state.yaml` under `demographics` | `data/political_state.yaml` | `village_politics.py` | births, disease, starvation, cold deaths | levy extraction and labor shortage are not economically integrated enough |
| Union structure | `data/political_state.yaml` under `unions` | `data/political_state.yaml` | `village_politics.py` | cohesion, war readiness, combined treasury reporting, dark-arts narration | tribute, in-kind dues, trade bonuses, levy fighters, and covert upkeep do not flow into economy state |
| Tribute terms | `data/political_state.yaml` union member fields | none beyond prose-like fields in same file | `village_politics.py` reporting only | values are stored | no weekly/monthly extraction logic |
| Dark arts and covert network | `data/political_state.yaml` union dark-arts fields | partial mutation of practitioner health | `village_politics.py` | event text and catastrophic outcomes | no recurring silver, scarcity, smuggling, or confidence economics |
| Wolfshead bands | `data/wolfshead_bands.yaml` | none | currently no economy-state consumer | none in weekly economy | no revenue, pressure, predation, or winter burden state |
| Contract database | `data/contracts/*.yaml` | none | `contract_manager.py`, `contracts.py` | browsing, filtering, pay display, simple evaluation | no employer budget depletion or settlement-economy mutation on outcome |
| Band treasury and payroll | band files plus script inputs | external band JSON/YAML, not regional state | `ledger.py` | pay cycles, loot, trade pricing, upkeep, occupation and tribute calculations for the band | separate from faction, settlement, and union treasuries |
| Settlement CLI visibility | `data/settlements.yaml`, `data/economy/settlement_economies.yaml` | none | `settlement.py` | infrastructure info, market lookups, animal stock, economy profile display | no direct readout of live weekly economy state from `political_state.yaml` |

## Current Weekly State Variables

The current mutable settlement-economy state in `data/political_state.yaml` is:

- `crop_fields`
- `livestock`
- `food_stores_days`
- `food_stores_max`
- `silver_treasury`
- `weekly_trade_income`
- `weekly_expenses`
- `labor_allocation`

These are the only settlement variables currently advanced by the weekly tick.

## What `village_politics.py` Actually Uses

The current weekly economy tick in `scripts/village_politics.py` uses:

- season
- population totals
- labor allocation
- crop fields
- livestock
- flat weekly trade income and expenses
- feud trade penalty
- route throughput scalar
- import urgency aggregate
- a crude export bonus
- a crude food import bonus

It does not maintain commodity stocks by good, route partner balances, union
tribute drains, contract-market depletion, or outlaw pressure.

## State Variables Missing From The Weekly Tick

### Settlement economy variables authored but not stateful

- production by named good
- import dependency by named good
- export dependency by destination and good
- market liquidity, trader frequency, and stall capacity
- strategic resource control
- siege endurance and essential imports at risk
- vulnerability-trigger state such as arson, blockade chokepoints, or smithy
  failure

### Union variables authored but not stateful

- `tribute_livestock_monthly`
- `trade_bonus`
- `levy_fighters`
- `whisper_agents` upkeep and leverage
- `dark_arts_practitioners` recurring cost and recruitment pressure

### Wolfshead variables authored but not stateful

- survival strategy revenue
- territory pressure on routes
- camp defense impact on suppression cost
- family burden and winter desperation
- mercenary-market competition

### Contract-market variables authored but not stateful

- employer budget pools
- `payment_silver` and `advance_silver` depletion from faction treasuries
- demand spikes by season and year
- economic consequences of sabotage, escort success, or supply destruction
- contract-induced changes to route safety, shortages, and market prices

## Practical Ownership Conclusions

1. `village_politics.py` should remain the weekly regional-economy tick owner.
2. `data/political_state.yaml` should remain the live mutable store, but it
   needs a richer economy subtree.
3. `data/economy/settlement_economies.yaml` should be treated as canonical
   authored input for production, imports, exports, markets, vulnerabilities,
   and wartime resilience.
4. `data/wolfshead_bands.yaml` and `data/contracts/*.yaml` should stop being
   read-only lore pools and become economic event/input sources.
5. `ledger.py` should stay band-finance focused, but any employer or settlement
   side-effects from contracts need a bridge into `political_state.yaml`.

## Recommended Next Implementation Order

1. Settlement production and stock state.
2. Import-shortage propagation.
3. Route throughput and market liquidity.
4. Union tribute and treasury flows.
5. Wolfshead route pressure and outlaw revenue.
6. Contract-budget depletion and consequence wiring.
