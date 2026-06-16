"""combat_model.py — Iron Ledger dataclasses: Condition, Wound, GrappleState, Fighter, RoundResult."""
import json
from dataclasses import dataclass, field, asdict
from typing import Optional

from engine import compute_max_hp, compute_max_stamina, wound_severity
from combat_types import *

# ───────────────────────────────────────────────────────────────────────
# Dataclasses
# ───────────────────────────────────────────────────────────────────────

@dataclass
class Condition:
    type: ConditionType
    remaining_rounds: int  # -1 = until cleared by action


@dataclass
class Wound:
    location: str
    severity: str   # scratch, light, serious, critical, mortal
    damage: int
    bleeding: int = 0  # HP per round


@dataclass
class GrappleState:
    """Live state of an active grapple between two fighters."""
    position: str = "clinch"           # GrapplePosition.value
    dominant: str = ""                 # name of dominant fighter; "" = neutral
    position_round: int = 0            # rounds held at this position
    ground: bool = False               # both fighters on the ground
    # Sub-states
    throat_seized: bool = False
    throat_seized_by: str = ""
    weapon_pressed: bool = False
    weapon_pressed_by: str = ""
    arm_locked: str = ""               # name of fighter whose arm is locked
    choke_rounds: int = 0


@dataclass
class Fighter:
    """A combatant with full HEMA state."""
    name: str
    mig: int            # Might — strength, melee power
    nim: int            # Nimbleness — speed, defense
    tou: int            # Toughness — HP, stamina pool
    wit: int            # Wits — perception, feint skill
    wil: int            # Will — courage, stamina pool

    weapon_skill: int = 1
    weapon_base: int = 6
    weapon_speed: int = 3
    weapon_type: str = "generic"    # sword, hand_axe, spear, etc.
    weapon_properties: list = field(default_factory=list)  # ["silver", "iron", "fire"] — material/enchantment tags
    damage_type: str = "physical"   # "physical", "fire", "cold", "supernatural"
    shield_skill: int = 0
    shield_def: int = 0
    armor: dict = field(default_factory=lambda: {loc: 0 for loc in LOCATIONS})
    secondary_weapons: list = field(default_factory=list)  # [{"type": str, "base": int, "speed": int}, ...]

    # ── Computed / mutable state ──
    max_hp: int = 0
    hp: int = 0
    max_stamina: int = 0
    stamina: int = 0
    stance: Stance = Stance.BALANCED
    wounds: list = field(default_factory=list)
    conditions: list = field(default_factory=list)
    wound_penalty: int = 0
    is_down: bool = False
    total_bleeding: int = 0
    feinted: bool = False   # next attack ignores shield defense

    # ── Undead / creature traits ──
    resistances: list = field(default_factory=list)   # "bleeding", "cold", "fear", "poison", ...
    weaknesses: list = field(default_factory=list)    # "fire", "silver", "sunlight", "decapitation", ...
    traits: list = field(default_factory=list)        # "unfeeling", "terrifying_presence", "combat_memory", "ancient_resilience", "no_counter"
    is_undead: bool = False
    allies_in_fight: int = 0

    # ── Grapple sub-game ──
    grapple_state: Optional["GrappleState"] = None  # shared state while grappled
    ground: bool = False                             # fighter is on the ground
    brawl_skill: int = 0                             # grappling proficiency (0–3)
    # ── Intent flags ──
    glima_mode: bool = False       # fighter commits to wrestling / no lethal
    wants_nonlethal: bool = False  # prefer grapple/restraint over lethal strike
    terrain_context: str = "open"  # see TERRAIN_SPACE_CLASS for valid values (weapon-size calc)
    terrain: str = "open"          # combat environment: "barrow", "daylight_open", "blizzard", etc.
    hair: str = "short"            # "short","shoulder","long" for hair-grip
    sunlight_rounds: int = 0       # cumulative rounds exposed to direct sunlight (for sunlight weakness)
    charged_this_fight: bool = False
    territorial_rage_active: bool = False

    # ── Bloodied phase state ──
    bloodied_triggered: bool = False
    bloodied_at: float = 0.5
    bloodied_traits: list = field(default_factory=list)
    bloodied_mig_bonus: int = 0
    bloodied_nim_bonus: int = 0
    death_quarter_triggered: bool = False
    death_quarter_traits: list = field(default_factory=list)
    mig_bonus: int = 0
    nim_bonus: int = 0

    # ── Batch 7 — On-Death Dispatch ──
    death_effects: list = field(default_factory=list)

    # ── Batch 8 — Supernatural traits ──
    home_terrain: str = ""                     # anchor terrain for domain_bonus_3
    wil_penalty: int = 0                       # cumulative WIL drain (warmth_drain / dread_aura)
    wrong_geometry_used: bool = False          # wrong_geometry first-attack tracker
    shapeshifter_surprise_active: bool = False # shapeshifter pre-battle surprise flag
    frostbitten_dmg: int = 0                   # FROSTBITTEN DOT damage per round
    death_command_rounds: int = 0              # rounds of death_command attack buff remaining
    pain_fury_rounds: int = 0                  # berserker pain-fury attack window
    lure_song_entranced_rounds: int = 0        # rounds wasted (GUARD) due to lure_song

    # ── Batch 9 — Boss / Named-Enemy traits ──
    used_traits: list = field(default_factory=list)    # one-shot trait fire tracker
    mig_bonus_timer: int = 0                           # rounds remaining on blackwine_rage mig_bonus
    veteran_target: str = ""                           # target name for veteran_eye
    tactical_withdrawal_active: bool = False           # blocks opponent counter for 1 round

    # ── Batch 10 — Pre-battle expansion ──
    init_penalty: int = 0                              # initiative penalty (grave_moan)
    reality_warping_rounds: int = 0                    # rounds attackers take -10 vs this fighter
    prebattle_attack_penalty: int = 0                  # flat attack modifier from pre-battle effects
    prebattle_attack_penalty_rounds: int = 0
    prebattle_nim_penalty: int = 0                     # attribute-point penalty (−4 ~= −20%)
    prebattle_nim_penalty_rounds: int = 0
    prebattle_wit_penalty: int = 0                     # attribute-point penalty (−4 ~= −20%)
    prebattle_wit_penalty_rounds: int = 0

    # ── Wolfshead traits ──
    curse_hex_rounds: int = 0                          # rounds of -10 to all rolls (curse_hex)
    prepared_ground_triggered: bool = False            # prepared_ground pre-battle fired

    # ── Weapon reach / size / distance state ──
    weapon_reach: int = 0          # Reach tier 0–5 (auto-set from weapon_type)
    weapon_size:  int = 0          # Physical size tier 0–5 (auto-set from weapon_type)
    current_distance: int = 2      # Distance band vs current opponent (synced by fight loop)
    # ── Awareness ──
    aware: bool = True             # False → surprise round: no reactions, -50 def first round
    ambient: list = field(default_factory=list)  # AmbientCondition values as strings

    # ── Trauma / psychological conditions ──
    trauma_conditions: list = field(default_factory=list)  # [{condition, severity, wil}]

    # ── Skirmish targeting state (transient; not serialised) ──
    combat_role: str = ""           # hint: line|skirmisher|archer|caster|commander|brute|support; auto-inferred if blank
    discipline: int = -1            # 0-3; auto-inferred from stats/traits if -1
    current_target_name: str = ""   # last chosen target (stickiness across rounds)
    turns_on_target: int = 0        # consecutive rounds on current_target_name

    # ── Prompt 4: skirmish perception economy / local awareness ──
    awareness: int = 2                          # 0-5 baseline ability to track threats
    stress_load: int = 0                        # 0-100 cumulative stress load
    facing_mode: str = "rotating"              # front_guard | rotating | overextended
    attention_budget_base: int = 2              # 1-5 base track capacity
    order_reliability: float = 0.65             # 0-1 command-follow reliability
    combat_noise_tolerance: int = 2             # 0-5 tolerance to battlefield noise
    front_arc_deg: int = 140                    # broad focused awareness arc
    flank_arc_deg: int = 80                     # degraded flank awareness arc

    focused_target: str = ""                    # active tracked target this round
    noticed_targets: list = field(default_factory=list)
    glimpsed_targets: list = field(default_factory=list)
    unseen_threat_count: int = 0
    last_rear_alert_round: int = -1
    order_state: str = "none"                  # clear|partial|ignored|none
    orientation_commitment: int = 50            # 0-100, higher = harder to reorient
    recent_attackers: list = field(default_factory=list)

    # ── Prompt 5: formation warfare / morale contagion / rout state ──
    formation: str = "loose_line"               # shield_wall | loose_line | wedge | broken
    cohesion_score: int = 70                    # 0-100
    frontage_pressure: int = 0                  # 0-100
    morale_score: int = 70                      # 0-100
    rout_state: str = "steady"                 # steady | wavering | rout
    is_commander: bool = False                  # optional explicit commander marker

    # ── Prompt 8: missile combat / suppression / ammo discipline ──
    ammo_max: int = 0                           # 0 => non-missile fighter or unspecified
    ammo_current: int = 0                       # tracked live ammunition
    missile_mode: str = "auto"                 # auto | aimed | volley
    suppression_rounds: int = 0                 # rounds left under suppression pressure
    resupplies_used: int = 0                    # conservative in-fight ammo scavenging count

    # ── Prompt 9: mounted combat / charge / dismount state ──
    mounted: bool = False                        # True when fighting from horseback
    mount_condition: str = "steady"             # steady | panicked | wounded
    rider_stability: int = 70                    # 0-100 seat control under shock/impact
    mount_fatigue: int = 0                       # 0-100 cumulative horse fatigue
    mount_breed: str = ""
    mount_mood: str = "calm"
    mount_traits: list = field(default_factory=list)
    mount_tricks: list = field(default_factory=list)
    mount_stats: dict = field(default_factory=dict)
    mount_max_hp: int = 0
    mount_hp: int = 0
    mount_wounds: list = field(default_factory=list)
    dog_companions: list = field(default_factory=list)
    charge_cooldown: int = 0                     # rounds until next full charge window
    dismount_vulnerability_rounds: int = 0       # short post-dismount vulnerability timer
    mounted_pursuit_chain: int = 0               # consecutive mounted pursuit actions

    # ── Prompt 4: transient, per-action directional modifiers ──
    action_attack_mod: int = 0
    action_defense_mod: int = 0

    def __post_init__(self):
        if self.max_hp == 0:
            self.max_hp = compute_max_hp(self.tou, self.mig)
        if self.hp == 0:
            self.hp = self.max_hp
        if self.max_stamina == 0:
            self.max_stamina = compute_max_stamina(self.tou, self.wil)
        if self.stamina == 0:
            self.stamina = self.max_stamina
        if self.weapon_reach == 0:
            self.weapon_reach = get_weapon_reach(self.weapon_type)
        if self.weapon_size == 0:
            self.weapon_size = get_weapon_size(self.weapon_type)
        if self.ammo_max > 0 and self.ammo_current <= 0:
            self.ammo_current = self.ammo_max
        if self.mount_condition not in {"steady", "panicked", "wounded"}:
            self.mount_condition = "steady"
        self._update_wound_state()

    # ── Wound management (backward-compatible) ──

    def _update_wound_state(self):
        penalty = 0
        bleed = 0
        for w in self.wounds:
            if w.severity == "light":
                penalty += 5
            elif w.severity == "serious":
                penalty += 15
                bleed += 1
            elif w.severity == "critical":
                penalty += 30
                bleed += 2
            elif w.severity == "mortal":
                penalty += 50
                bleed += 3
        # Undead, unfeeling, and pain-resistant creatures ignore wound penalties
        if (self.is_undead or "unfeeling" in self.traits
                or "pain" in self.resistances
                or "pain_penalties" in self.resistances):
            self.wound_penalty = 0
        elif "starvation_frenzy" in self.traits and len(self.wounds) == 1:
            # The very first wound's penalty is ignored for starving pack predators
            self.wound_penalty = 0
        else:
            self.wound_penalty = penalty

        # Territorial rage turns on below 50% HP once and stays active
        if ("territorial_rage" in self.traits
                and not self.territorial_rage_active
                and self.hp <= self.max_hp * 0.5):
            self.territorial_rage_active = True

        # Bleeding-resistant creatures have no lifeforce to drain through blood
        if "bleeding" in self.resistances:
            self.total_bleeding = 0
        else:
            self.total_bleeding = bleed

    def _check_bloodied(self):
        """Apply one-time bloodied/death-quarter transitions based on HP thresholds."""
        if self.max_hp <= 0:
            return

        # Bloodied threshold (default 50%)
        if (not self.bloodied_triggered
                and self.hp <= self.max_hp * self.bloodied_at):
            self.bloodied_triggered = True
            for tr in self.bloodied_traits:
                if tr not in self.traits:
                    self.traits.append(tr)
            self.mig_bonus += self.bloodied_mig_bonus
            self.nim_bonus += self.bloodied_nim_bonus

        # Death-quarter threshold (25%)
        if (not self.death_quarter_triggered
                and self.hp <= self.max_hp * 0.25):
            self.death_quarter_triggered = True
            for tr in self.death_quarter_traits:
                if tr not in self.traits:
                    self.traits.append(tr)
            # last_stand_25: +3 weapon_base at death's door (once)
            if ("last_stand_25" in self.traits
                    and "last_stand_25_applied" not in self.used_traits):
                self.used_traits.append("last_stand_25_applied")
                self.weapon_base += 3

    def apply_wound(self, location: str, damage: int) -> Wound:
        sev = wound_severity(damage)
        # relentless_no_crit: downgrade first critical wound to serious (once)
        if (sev == "critical" and "relentless_no_crit" in self.traits
                and "relentless_no_crit_used" not in self.used_traits):
            sev = "serious"
            self.used_traits.append("relentless_no_crit_used")
        # Bleeding-resistant creatures don't bleed out
        bleed = 0
        if "bleeding" not in self.resistances:
            if sev == "serious":
                bleed = 1
            elif sev == "critical":
                bleed = 2
            elif sev == "mortal":
                bleed = 3
        w = Wound(location=location, severity=sev, damage=damage, bleeding=bleed)
        self.wounds.append(w)
        self.hp -= damage
        self._check_bloodied()
        # blackwine_rage: first wound → MIG +2 for 3 rounds (once; trait appears via bloodied)
        if ("blackwine_rage" in self.traits
                and "blackwine_rage_triggered" not in self.used_traits):
            self.used_traits.append("blackwine_rage_triggered")
            self.mig_bonus += 2
            self.mig_bonus_timer = 3
        self._update_wound_state()
        if self.hp <= 0 or sev == "mortal":
            self.is_down = True
        # Dazed from serious+ head wound — undead don't get dazed
        if not self.is_undead and location == "head" and sev in ("serious", "critical"):
            self.add_condition(ConditionType.DAZED, 2)
        # Staggered from critical body hit — undead don't get staggered
        if not self.is_undead and sev == "critical" and location == "torso":
            self.add_condition(ConditionType.STAGGERED, 1)
        return w

    def apply_bleeding(self) -> int:
        if self.total_bleeding > 0:
            self.hp -= self.total_bleeding
            if self.hp <= 0:
                self.is_down = True
        return self.total_bleeding

    def get_armor_at(self, location: str) -> int:
        return self.armor.get(location, 0)

    def incoming_damage_factor(self) -> float:
        """Multiplier applied to incoming damage before the wound record."""
        if "ancient_resilience" in self.traits:
            return 0.5
        return 1.0

    # ── Stamina management ──

    def spend_stamina(self, cost: int):
        """Deduct stamina, auto-apply winded if below threshold."""
        self.stamina = max(0, self.stamina - cost)
        self._check_winded()

    def recover_stamina(self, amount: int):
        """Recover stamina up to max, clear winded if above threshold."""
        self.stamina = min(self.max_stamina, self.stamina + amount)
        self._check_winded()

    def _check_winded(self):
        threshold = self.max_stamina // 3
        if self.stamina <= threshold:
            if not self.has_condition(ConditionType.WINDED):
                self.add_condition(ConditionType.WINDED, -1)
        else:
            self.remove_condition(ConditionType.WINDED)

    # ── Condition management ──

    def has_condition(self, ctype: ConditionType) -> bool:
        return any(c.type == ctype for c in self.conditions)

    def add_condition(self, ctype: ConditionType, rounds: int):
        """Add or refresh a condition. Does not stack — extends duration."""
        # fog_fighter: immune to BLINDED condition
        if ctype == ConditionType.BLINDED and "fog_fighter" in self.traits:
            return
        for c in self.conditions:
            if c.type == ctype:
                c.remaining_rounds = max(c.remaining_rounds, rounds)
                return
        self.conditions.append(Condition(type=ctype, remaining_rounds=rounds))

    def remove_condition(self, ctype: ConditionType):
        self.conditions = [c for c in self.conditions if c.type != ctype]

    def tick_conditions(self):
        """Advance condition timers at end of round."""
        remaining = []
        for c in self.conditions:
            if c.type == ConditionType.WINDED:
                remaining.append(c)  # managed by stamina, not timer
                continue
            if c.remaining_rounds == -1:
                remaining.append(c)  # permanent until cleared by action
                continue
            c.remaining_rounds -= 1
            if c.remaining_rounds > 0:
                remaining.append(c)
        self.conditions = remaining

    def condition_attack_mod(self) -> int:
        total = 0
        for c in self.conditions:
            total += CONDITION_EFFECTS.get(c.type, {}).get("attack", 0)
        return total

    def condition_defense_mod(self) -> int:
        total = 0
        for c in self.conditions:
            total += CONDITION_EFFECTS.get(c.type, {}).get("defense", 0)
        return total

    def active_conditions_str(self) -> str:
        if not self.conditions:
            return ""
        return ", ".join(c.type.value for c in self.conditions)

    # ── Maneuver availability ──

    def can_maneuver(self, maneuver: Maneuver) -> bool:
        """Check whether this fighter can execute the given maneuver."""
        # Unaware fighters cannot react or choose defensive maneuvers
        if self.has_condition(ConditionType.UNAWARE):
            return maneuver in (Maneuver.GUARD,)  # only defensive stand — no counter
        if maneuver in (Maneuver.GUARD, Maneuver.STAND, Maneuver.PICK_UP_WEAPON):
            return True
        if maneuver == Maneuver.SWITCH_WEAPON:
            # Drawing a backup clears DISARMED too, so allow even while disarmed
            return (
                bool(self.secondary_weapons)
                and not self.has_condition(ConditionType.GRAPPLED)
                and not self.has_condition(ConditionType.PINNED)
            )
        if maneuver == Maneuver.SHIELD_BASH:
            return self.shield_def > 0
        if maneuver in (Maneuver.HALF_SWORD, Maneuver.MORDSCHLAG):
            if self.weapon_type not in ("sword", "great_sword"):
                return False
        # Terrain-based maneuver restrictions
        _space = get_space_class(self.terrain_context)
        if maneuver == Maneuver.HEAVY_BLOW and _space == "very_tight":
            return False  # no overhead clearance in barrow or low-ceiling space
        if maneuver == Maneuver.STEP_BACK and _space == "very_tight":
            return False  # dead-end passage — no room to disengage backwards
        # Grapple entry — available to all fighters not already grappled; requires CLOSE range
        if maneuver in GRAPPLE_ENTRY_MANEUVERS:
            return (
                not self.has_condition(ConditionType.GRAPPLED)
                and self.current_distance <= DIST_CLOSE
            )
        # Legacy GRAPPLE control maneuver also requires CLOSE range
        if maneuver == Maneuver.GRAPPLE:
            return (
                not self.has_condition(ConditionType.GRAPPLED)
                and self.current_distance <= DIST_CLOSE
                and "grapple" in WEAPON_MANEUVERS.get(self.weapon_type, WEAPON_MANEUVERS["generic"])
            )
        # In-grapple moves — require active grapple state
        if maneuver in IN_GRAPPLE_MANEUVERS:
            return self.grapple_state is not None
        # Glíma finishers — require Brawl 3+ or specialist trait
        if maneuver in GLIMA_FINISHER_MANEUVERS:
            return (
                self.grapple_state is not None
                and (
                    self.brawl_skill >= 3
                    or "glima_brokartok" in self.traits
                    or "glima_lausatok" in self.traits
                )
            )
        # Dirty tactics — available at melee range regardless of weapon
        if maneuver in DIRTY_MANEUVERS:
            if maneuver == Maneuver.EAR_CUP:
                return self.weapon_type == "unarmed"
            if maneuver in (Maneuver.NOSE_BUTT, Maneuver.THUMB_GOUGE):
                gs = self.grapple_state
                return (
                    self.has_condition(ConditionType.GRAPPLED)
                    or (gs is not None and gs.position in (
                        GrapplePosition.DOMINANT_CLINCH.value,
                        GrapplePosition.MOUNTED.value,
                        GrapplePosition.SIDE_CONTROL.value,
                    ))
                )
            return True  # BITE, HEADBUTT, DIRT_EYES, SPIT_EYES, HAIR_GRIP always usable
        if self.has_condition(ConditionType.DISARMED):
            return maneuver in (
                Maneuver.SHOVE, Maneuver.GRAPPLE, Maneuver.GUARD,
                Maneuver.STAND, Maneuver.PICK_UP_WEAPON,
            )
        allowed = WEAPON_MANEUVERS.get(self.weapon_type, WEAPON_MANEUVERS["generic"])
        return maneuver.value in allowed

    def switch_to_best_secondary(self, prefer_size: int | None = None) -> dict | None:
        """Swap active weapon with the best available secondary.

        Args:
            prefer_size: if given, prefer secondaries with weapon_size ≤ this value.

        Returns:
            Dict with old/new weapon info on success, None if no secondary.
        """
        if not self.secondary_weapons:
            return None
        candidates = list(self.secondary_weapons)
        if prefer_size is not None:
            small = [w for w in candidates if get_weapon_size(w["type"]) <= prefer_size]
            if small:
                candidates = small
        chosen = max(candidates, key=lambda w: w["base"])
        old_weapon = {
            "type": self.weapon_type,
            "base": self.weapon_base,
            "speed": self.weapon_speed,
        }
        self.weapon_type  = chosen["type"]
        self.weapon_base  = chosen["base"]
        self.weapon_speed = chosen["speed"]
        self.weapon_reach = get_weapon_reach(chosen["type"])
        self.weapon_size  = get_weapon_size(chosen["type"])
        self.secondary_weapons = [w for w in self.secondary_weapons if w is not chosen]
        self.secondary_weapons.append(old_weapon)
        return {
            "old_type": old_weapon["type"],
            "old_base": old_weapon["base"],
            "new_type": chosen["type"],
            "new_base": chosen["base"],
            "new_speed": chosen["speed"],
        }

    # ── Combat modifiers (backward-compatible signature) ──

    def attack_chance_mods(self) -> int:
        mods = -self.wound_penalty
        mods += STANCE_MODS[self.stance]["attack"]
        mods += self.condition_attack_mod()
        mods += self.action_attack_mod
        return mods

    def defense_chance_mods(self) -> int:
        mods = -self.wound_penalty
        mods += STANCE_MODS[self.stance]["defense"]
        mods += self.condition_defense_mod()
        mods += self.action_defense_mod
        return mods

    def damage_bonus(self) -> int:
        return STANCE_MODS[self.stance]["damage"]

    # ── Serialization ──

    def to_dict(self) -> dict:
        d = {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "stamina": self.stamina,
            "max_stamina": self.max_stamina,
            "stance": self.stance.value,
            "is_down": self.is_down,
            "wounds": [asdict(w) for w in self.wounds],
            "conditions": [
                {"type": c.type.value, "remaining": c.remaining_rounds}
                for c in self.conditions
            ],
            "wound_penalty": self.wound_penalty,
            "total_bleeding": self.total_bleeding,
            "is_undead": self.is_undead,
            "resistances": self.resistances,
            "traits": self.traits,
            "brawl_skill": self.brawl_skill,
            "glima_mode": self.glima_mode,
            "wants_nonlethal": self.wants_nonlethal,
            "ground": self.ground,
            "hair": self.hair,
            "terrain_context": self.terrain_context,
            "terrain": self.terrain,
            "weapon_reach": self.weapon_reach,
            "weapon_size": self.weapon_size,
            "current_distance": self.current_distance,
            "aware": self.aware,
            "ambient": self.ambient,
            "secondary_weapons": self.secondary_weapons,
            "weapon_properties": self.weapon_properties,
            "damage_type": self.damage_type,
            "weaknesses": self.weaknesses,
            "sunlight_rounds": self.sunlight_rounds,
            "allies_in_fight": self.allies_in_fight,
            "charged_this_fight": self.charged_this_fight,
            "territorial_rage_active": self.territorial_rage_active,
            "bloodied_triggered": self.bloodied_triggered,
            "bloodied_at": self.bloodied_at,
            "bloodied_traits": self.bloodied_traits,
            "bloodied_mig_bonus": self.bloodied_mig_bonus,
            "bloodied_nim_bonus": self.bloodied_nim_bonus,
            "death_quarter_triggered": self.death_quarter_triggered,
            "death_quarter_traits": self.death_quarter_traits,
            "mig_bonus": self.mig_bonus,
            "nim_bonus": self.nim_bonus,
            "death_effects": self.death_effects,
            "home_terrain": self.home_terrain,
            "wil_penalty": self.wil_penalty,
            "wrong_geometry_used": self.wrong_geometry_used,
            "shapeshifter_surprise_active": self.shapeshifter_surprise_active,
            "frostbitten_dmg": self.frostbitten_dmg,
            "death_command_rounds": self.death_command_rounds,
            "pain_fury_rounds": self.pain_fury_rounds,
            "used_traits": list(self.used_traits),
            "mig_bonus_timer": self.mig_bonus_timer,
            "veteran_target": self.veteran_target,
            "tactical_withdrawal_active": self.tactical_withdrawal_active,
            "init_penalty": self.init_penalty,
            "reality_warping_rounds": self.reality_warping_rounds,
            "prebattle_attack_penalty": self.prebattle_attack_penalty,
            "prebattle_attack_penalty_rounds": self.prebattle_attack_penalty_rounds,
            "prebattle_nim_penalty": self.prebattle_nim_penalty,
            "prebattle_nim_penalty_rounds": self.prebattle_nim_penalty_rounds,
            "prebattle_wit_penalty": self.prebattle_wit_penalty,
            "prebattle_wit_penalty_rounds": self.prebattle_wit_penalty_rounds,
            "awareness": self.awareness,
            "stress_load": self.stress_load,
            "facing_mode": self.facing_mode,
            "attention_budget_base": self.attention_budget_base,
            "order_reliability": self.order_reliability,
            "combat_noise_tolerance": self.combat_noise_tolerance,
            "front_arc_deg": self.front_arc_deg,
            "flank_arc_deg": self.flank_arc_deg,
            "focused_target": self.focused_target,
            "noticed_targets": list(self.noticed_targets),
            "glimpsed_targets": list(self.glimpsed_targets),
            "unseen_threat_count": self.unseen_threat_count,
            "last_rear_alert_round": self.last_rear_alert_round,
            "order_state": self.order_state,
            "orientation_commitment": self.orientation_commitment,
            "recent_attackers": list(self.recent_attackers),
            "formation": self.formation,
            "cohesion_score": self.cohesion_score,
            "frontage_pressure": self.frontage_pressure,
            "morale_score": self.morale_score,
            "rout_state": self.rout_state,
            "is_commander": self.is_commander,
            "ammo_max": self.ammo_max,
            "ammo_current": self.ammo_current,
            "missile_mode": self.missile_mode,
            "suppression_rounds": self.suppression_rounds,
            "resupplies_used": self.resupplies_used,
            "mounted": self.mounted,
            "mount_condition": self.mount_condition,
            "rider_stability": self.rider_stability,
            "mount_fatigue": self.mount_fatigue,
            "mount_breed": self.mount_breed,
            "mount_mood": self.mount_mood,
            "mount_traits": list(self.mount_traits),
            "mount_tricks": list(self.mount_tricks),
            "mount_stats": dict(self.mount_stats),
            "mount_max_hp": self.mount_max_hp,
            "mount_hp": self.mount_hp,
            "mount_wounds": list(self.mount_wounds),
            "dog_companions": list(self.dog_companions),
            "charge_cooldown": self.charge_cooldown,
            "dismount_vulnerability_rounds": self.dismount_vulnerability_rounds,
            "mounted_pursuit_chain": self.mounted_pursuit_chain,
        }
        if self.grapple_state is not None:
            d["grapple_state"] = asdict(self.grapple_state)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Fighter":
        armor = d.get("armor", {loc: 0 for loc in LOCATIONS})
        return cls(
            name=d["name"],
            mig=d.get("mig", 5),
            nim=d.get("nim", 5),
            tou=d.get("tou", 5),
            wit=d.get("wit", 5),
            wil=d.get("wil", 5),
            weapon_skill=d.get("weapon_skill", 1),
            weapon_base=d.get("weapon_base", 6),
            weapon_speed=d.get("weapon_speed", 3),
            weapon_type=d.get("weapon_type", "generic"),
            shield_skill=d.get("shield_skill", 0),
            shield_def=d.get("shield_def", 0),
            armor=armor,
            max_hp=d.get("max_hp", 0),
            hp=d.get("hp", 0),
            resistances=d.get("resistances", []),
            traits=d.get("traits", []),
            is_undead=d.get("is_undead", False),
            brawl_skill=d.get("brawl_skill", 0),
            glima_mode=d.get("glima_mode", False),
            wants_nonlethal=d.get("wants_nonlethal", False),
            ground=d.get("ground", False),
            hair=d.get("hair", "short"),
            terrain_context=d.get("terrain_context", "open"),
            terrain=d.get("terrain", "open"),
            weapon_size=d.get("weapon_size", 0),
            aware=d.get("aware", True),
            ambient=d.get("ambient", []),
            secondary_weapons=d.get("secondary_weapons", []),
            weapon_properties=d.get("weapon_properties", []),
            damage_type=d.get("damage_type", "physical"),
            weaknesses=d.get("weaknesses", []),
            sunlight_rounds=d.get("sunlight_rounds", 0),
            allies_in_fight=d.get("allies_in_fight", 0),
            charged_this_fight=d.get("charged_this_fight", False),
            territorial_rage_active=d.get("territorial_rage_active", False),
            bloodied_triggered=d.get("bloodied_triggered", False),
            bloodied_at=d.get("bloodied_at", 0.5),
            bloodied_traits=d.get("bloodied_traits", []),
            bloodied_mig_bonus=d.get("bloodied_mig_bonus", 0),
            bloodied_nim_bonus=d.get("bloodied_nim_bonus", 0),
            death_quarter_triggered=d.get("death_quarter_triggered", False),
            death_quarter_traits=d.get("death_quarter_traits", []),
            mig_bonus=d.get("mig_bonus", 0),
            nim_bonus=d.get("nim_bonus", 0),
            death_effects=d.get("death_effects", []),
            home_terrain=d.get("home_terrain", ""),
            wil_penalty=d.get("wil_penalty", 0),
            wrong_geometry_used=d.get("wrong_geometry_used", False),
            shapeshifter_surprise_active=d.get("shapeshifter_surprise_active", False),
            frostbitten_dmg=d.get("frostbitten_dmg", 0),
            death_command_rounds=d.get("death_command_rounds", 0),
            pain_fury_rounds=d.get("pain_fury_rounds", 0),
            used_traits=d.get("used_traits", []),
            mig_bonus_timer=d.get("mig_bonus_timer", 0),
            veteran_target=d.get("veteran_target", ""),
            tactical_withdrawal_active=d.get("tactical_withdrawal_active", False),
            init_penalty=d.get("init_penalty", 0),
            reality_warping_rounds=d.get("reality_warping_rounds", 0),
            prebattle_attack_penalty=d.get("prebattle_attack_penalty", 0),
            prebattle_attack_penalty_rounds=d.get("prebattle_attack_penalty_rounds", 0),
            prebattle_nim_penalty=d.get("prebattle_nim_penalty", 0),
            prebattle_nim_penalty_rounds=d.get("prebattle_nim_penalty_rounds", 0),
            prebattle_wit_penalty=d.get("prebattle_wit_penalty", 0),
            prebattle_wit_penalty_rounds=d.get("prebattle_wit_penalty_rounds", 0),
            awareness=d.get("awareness", 2),
            stress_load=d.get("stress_load", 0),
            facing_mode=d.get("facing_mode", "rotating"),
            attention_budget_base=d.get("attention_budget_base", 2),
            order_reliability=d.get("order_reliability", 0.65),
            combat_noise_tolerance=d.get("combat_noise_tolerance", 2),
            front_arc_deg=d.get("front_arc_deg", 140),
            flank_arc_deg=d.get("flank_arc_deg", 80),
            focused_target=d.get("focused_target", ""),
            noticed_targets=d.get("noticed_targets", []),
            glimpsed_targets=d.get("glimpsed_targets", []),
            unseen_threat_count=d.get("unseen_threat_count", 0),
            last_rear_alert_round=d.get("last_rear_alert_round", -1),
            order_state=d.get("order_state", "none"),
            orientation_commitment=d.get("orientation_commitment", 50),
            recent_attackers=d.get("recent_attackers", []),
            formation=d.get("formation", "loose_line"),
            cohesion_score=d.get("cohesion_score", 70),
            frontage_pressure=d.get("frontage_pressure", 0),
            morale_score=d.get("morale_score", 70),
            rout_state=d.get("rout_state", "steady"),
            is_commander=d.get("is_commander", False),
            ammo_max=d.get("ammo_max", 0),
            ammo_current=d.get("ammo_current", d.get("ammo_max", 0)),
            missile_mode=d.get("missile_mode", "auto"),
            suppression_rounds=d.get("suppression_rounds", 0),
            resupplies_used=d.get("resupplies_used", 0),
            mounted=d.get("mounted", False),
            mount_condition=d.get("mount_condition", "steady"),
            rider_stability=d.get("rider_stability", 70),
            mount_fatigue=d.get("mount_fatigue", 0),
            mount_breed=d.get("mount_breed", ""),
            mount_mood=d.get("mount_mood", "calm"),
            mount_traits=d.get("mount_traits", []),
            mount_tricks=d.get("mount_tricks", []),
            mount_stats=d.get("mount_stats", {}),
            mount_max_hp=d.get("mount_max_hp", 0),
            mount_hp=d.get("mount_hp", 0),
            mount_wounds=d.get("mount_wounds", []),
            dog_companions=d.get("dog_companions", []),
            charge_cooldown=d.get("charge_cooldown", 0),
            dismount_vulnerability_rounds=d.get("dismount_vulnerability_rounds", 0),
            mounted_pursuit_chain=d.get("mounted_pursuit_chain", 0),
        )


@dataclass
class RoundResult:
    round_num: int
    initiative_order: list      # names in order
    stances: dict               # name -> stance string
    actions: list               # list of action dicts
    bleeding: dict              # name -> bleed HP this round
    state: dict                 # name -> Fighter.to_dict()


# ───────────────────────────────────────────────────────────────────────
