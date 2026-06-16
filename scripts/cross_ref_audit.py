#!/usr/bin/env python3
"""Cross-reference audit of all YAML data files in the norse_grit project."""

import yaml, os, glob, re
from collections import Counter, defaultdict

base = '/home/apoapostolov/git/lifestyle/writing/norse_grit'

def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)

warnings = []
failures = []
passes = []
info_lines = []

def warn(section, msg):
    warnings.append(f"[{section}] {msg}")

def fail(section, msg):
    failures.append(f"[{section}] {msg}")

def ok(section, msg):
    passes.append(f"[{section}] {msg}")

def info(section, msg):
    info_lines.append(f"[{section}] {msg}")

# ============================================================
# 1. LOAD ALL DATA
# ============================================================

# --- Settlements ---
settlements_data = load_yaml(f'{base}/data/settlements.yaml')
settlement_names = set()
for s in settlements_data.get('settlements', []):
    settlement_names.add(s['name'])
print(f"Loaded {len(settlement_names)} settlements", flush=True)

settlement_positions = set()
if 'settlement_positions' in settlements_data:
    for name in settlements_data['settlement_positions']:
        settlement_positions.add(name)

# --- Geography: Atlas ---
atlas_data = load_yaml(f'{base}/data/geography/atlas.yaml')
atlas_ids = set()
atlas_names = set()
atlas_npcs = set()
atlas_barrows = set()
for loc in atlas_data.get('locations', []):
    lid = loc.get('id', '')
    atlas_ids.add(lid)
    atlas_names.add(loc.get('name', ''))
    for npc in loc.get('associated_npcs', []):
        atlas_npcs.add(npc)
    for bar in loc.get('associated_barrows', []):
        atlas_barrows.add(bar)
print(f"Loaded {len(atlas_ids)} atlas locations", flush=True)

# --- Geography: Routes ---
routes_data = load_yaml(f'{base}/data/geography/routes.yaml')
routes = routes_data.get('routes', [])
print(f"Loaded {len(routes)} routes", flush=True)

# --- NPCs ---
npc_files = glob.glob(f'{base}/data/npcs/*.yaml')
all_npcs = {}
npc_names = set()
npc_ids = set()
npc_locations = {}
npc_skip = ('NPC_SCHEMA.md', 'relationship_web.yaml')
for nf in sorted(npc_files):
    fname = os.path.basename(nf)
    if fname in npc_skip:
        continue
    data = load_yaml(nf)
    if data is None:
        continue
    for npc in data.get('npcs', []):
        nid = npc.get('id', '')
        name = npc.get('name', '')
        npc_ids.add(nid)
        npc_names.add(name)
        all_npcs[nid] = npc
        loc = npc.get('settlement') or npc.get('base') or npc.get('location') or ''
        if loc:
            npc_locations[name] = loc
print(f"Loaded {len(npc_ids)} NPCs", flush=True)

# --- Relationship Web ---
relweb_data = load_yaml(f'{base}/data/npcs/relationship_web.yaml')
relweb_edges = relweb_data.get('edges', [])
print(f"Loaded {len(relweb_edges)} relationship web edges", flush=True)

# --- Bestiary ---
bestiary_files = glob.glob(f'{base}/data/bestiary/*.yaml')
enemy_ids = set()
enemy_names = {}
bestiary_skip = ('encounters.yaml', 'BESTIARY_SCHEMA.md', 'image_prompts.md')
for bf in sorted(bestiary_files):
    fname = os.path.basename(bf)
    if fname in bestiary_skip:
        continue
    data = load_yaml(bf)
    if data is None:
        continue
    for enemy in data.get('enemies', []):
        eid = enemy.get('id', '')
        enemy_ids.add(eid)
        enemy_names[eid] = enemy.get('name', '')
print(f"Loaded {len(enemy_ids)} enemy IDs from bestiary", flush=True)

# --- Encounters ---
encounters_data = load_yaml(f'{base}/data/bestiary/encounters.yaml')
encounters = encounters_data.get('encounters', [])
print(f"Loaded {len(encounters)} pre-built encounters", flush=True)

# --- Barrow encounter tables ---
barrow_enc_data = load_yaml(f'{base}/data/barrows/encounter_tables.yaml')
barrow_encounters = barrow_enc_data.get('encounter_tables', [])
print(f"Loaded {len(barrow_encounters)} barrow encounter entries", flush=True)

# --- Barrows ---
barrows_data = load_yaml(f'{base}/data/barrows/barrows.yaml')
barrow_ids = set()
barrow_names = {}
barrows = barrows_data.get('barrows', [])
for b in barrows:
    bid = b.get('id', '')
    barrow_ids.add(bid)
    barrow_names[bid] = b.get('name', '')
print(f"Loaded {len(barrow_ids)} barrows", flush=True)

# --- Contracts ---
contract_files = glob.glob(f'{base}/data/contracts/*.yaml')
contract_ids = set()
all_contracts = {}
for cf in sorted(contract_files):
    data = load_yaml(cf)
    if data is None:
        continue
    for c in data.get('contracts', []):
        cid = c.get('id', '')
        contract_ids.add(cid)
        all_contracts[cid] = c

ca_path = f'{base}/data/contracts_available.yaml'
if os.path.exists(ca_path):
    ca_data = load_yaml(ca_path)
    if ca_data:
        for c in ca_data.get('contracts', ca_data.get('available', [])):
            if isinstance(c, dict):
                cid = c.get('id', '')
                if cid:
                    contract_ids.add(cid)
                    all_contracts[cid] = c
print(f"Loaded {len(contract_ids)} contracts", flush=True)

# --- Events ---
event_files = glob.glob(f'{base}/data/events/*.yaml')
all_events = {}
event_ids_by_file = defaultdict(list)
events_by_year = Counter()
for ef in sorted(event_files):
    fname = os.path.basename(ef)
    if fname == 'EVENT_SCHEMA.md':
        continue
    data = load_yaml(ef)
    if data is None:
        continue
    for ev in data.get('events', []):
        eid = ev.get('id', '')
        all_events[eid] = ev
        event_ids_by_file[fname].append(eid)
        year = ev.get('year', 0)
        events_by_year[year] += 1
print(f"Loaded {len(all_events)} events", flush=True)

# --- Volumes ---
volume_files = glob.glob(f'{base}/data/volumes/volumes_*.yaml')
volume_event_refs = set()
for vf in sorted(volume_files):
    data = load_yaml(vf)
    if data is None:
        continue
    def extract_event_ids(obj, depth=0):
        if depth > 10:
            return
        if isinstance(obj, str):
            for m in re.finditer(r'EVT_\d+_\w+', obj):
                volume_event_refs.add(m.group())
        elif isinstance(obj, dict):
            for v in obj.values():
                extract_event_ids(v, depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                extract_event_ids(item, depth + 1)
    extract_event_ids(data)
print(f"Found {len(volume_event_refs)} volume event refs", flush=True)

# ============================================================
# 2. SETTLEMENT CROSS-REFERENCES
# ============================================================
section = "Settlements"

all_known_locations = settlement_names | atlas_names

events_unknown_loc = []
for eid, ev in all_events.items():
    loc = ev.get('location', '')
    if loc and loc not in all_known_locations:
        events_unknown_loc.append((eid, loc))

if events_unknown_loc:
    locs = sorted(set(l for _, l in events_unknown_loc))
    warn(section, f"{len(events_unknown_loc)} events reference {len(locs)} locations not in settlements or atlas")
    for loc in locs:
        evts = [eid for eid, l in events_unknown_loc if l == loc]
        info(section, f"  '{loc}' referenced by {len(evts)} events")
else:
    ok(section, "All event locations match known settlements or atlas locations")

contracts_unknown_sett = []
for cid, c in all_contracts.items():
    sett = c.get('settlement', '')
    if sett and sett not in settlement_names:
        contracts_unknown_sett.append((cid, sett))

if contracts_unknown_sett:
    warn(section, f"{len(contracts_unknown_sett)} contracts reference unknown settlements")
else:
    ok(section, "All contract settlements match known settlements")

npc_unknown_loc = []
for name, loc in npc_locations.items():
    if loc and loc not in all_known_locations:
        npc_unknown_loc.append((name, loc))

if npc_unknown_loc:
    warn(section, f"{len(npc_unknown_loc)} NPCs reference locations not in settlements or atlas")
else:
    ok(section, "All NPC locations match known settlements or atlas locations")

if settlement_positions:
    missing = settlement_names - settlement_positions
    extra = settlement_positions - settlement_names
    if missing or extra:
        if missing:
            warn(section, f"{len(missing)} settlements missing from settlement_positions")
        if extra:
            warn(section, f"{len(extra)} extra names in settlement_positions")
    else:
        ok(section, "settlement_positions matches settlements list exactly")

# ============================================================
# 3. ROUTE CROSS-REFERENCES
# ============================================================
section = "Routes"

route_unknown = []
route_fuzzy = []
for r in routes:
    for field in ('from_settlement', 'to_settlement'):
        name = r.get(field, '')
        if name and name not in settlement_names:
            fuzzy = [sn for sn in settlement_names if name in sn or sn.startswith(name)]
            if fuzzy:
                route_fuzzy.append((r.get('id', ''), name, fuzzy[0]))
            else:
                route_unknown.append((r.get('id', ''), name))

if route_unknown:
    fail(section, f"{len(route_unknown)} route endpoints reference unknown settlements (no match)")
    for rid, name in route_unknown:
        info(section, f"  Route {rid} -> '{name}'")
elif route_fuzzy:
    warn(section, f"{len(route_fuzzy)} route endpoints use shortened names (fuzzy match)")
    for rid, short, full in route_fuzzy:
        info(section, f"  Route {rid}: '{short}' -> likely '{full}'")
else:
    ok(section, f"All {len(routes)} route endpoints match known settlements")

travel_routes = settlements_data.get('travel_routes', [])
travel_unknown = []
for tr in travel_routes:
    fr = tr.get('from', '')
    to = tr.get('to', '')
    if fr and fr not in settlement_names:
        travel_unknown.append(f"from '{fr}'")
    if to and to not in settlement_names:
        travel_unknown.append(f"to '{to}'")

if travel_unknown:
    warn(section, f"{len(travel_unknown)} travel_route endpoints reference unknown settlements")
else:
    ok(section, f"All {len(travel_routes)} travel_route endpoints match known settlements")

route_lm_unknown = []
for r in routes:
    for lm in r.get('landmarks', []):
        if lm not in atlas_ids:
            route_lm_unknown.append((r.get('id', ''), lm))

if route_lm_unknown:
    warn(section, f"{len(route_lm_unknown)} route landmark refs not in atlas")
else:
    ok(section, "All route landmark references match atlas location IDs")

# ============================================================
# 4. NPC CROSS-REFERENCES
# ============================================================
section = "NPCs"

npc_name_lookup = set()
npc_call_names = set()
for nid, npc in all_npcs.items():
    npc_name_lookup.add(npc.get('name', ''))
    cn = npc.get('call_name', '')
    if cn:
        npc_call_names.add(cn)
    first = npc.get('name', '').split()[0] if npc.get('name', '') else ''
    if first:
        npc_name_lookup.add(first)

all_npc_identifiers = npc_name_lookup | npc_call_names

event_actors = set()
for eid, ev in all_events.items():
    for a in ev.get('actors', []):
        event_actors.add(a)

actors_missing = sorted(a for a in event_actors if a not in all_npc_identifiers)
if actors_missing:
    warn(section, f"{len(actors_missing)} event actors not in NPC database (may be band members)")
    for a in actors_missing:
        info(section, f"  Actor '{a}'")
else:
    ok(section, "All event actors found in NPC database")

# Relationship web - categorize missing refs
relweb_names = set()
for edge in relweb_edges:
    relweb_names.add(edge.get('source_name', ''))
    relweb_names.add(edge.get('target', ''))

relweb_missing_npcs = []
relweb_non_npc = []
for n in sorted(relweb_names):
    if not n or n in all_npc_identifiers:
        continue
    if (n in settlement_names or n in barrow_ids or
        n.startswith('BAR_') or n.startswith('NPC_') or
        n.startswith('SUP_') or n.startswith('CONT_') or
        any(n in sn for sn in settlement_names)):
        relweb_non_npc.append(n)
    else:
        relweb_missing_npcs.append(n)

if relweb_missing_npcs:
    warn(section, f"{len(relweb_missing_npcs)} relationship_web names not in NPC files (may be band members or unnamed NPCs)")
    for name in relweb_missing_npcs:
        info(section, f"  '{name}'")
else:
    ok(section, "All relationship_web person names found in NPC files")

if relweb_non_npc:
    info(section, f"{len(relweb_non_npc)} relationship_web refs are settlements/barrows/IDs (expected)")

# ============================================================
# 5. BESTIARY CROSS-REFERENCES
# ============================================================
section = "Bestiary"

enc_unknown = []
for enc in encounters:
    for er in enc.get('enemies', []):
        eid = er.get('enemy_id', '')
        if eid and eid not in enemy_ids:
            enc_unknown.append((enc.get('id', ''), eid))

if enc_unknown:
    warn(section, f"{len(enc_unknown)} encounter enemy refs not in bestiary")
else:
    ok(section, f"All enemy refs in {len(encounters)} encounters match bestiary IDs")

barrow_enc_unknown = []
for benc in barrow_encounters:
    for er in benc.get('enemies', []):
        eid = er.get('id', '') if isinstance(er, dict) else ''
        if eid and eid not in enemy_ids:
            barrow_enc_unknown.append((benc.get('id', ''), eid))

if barrow_enc_unknown:
    missing_ids = sorted(set(eid for _, eid in barrow_enc_unknown))
    warn(section, f"{len(barrow_enc_unknown)} barrow encounter refs use {len(missing_ids)} enemy IDs not in bestiary")
    for eid in missing_ids:
        info(section, f"  Missing: '{eid}'")
else:
    ok(section, f"All enemy refs in {len(barrow_encounters)} barrow encounters match bestiary")

barrow_occ_unknown = []
for b in barrows:
    occ = b.get('occupants', {})
    all_occ = []
    if occ.get('primary'):
        all_occ.append(occ['primary'])
    if occ.get('boss'):
        all_occ.append(occ['boss'])
    for s in occ.get('secondary', []):
        all_occ.append(s)
    for oid in all_occ:
        if oid and oid not in enemy_ids:
            barrow_occ_unknown.append((b.get('id', ''), oid))

if barrow_occ_unknown:
    missing_ids = sorted(set(eid for _, eid in barrow_occ_unknown))
    warn(section, f"{len(barrow_occ_unknown)} barrow occupant refs use {len(missing_ids)} IDs not in bestiary")
    for eid in missing_ids:
        info(section, f"  Missing: '{eid}'")
else:
    ok(section, "All barrow occupant IDs match bestiary entries")

# ============================================================
# 6. CONTRACT CROSS-REFERENCES
# ============================================================
section = "Contracts"

contract_enemy_unknown = []
for cid, c in all_contracts.items():
    sup = c.get('supernatural_elements', {})
    if sup:
        for ut in sup.get('undead_types', []):
            if ut not in enemy_ids:
                contract_enemy_unknown.append((cid, ut))

if contract_enemy_unknown:
    warn(section, f"{len(contract_enemy_unknown)} contract enemy refs not in bestiary")
else:
    ok(section, "All contract enemy references match bestiary IDs")

contract_ref_missing = []
for cid, c in all_contracts.items():
    pol = c.get('political_conditions', {})
    if pol:
        req = pol.get('requires_event', '')
        if req and req not in all_events:
            contract_ref_missing.append((cid, f"requires_event: {req}"))
    cons = c.get('consequences', {})
    for outcome in ('success', 'failure'):
        od = cons.get(outcome, {})
        if isinstance(od, dict):
            for u in (od.get('unlocks') or []):
                if u.startswith('CONT_') and u not in contract_ids:
                    contract_ref_missing.append((cid, f"unlocks: {u}"))

if contract_ref_missing:
    warn(section, f"{len(contract_ref_missing)} contract refs to missing events/contracts")
else:
    ok(section, "All contract event/unlock references are valid")

# ============================================================
# 7. BARROW CROSS-REFERENCES
# ============================================================
section = "Barrows"

barrow_sett_unknown = []
for b in barrows:
    ns = b.get('nearest_settlement', '')
    if ns and ns not in settlement_names:
        barrow_sett_unknown.append((b.get('id', ''), ns))

if barrow_sett_unknown:
    warn(section, f"{len(barrow_sett_unknown)} barrows reference unknown nearest_settlement")
else:
    ok(section, "All barrow nearest_settlement refs match known settlements")

atlas_bar_unknown = [b for b in atlas_barrows if b not in barrow_ids]
if atlas_bar_unknown:
    warn(section, f"{len(atlas_bar_unknown)} atlas barrow refs not in barrows.yaml")
else:
    ok(section, "All atlas barrow references match barrows.yaml")

# ============================================================
# 8. EVENT ID CONSISTENCY
# ============================================================
section = "Events"

# Accept all observed patterns: S01, A01, W01, U01, PER, PER01, SUP, SUP01
evt_pattern = re.compile(r'^EVT_\d{3}_[A-Z]{1,3}\d{0,2}_\d{3}$')
bad_format = [eid for eid in all_events if not evt_pattern.match(eid)]
if bad_format:
    warn(section, f"{len(bad_format)} events don't match expected ID format")
    for eid in bad_format[:15]:
        info(section, f"  Non-standard: '{eid}'")
else:
    ok(section, "All event IDs match expected format patterns")

# Format breakdown
format_counts = Counter()
for eid in all_events:
    m = re.match(r'EVT_\d{3}_([A-Z]+)\d*_\d{3}', eid)
    if m:
        format_counts[m.group(1)] += 1
info(section, "Event ID prefixes: " + ", ".join(f"{k}={v}" for k, v in sorted(format_counts.items())))

all_evt_ids = []
for ids in event_ids_by_file.values():
    all_evt_ids.extend(ids)
dups = {k: v for k, v in Counter(all_evt_ids).items() if v > 1}
if dups:
    fail(section, f"{len(dups)} duplicate event IDs found")
else:
    ok(section, "No duplicate event IDs")

info(section, "Events per file: " + ", ".join(f"{fn}={len(ids)}" for fn, ids in sorted(event_ids_by_file.items())))

# ============================================================
# 9. GEOGRAPHY
# ============================================================
section = "Geography"

atlas_id_counter = Counter(loc.get('id', '') for loc in atlas_data.get('locations', []))
atlas_dups = {k: v for k, v in atlas_id_counter.items() if v > 1}
if atlas_dups:
    fail(section, f"{len(atlas_dups)} duplicate atlas location IDs")
else:
    ok(section, f"All {len(atlas_ids)} atlas location IDs are unique")

atlas_sett_unknown = []
for loc in atlas_data.get('locations', []):
    ns = loc.get('nearest_settlement', '')
    if ns and ns not in settlement_names:
        matched = any(ns in sn or sn in ns for sn in settlement_names)
        if not matched:
            atlas_sett_unknown.append((loc.get('id', ''), ns))

if atlas_sett_unknown:
    warn(section, f"{len(atlas_sett_unknown)} atlas locations reference unknown nearest_settlement")
else:
    ok(section, "All atlas nearest_settlement refs match known settlements")

# ============================================================
# 10. VOLUME/EVENT REFERENCES
# ============================================================
section = "Volumes"

vol_missing = sorted(v for v in volume_event_refs if v not in all_events)
if vol_missing:
    warn(section, f"{len(vol_missing)} volume event refs not found in event files")
    for vref in vol_missing[:30]:
        info(section, f"  '{vref}' not in events")
else:
    ok(section, f"All {len(volume_event_refs)} volume event references match event files")

# ============================================================
# GENERATE REPORT
# ============================================================
total = len(passes) + len(warnings) + len(failures)

report = []
report.append("# Cross-Reference Audit Report")
report.append("")
report.append("Generated: 2026-04-13")
report.append("")
report.append("## Summary")
report.append("")
report.append(f"- **{len(passes)}/{total}** checks passed")
report.append(f"- **{len(warnings)}** warnings")
report.append(f"- **{len(failures)}** failures")
report.append("")
report.append("### Data Inventory")
report.append("")
report.append("| Category | Count |")
report.append("|---|---|")
report.append(f"| Settlements | {len(settlement_names)} |")
report.append(f"| Atlas locations | {len(atlas_ids)} |")
report.append(f"| Routes (detailed) | {len(routes)} |")
report.append(f"| Travel routes (settlement) | {len(travel_routes)} |")
report.append(f"| NPCs | {len(npc_ids)} |")
report.append(f"| Relationship web edges | {len(relweb_edges)} |")
report.append(f"| Enemy IDs (bestiary) | {len(enemy_ids)} |")
report.append(f"| Pre-built encounters | {len(encounters)} |")
report.append(f"| Barrow encounter entries | {len(barrow_encounters)} |")
report.append(f"| Barrows | {len(barrow_ids)} |")
report.append(f"| Contracts | {len(contract_ids)} |")
report.append(f"| Events | {len(all_events)} |")
report.append(f"| Volume event refs | {len(volume_event_refs)} |")
report.append("")

sections_order = [
    "Settlements", "Routes", "NPCs", "Bestiary", "Contracts",
    "Barrows", "Events", "Geography", "Volumes"
]

for sec in sections_order:
    sec_p = [p for p in passes if p.startswith(f"[{sec}]")]
    sec_w = [w for w in warnings if w.startswith(f"[{sec}]")]
    sec_f = [f for f in failures if f.startswith(f"[{sec}]")]
    sec_i = [i for i in info_lines if i.startswith(f"[{sec}]")]

    if not sec_p and not sec_w and not sec_f:
        continue

    report.append(f"## {sec}")
    report.append("")

    for p in sec_p:
        report.append(f"- PASS: {p.split('] ', 1)[1]}")
    for w in sec_w:
        report.append(f"- WARNING: {w.split('] ', 1)[1]}")
    for fi in sec_f:
        report.append(f"- FAILURE: {fi.split('] ', 1)[1]}")

    if sec_i:
        report.append("")
        for i in sec_i:
            detail = i.split('] ', 1)[1]
            report.append(f"  - {detail}")

    report.append("")

report_path = f'{base}/data/CROSS_REFERENCE_AUDIT.md'
with open(report_path, 'w') as f:
    f.write('\n'.join(report))

print(f"\nReport written to {report_path}", flush=True)
print(f"\n=== SUMMARY ===")
print(f"PASSES: {len(passes)}/{total}")
print(f"WARNINGS: {len(warnings)}")
print(f"FAILURES: {len(failures)}")
print()
for p in passes:
    print(f"  OK  {p}")
for w in warnings:
    print(f"  !!  {w}")
for fi in failures:
    print(f"  XX  {fi}")
