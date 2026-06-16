# Economy Simulation Gap Report

## Summary

- Settlement profiles analyzed: 15
- Political-state economies mapped: 15
- Unions analyzed: 3
- Wolfshead bands analyzed: 10
- Faction contracts analyzed: 22

## Highest-Priority Missing Simulation

- Simulate imports, exports, and route throughput before adding more war-economy events.
- Apply union tribute, levy, and trade bonuses as real weekly treasury and supply flows.
- Give wolfshead bands recurring revenue, upkeep, and territorial pressure so they behave like economic actors instead of static lore.
- Bind faction contract payouts and sabotage outcomes to settlement and union state changes.

## Settlement Economy Gaps

- Detailed-only fields not currently represented in the weekly state model: economic_vulnerabilities, exports, imports, market, production, size, strategic_resources, terrain, trade_routes, wartime_impact
- Settlement name mismatches between detailed and political-state data: none

- `import dependency and shortage propagation` via `imports`: The detailed data tracks urgent imports, but the economy tick only uses flat income and food stores.
- `commodity production by good` via `production`: Settlements list concrete goods and weekly quantities, but no simulation converts them into stocks, trade, or bargaining power.
- `export destination throughput` via `exports`: Destination-specific exports exist, but route closures do not currently reduce settlement income by commodity or partner.
- `route-level trade flow and disruption` via `trade_routes`: Routes include frequency and goods flow, but the simulation only applies feud penalties rather than route capacity or blockade state.
- `market liquidity and local price pressure` via `market`: Market day, trader traffic, exotic goods, and price modifiers are defined but not fed into dynamic pricing.
- `strategic resource control` via `strategic_resources`: Military-economic assets like harbours, tar-works, and smithies are present only as prose.
- `wartime endurance and essential imports` via `wartime_impact`: Siege endurance and at-risk imports are authored per settlement but not simulated.
- `economic vulnerability triggers` via `economic_vulnerabilities`: Arson, blockade chokepoints, and single-point failures are enumerated but do not drive state changes.

## Union and Faction Gaps

- Union fields present but not economically simulated: dark_arts_practitioners, name, whisper_agents
- Union member fields present but not economically simulated: levy_fighters, notes, trade_bonus, tribute_livestock_monthly

- `in-kind tribute and levy extraction` via `tribute_livestock_monthly / levy_fighters`: Union member data already carries livestock tribute and levy fighters, but no weekly or monthly extraction logic applies them.
- `intra-union trade modifiers` via `trade_bonus`: Economic unions encode trade bonuses on members, but treasury and supply never use them.
- `covert network maintenance economics` via `whisper_agents`: Agents exist for intelligence, but they do not consume silver, generate smuggling leverage, or alter market confidence.
- `practitioner upkeep and dark-arts cost curves` via `dark_arts_practitioners`: The script handles dark-arts failures, but not recurring upkeep, scarcity, or recruitment economics for practitioners.

## Wolfshead Band Gaps

- Wolfshead fields present but not economically simulated: camp_defenses, camp_type, disposition, narrative_hook, notes, origin_story, relationship_to_mercenaries, survival_strategy, territory, threat_tier, winter_strategy

- `outlaw revenue model` via `survival_strategy`: Wolfshead bands explicitly earn by toll-taking, escort work, poaching, smuggling, or raiding, but none of it feeds a faction economy.
- `territory control and route predation` via `territory / camp_defenses`: Their camp locations and chokepoints should affect route risk, toll pressure, and caravan losses.
- `winter survival and family burden` via `winter_strategy / origin_story`: Some bands have children, dependents, and seasonal labor strategies that should alter desperation and raid frequency.
- `mercenary-market competition` via `relationship_to_mercenaries / disposition`: These bands compete with legal mercenaries for escort, smuggling, and intimidation work, but there is no contract-market pressure model.

## Contract-Market Gaps

- Contracts by faction: {"Jarl Sigrun's Interest": 3, "The Fjord Compact": 5, "The Free Bands": 3, "The Iron Grip": 6, "The Whispering Circle": 5}

- `faction hiring budget depletion` via `payment_silver / advance_silver`: Contract values exist, but faction treasuries do not go down when these offers appear or pay out.
- `seasonal contract demand spikes` via `season / year_range / region`: The contract market is rich enough to affect regional labor prices, but demand is not fed back into economy or manpower.
- `supply destruction consequences` via `grain-store burning / siege support contracts`: Contracts that attack granaries or hold passes should mutate settlement economy state directly.
