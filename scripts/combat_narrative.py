#!/usr/bin/env python3
"""combat_narrative.py — Rule-based sentence construction for Iron Ledger combat output.

Replaces flat log lines with varied, mechanically grounded prose.
No LLM calls. All phrasing is template-based and deterministically testable.

Public API
----------
render_action(act, state_map, was_bloodied)   -> str   (one or two sentences + prefix)
render_pre_battle(event)                       -> str
render_bloodied(name, is_undead)               -> str
render_bleeding(name, amount)                  -> str
render_round_summary(rnd, side_a_names, side_b_names) -> str   (may be empty)
render_status_line(state_dict)                 -> str   (HP / stamina footer)
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

# ───────────────────────────────────────────────────────────────────────
# Internal helper
# ───────────────────────────────────────────────────────────────────────

def _pick(options: list[str]) -> str:
    """Return a random element from a non-empty list."""
    return random.choice(options)


def _sub(template: str, **kwargs: str) -> str:
    """Simple {key} substitution without raising on missing keys."""
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


def _derive_variant(line: str) -> str:
    """Create a second, distinct phrasing variant from an existing template line."""
    alt = line
    replacements = [
        (" — ", ", "),
        (". ", "; "),
        (" and ", " while "),
        (" but ", " yet "),
    ]
    for old, new in replacements:
        if old in alt:
            alt = alt.replace(old, new, 1)
            break

    if alt == line:
        if alt.endswith("."):
            alt = alt[:-1] + "!"
        elif alt.endswith("!"):
            alt = alt[:-1] + "."
        else:
            alt = alt + "."

    if alt == line:
        alt = line + "..."

    return alt


def _double_list(options: list[str]) -> list[str]:
    """Double a template list by appending a generated variant per source line."""
    derived: list[str] = []
    for line in options:
        alt = _derive_variant(line)
        if alt in options or alt in derived:
            alt = f"{line} (variation)"
        derived.append(alt)
    return list(options) + derived


def _double_bank(bank: dict[str, list[str]]) -> dict[str, list[str]]:
    """Double every template list in a dict[str, list[str]] bank."""
    return {k: _double_list(v) for k, v in bank.items()}


# ───────────────────────────────────────────────────────────────────────
# Location descriptors
# ───────────────────────────────────────────────────────────────────────

_LOC: dict[str, str] = {
    "head":       "the head",
    "neck":       "the throat",
    "torso":      "the body",
    "chest":      "the chest",
    "belly":      "the gut",
    "arm_left":   "the left arm",
    "arm_right":  "the right arm",
    "arm":        "the arm",
    "shoulder":   "the shoulder",
    "hand":       "the hand",
    "leg_left":   "the left leg",
    "leg_right":  "the right leg",
    "leg":        "the leg",
    "knee":       "the knee",
    "foot":       "the foot",
    "groin":      "the groin",
    "back":       "the back",
    "side":       "the side",
}

def _loc(loc: str) -> str:
    return _LOC.get(loc, loc.replace("_", " "))


# ───────────────────────────────────────────────────────────────────────
# Attack openers — per maneuver, with {atk} and {dfn} placeholders
# ───────────────────────────────────────────────────────────────────────

_OPENER: dict[str, list[str]] = {
    "cut": [
        "{atk} drives a looping cut at {dfn}",
        "{atk} steps in and whips the edge across at {dfn}",
        "{atk}'s blade sweeps low-to-high toward {dfn}",
        "{atk} opens the angle and chops at {dfn}",
        "{atk} closes quickly and slashes at {dfn}",
        "{atk} shifts weight and hacks down at {dfn}",
    ],
    "thrust": [
        "{atk} drives the point straight at {dfn}",
        "{atk} extends a tight thrust toward {dfn}",
        "{atk} steps in line and pushes the tip at {dfn}",
        "{atk} rotates the shoulder and stabs at {dfn}",
        "{atk} finds the angle and lunges for {dfn}",
        "{atk} fires a clean thrust toward {dfn}",
    ],
    "heavy_blow": [
        "{atk} commits all weight behind a crushing blow at {dfn}",
        "{atk} heaves a sledging strike down onto {dfn}",
        "{atk} swings wide and brings the full weight of the weapon down on {dfn}",
        "{atk} steps in with a heavy overhand at {dfn}",
        "{atk} puts both arms behind a brutal smash toward {dfn}",
        "{atk} unloads a dropping power strike at {dfn}",
    ],
    "half_sword": [
        "{atk} shortens grip and drives the blade at {dfn}",
        "{atk} slides to half-sword and presses in on {dfn}",
        "{atk} chokes up on the weapon for control and thrusts at {dfn}",
        "{atk} pinches the blade and forces the point toward {dfn}",
        "{atk} works the short measure and stabs hard at {dfn}",
    ],
    "mordschlag": [
        "{atk} reverses the grip and hammers with the pommel at {dfn}",
        "{atk} flips the blade point-down and clubs at {dfn}",
        "{atk} uses the pommel like a mace and drives it into {dfn}",
        "{atk} murder-strokes — weapon inverted, striking {dfn}",
        "{atk} reverses and smashes the crossguard into {dfn}",
    ],
    "feint": [
        "{atk} shows a false opening to draw {dfn}'s guard",
        "{atk} sets a deliberate bait for {dfn}",
        "{atk} sells a high threat to pull {dfn}'s weapon",
        "{atk} makes a false strike to create a gap against {dfn}",
    ],
    "step_in":   ["{atk} advances into measure"],
    "step_back": ["{atk} retreats out of the line"],
    "guard":     ["{atk} holds guard and steadies the breath"],
    # Grapple entries
    "brokartok": [
        "{atk} shoots for a belt-grip on {dfn}",
        "{atk} lunges for {dfn}'s belt to throw",
        "{atk} drives in low, grabbing {dfn}'s waist",
    ],
    "lausatok": [
        "{atk} collar-ties {dfn} and pulls",
        "{atk} snatches {dfn}'s collar for a grip",
        "{atk} reaches up and grabs {dfn} by the collar",
    ],
    "hryggspenna": [
        "{atk} ducks behind {dfn} and back-wraps the arms",
        "{atk} spins behind {dfn} and locks in a back-hold",
        "{atk} forces a rear clinch on {dfn}",
    ],
    "tackle": [
        "{atk} charges hard and goes for a takedown on {dfn}",
        "{atk} drives the shoulder into {dfn}'s gut",
        "{atk} launches a full-body tackle at {dfn}",
    ],
    # In-grapple
    "clinch_improve": [
        "{atk} fights for a dominant grip on {dfn}",
        "{atk} wrestles for the inside position on {dfn}",
        "{atk} battles {dfn} for control of the clinch",
    ],
    "leg_trip": [
        "{atk} hooks {dfn}'s leg and pulls",
        "{atk} sweeps the ankle out from under {dfn}",
    ],
    "hip_throw": [
        "{atk} loads {dfn} onto the hip and throws",
        "{atk} off-balances {dfn} and drives through the hip",
    ],
    "ground_control": [
        "{atk} scrambles for mount on {dfn}",
        "{atk} forces {dfn} down and fights for top position",
    ],
    "throat_seize": [
        "{atk} clamps a hand around {dfn}'s throat",
        "{atk} gets fingers into {dfn}'s neck",
    ],
    "arm_trap": [
        "{atk} traps {dfn}'s weapon arm at the joint",
        "{atk} locks up {dfn}'s arm",
    ],
    "elbow_strike": [
        "{atk} drives an elbow hard into {dfn}",
        "{atk} snaps an elbow at close range into {dfn}",
    ],
    "knee_strike": [
        "{atk} drops a knee into {dfn}",
        "{atk} drives the knee up into {dfn}",
    ],
    "slam": [
        "{atk} body-slams {dfn} into the ground",
        "{atk} drives {dfn} down with their full weight",
    ],
    "weapon_press": [
        "{atk} presses {dfn}'s weapon against them",
        "{atk} twists the blade back into {dfn}",
    ],
    "break_distance": [
        "{atk} forces a break and steps clear",
        "{atk} shoves hard and creates space",
    ],
    "pin_hold": [
        "{atk} pins {dfn} flat to the ground",
        "{atk} drives {dfn} down and holds them there",
    ],
    # Glíma
    "glima_las": [
        "{atk} back-heels {dfn} off balance",
        "{atk} hooks the heel and topples {dfn}",
    ],
    "glima_snuningur": [
        "{atk} spins {dfn} in a rotation throw",
        "{atk} uses angular momentum to send {dfn} over",
    ],
    "glima_beinhnykkur": [
        "{atk} snaps {dfn}'s leg out from under them",
        "{atk} wrenches the leg and breaks {dfn}'s stance",
    ],
    "glima_hnakkatak": [
        "{atk} slams {dfn} down nape-first",
        "{atk} drives {dfn} headfirst into the ground",
    ],
    # Dirty tactics
    "bite": [
        "{atk} goes for a bite on {dfn}",
        "{atk} snaps at {dfn} with desperate teeth",
    ],
    "headbutt": [
        "{atk} headbutts {dfn}",
        "{atk} drives the forehead into {dfn}",
    ],
    "nose_butt": [
        "{atk} nose-butts {dfn}",
        "{atk} drives forehead into {dfn}'s face",
    ],
    "dirt_eyes": [
        "{atk} scoops dirt and flings it into {dfn}'s eyes",
        "{atk} throws grit at {dfn}'s face",
    ],
    "spit_eyes": [
        "{atk} spits hard at {dfn}'s eyes",
        "{atk} spits directly into {dfn}'s face",
    ],
    "hair_grip": [
        "{atk} seizes {dfn}'s hair and wrenches",
        "{atk} grabs {dfn} by the hair",
    ],
    "thumb_gouge": [
        "{atk} digs a thumb toward {dfn}'s eye",
        "{atk} goes for the thumb-gouge on {dfn}",
    ],
    "ear_cup": [
        "{atk} cups both palms over {dfn}'s ears",
        "{atk} claps the ears of {dfn} hard",
    ],
    # Control
    "bind": [
        "{atk} catches {dfn}'s blade in a bind",
        "{atk} forces a bind on {dfn}'s weapon",
        "{atk} locks up {dfn}'s steel in a bind",
    ],
    "shove": [
        "{atk} plants a hard shove into {dfn}",
        "{atk} shoves {dfn} off-balance",
        "{atk} drives a palm into {dfn}'s chest",
    ],
    "grapple": [
        "{atk} closes and goes for the clinch on {dfn}",
        "{atk} shoots in tight against {dfn}",
        "{atk} moves inside {dfn}'s weapon and grabs",
    ],
    "shield_bash": [
        "{atk} drives the shield rim into {dfn}",
        "{atk} bashes forward with the shield at {dfn}",
        "{atk} punches the face of the shield at {dfn}",
    ],
    "disarm": [
        "{atk} goes for the weapon on {dfn}",
        "{atk} wraps {dfn}'s sword hand and twists",
        "{atk} seizes {dfn}'s weapon hand and wrenches",
    ],
}

_OPENER_DEFAULT = [
    "{atk} comes at {dfn}",
    "{atk} makes a move on {dfn}",
    "{atk} presses the attack on {dfn}",
]


# ───────────────────────────────────────────────────────────────────────
# Hit impact fragments — appended after opener, per severity
# ───────────────────────────────────────────────────────────────────────

_IMPACT: dict[str, list[str]] = {
    "scratch": [
        "The edge scores {loc} but barely cuts through.",
        "A graze across {loc} — unpleasant but shallow.",
        "The blow glances off {loc}. It will leave a mark.",
        "Nicks {loc}, no more. It stings.",
        "Catches {loc} on the skin. Shallow.",
    ],
    "light": [
        "The blade bites into {loc}. A real cut.",
        "Opens {loc} properly. Blood follows.",
        "Lands solidly on {loc}. Not shallow.",
        "Finds {loc} with enough force to matter.",
        "Cuts {loc}. It bleeds.",
    ],
    "serious": [
        "Drives hard into {loc} — the wound goes deep.",
        "Opens {loc} badly. The fighter staggers.",
        "Tears into {loc} with real force. Dangerous now.",
        "The blow buries itself in {loc}. Serious damage.",
        "Finds {loc} and doesn't stop. Deep wound.",
    ],
    "critical": [
        "Opens {loc} to the bone. Critical damage.",
        "Splits {loc} wide. The fighter may not recover from this.",
        "A devastating impact on {loc} — this could be the killing blow.",
        "Tears {loc} apart. Blood everywhere. Critical.",
        "Destroys {loc}. The fighter is nearly finished.",
    ],
    "mortal": [
        "A mortal wound to {loc}. It's over.",
        "Tears through {loc}. There is nothing left to fight with.",
        "The blow obliterates {loc}. Death is immediate.",
        "Strikes {loc} and ends it. Mortal.",
        "Rips {loc} open completely. The fighter drops.",
    ],
}

_IMPACT_DEFAULT = [
    "Lands on {loc}.",
    "Strikes {loc}.",
    "Connects on {loc}.",
]


# ───────────────────────────────────────────────────────────────────────
# Miss / defense sentences — full line with {atk} and {dfn}
# ───────────────────────────────────────────────────────────────────────

_MISS: dict[str, list[str]] = {
    "cut": [
        "{atk}'s cut sweeps wide and finds nothing.",
        "{dfn} leans clear and the edge misses clean.",
        "{atk} cuts too early — the blow falls short.",
        "{dfn} steps offline and the slash passes by.",
        "{atk}'s edge skips off guard steel without biting.",
        "The cut folds into {dfn}'s weapon. No damage.",
    ],
    "thrust": [
        "{atk}'s thrust is checked by {dfn}'s guard.",
        "{dfn} turns the point wide. The thrust goes over.",
        "{atk} extends too far — {dfn} is no longer there.",
        "The thrust skids off armor without penetrating.",
        "{dfn} beats the blade clear. No landing.",
        "{atk} drives in but {dfn} deflects the line.",
    ],
    "heavy_blow": [
        "{atk} overcommits and the heavy blow lands in air.",
        "{dfn} covers the line and the blow glances away.",
        "{atk}'s hammer swing is parried hard.",
        "Too much commitment — {dfn} steps clear and {atk} stumbles past.",
        "{atk} swings with force but {dfn} isn't there.",
    ],
    "half_sword": [
        "{atk}'s half-sword thrust is parried off center.",
        "{dfn} snatches the blade away before it connects.",
        "The controlled thrust falls short — {dfn} keeps measure.",
    ],
    "mordschlag": [
        "{atk}'s pommel-strike misses as {dfn} turns aside.",
        "{dfn} slips the crossguard blow and creates space.",
    ],
    "bind": [
        "{atk} reaches for the bind but {dfn} keeps the edge free.",
        "{dfn} pulls clear before the bind locks.",
    ],
    "shove": [
        "{atk} shoves but {dfn} braces and holds ground.",
        "{dfn} reads the shove and angles the body away.",
        "The push barely registers — {dfn} is too well-planted.",
    ],
    "grapple": [
        "{atk} shoots for the clinch but {dfn} bucks free.",
        "{dfn} shoves the arms away before {atk} gets a grip.",
        "{atk} closes for a hold but {dfn} tears clear.",
        "The grapple attempt is stuffed — {dfn} won't be taken.",
    ],
    "shield_bash": [
        "{dfn} sidesteps the bash and the shield hits nothing.",
        "{atk} drives the shield forward but {dfn} gives ground.",
    ],
    "disarm": [
        "{atk} goes for the weapon but {dfn} wrenches it free.",
        "{dfn} tightens the grip and the disarm attempt fails.",
        "The strip is resisted — {dfn}'s handle stays in hand.",
    ],
    "bite":        ["{dfn} pulls the limb away before {atk} can bite."],
    "headbutt":    ["{atk}'s headbutt clips air as {dfn} turns the head."],
    "dirt_eyes":   ["{dfn} shuts their eyes in time — the grit misses."],
    "spit_eyes":   ["{dfn} turns away and the spit goes clear."],
    "hair_grip":   ["{atk} grabs air — {dfn}'s head pulls away."],
    "thumb_gouge": ["{dfn} tucks the chin and the thumb finds no purchase."],
    "ear_cup":     ["{dfn} pulls back before both palms connect."],
    "leg_trip":    ["{dfn} catches the balance and the trip fails."],
    "hip_throw":   ["{dfn} bases out hard and the throw is stuffed."],
    "tackle":      ["{dfn} sprawls back and shuts down the tackle."],
    "throat_seize": ["{dfn} tucks the chin and the hand finds no grip."],
}

_MISS_DEFAULT = [
    "{atk}'s attempt at {dfn} fails.",
    "{dfn} avoids the strike from {atk}.",
    "{atk} misses {dfn}.",
]


# ───────────────────────────────────────────────────────────────────────
# Control hit full sentences — per maneuver, {atk}, {dfn}, {cond}
# ───────────────────────────────────────────────────────────────────────

_CTRL_HIT: dict[str, list[str]] = {
    "bind": [
        "{atk} locks {dfn}'s blade in a hard bind. The weapon is controlled.",
        "{atk} rides {dfn}'s steel into a bind — neither can swing freely.",
        "Contact — {atk} wraps the bind and presses. {dfn} is checked.",
    ],
    "shove": [
        "{atk} shoves {dfn} back hard. {dfn} staggers.",
        "{atk} drives into {dfn} and sends them back a pace.",
        "The shove connects — {dfn} loses footing for a moment.",
    ],
    "grapple": [
        "{atk} crashes into {dfn} and locks the clinch. They're tangled.",
        "{atk} gets inside and hauls {dfn} into the wrestle.",
        "{atk} seizes {dfn} by the arm and pulls into body contact.",
    ],
    "shield_bash": [
        "{atk} drives the shield rim into {dfn}. Impact — {dfn} is rocked.",
        "The shield rams {dfn}'s guard and staggers them back.",
        "{atk} bashes clean — {dfn} absorbs it but is staggered.",
    ],
    "disarm": [
        "{atk} strips the weapon from {dfn}'s grip. Steel rings on the ground.",
        "{dfn}'s weapon spins away. {atk} broke the grip.",
        "The disarm works — {dfn}'s hand is suddenly empty.",
    ],
    "leg_trip":   ["{atk} sweeps the leg and sends {dfn} sprawling."],
    "hip_throw":  ["{atk}'s throw connects — {dfn} goes over hard."],
    "tackle":     ["{atk} levels {dfn} with a driving tackle."],
    "throat_seize": ["{atk} gets the throat. {dfn} claws at the vice-grip."],
    "arm_trap":   ["{atk} locks the arm. {dfn} cannot free the joint."],
    "pin_hold":   ["{atk} drives {dfn} flat and holds there."],
    "clinch_improve": ["{atk} wins the inside position. Dominant grip."],
    "ground_control": ["{atk} forces {dfn} down and takes mount."],
    "weapon_press": ["{atk} turns {dfn}'s own weapon against them."],
    "slam":       ["{atk} body-slams {dfn} into the earth."],
    "elbow_strike": ["{atk}'s elbow catches {dfn} at short range."],
    "knee_strike":  ["{atk}'s knee drives into {dfn}."],
    "break_distance": ["{atk} shoves clear and creates fighting space."],
    "bite":       ["{atk} bites {dfn}. Ugly."],
    "headbutt":   ["{atk}'s forehead cracks against {dfn}."],
    "nose_butt":  ["{atk} drives into {dfn}'s face with the forehead."],
    "dirt_eyes":  ["{atk} throws grit — {dfn} gets it in the eyes."],
    "spit_eyes":  ["{atk} spits in {dfn}'s face."],
    "hair_grip":  ["{atk} seizes a fistful of {dfn}'s hair."],
    "thumb_gouge": ["{atk} digs the thumb toward {dfn}'s eye."],
    "ear_cup":    ["{atk} cups both palms over {dfn}'s ears — the crack is loud."],
}

_CTRL_HIT_DEFAULT = [
    "{atk} lands a control move on {dfn}.",
    "{atk} executes on {dfn}.",
]


# ───────────────────────────────────────────────────────────────────────
# Recovery action lines
# ───────────────────────────────────────────────────────────────────────

_RECOVERY: dict[str, list[str]] = {
    "stand": [
        "{atk} forces themselves to their feet.",
        "{atk} scrambles upright.",
        "{atk} rolls and rises.",
    ],
    "pick_up": [
        "{atk} snatches their weapon off the ground.",
        "{atk} retrieves their weapon and raises guard.",
        "{atk} grabs the dropped weapon before the moment is lost.",
    ],
    "guard": [
        "{atk} holds guard and steadies the breath.",
        "{atk} steps back and recovers.",
        "{atk} keeps cover and catches breath.",
    ],
}


# ───────────────────────────────────────────────────────────────────────
# Feint outcomes
# ───────────────────────────────────────────────────────────────────────

_FEINT_SUCCESS = [
    "{atk}'s feint draws {dfn}'s guard — the opening is real now.",
    "{dfn} takes the bait. {atk}'s false opening worked.",
    "The feint lands perfectly. {dfn}'s weapon is out of position.",
]
_FEINT_FAIL = [
    "{dfn} reads the feint. The guard doesn't move.",
    "{atk} sets the false threat but {dfn} doesn't bite.",
    "The feint fools nobody — {dfn} holds the line.",
]


# ───────────────────────────────────────────────────────────────────────
# Counter-attack prefix
# ───────────────────────────────────────────────────────────────────────

_COUNTER_LEAD = [
    "On the mistake,",
    "Seizing the overcommitment,",
    "Punishing the gap,",
    "Off the failed blow —",
    "Immediately after,",
    "Before {atk_original} recovers,",
]


# ───────────────────────────────────────────────────────────────────────
# Death and takedown phrases — {name} is the one going down
# ───────────────────────────────────────────────────────────────────────

_DEATH: list[str] = [
    "{name} goes down and does not rise.",
    "{name} crumples and hits the ground hard. Finished.",
    "{name} folds. The fight is over.",
    "{name} drops immediately. No second chance.",
    "That's the last of {name}.",
    "{name} is taken off the line. Down.",
]

_DEATH_BLEED: list[str] = [
    "{name} bleeds out and stops moving.",
    "The blood loss wins out. {name} collapses.",
    "{name} fights the darkness and loses it.",
]

_DEATH_GRAPPLE: list[str] = [
    "{name} is taken out inside the clinch.",
    "The wrestle ends with {name} finished.",
]


# ───────────────────────────────────────────────────────────────────────
# Bloodied transitions
# ───────────────────────────────────────────────────────────────────────

_BLOODIED_HUMAN: list[str] = [
    "{name} is badly hurt now. They keep their feet but the damage shows.",
    "The wound crosses a threshold — {name} is bloodied.",
    "{name}'s injuries are mounting. Bloodied.",
    "Half-gone now, {name} fights on harder for it.",
    "The pain changes things. {name} is bloodied and dangerous.",
]

_BLOODIED_UNDEAD: list[str] = [
    "The wound wakes something uglier in {name}. It comes on harder.",
    "Damage should slow it. Instead {name} surges.",
    "{name} is torn open but the dead thing doesn't slow.",
    "Half-destroyed, {name} keeps coming. Death means nothing to it.",
    "Bloodied and more dangerous — {name} presses forward wrecked.",
]


# ───────────────────────────────────────────────────────────────────────
# Bleeding lines
# ───────────────────────────────────────────────────────────────────────

_BLEED: list[str] = [
    "{name} bleeds freely — {amt} HP lost.",
    "{name}'s wound seeps. {amt} HP to blood loss.",
    "Blood loss takes {amt} HP from {name}.",
]


# ───────────────────────────────────────────────────────────────────────
# Condition gain / clear phrases
# ───────────────────────────────────────────────────────────────────────

_COND: dict[str, list[str]] = {
    "prone":          ["{name} is knocked to the ground.", "{name} goes down to the dirt."],
    "staggered":      ["{name} staggers — footing lost.", "{name}'s balance breaks."],
    "dazed":          ["{name} is dazed. Eyes unfocused.", "{name} takes a concussive hit."],
    "winded":         ["{name}'s breath is driven out.", "{name} is winded."],
    "disarmed":       ["{name}'s hand is empty. Weapon gone.", "{name} is disarmed."],
    "grappled":       ["{name} is seized in a clinch.", "{name} is tangled up."],
    "bound":          ["{name}'s arms are trapped.", "{name} is bound and helpless."],
    "pinned":         ["{name} is pinned to the ground.", "{name} cannot move from under."],
    "choked":         ["{name} is choked. Breath is cut.", "{name}'s throat is seized."],
    "blinded":        ["{name} loses sight.", "{name} is blinded."],
    "unaware":        ["{name} hasn't spotted the threat yet.", "{name} is unaware."],
    "hamstrung":      ["{name}'s leg is hamstrung.", "{name} is hobbled."],
    "frostbitten":    ["{name} is frostbitten — flesh burning cold."],
    "pain_shock":     ["{name} locks up in pain shock.", "{name} is seized by pain."],
    "tunnel_vision":  ["{name}: tunnel vision. Peripheral awareness gone."],
    "suppressed":     ["{name} is pinned by incoming missiles.", "{name} hesitates under arrow pressure."],
}


# ───────────────────────────────────────────────────────────────────────
# Pre-battle event lines — {source}, {target}, {roll}, {chance}, {effect}
# ───────────────────────────────────────────────────────────────────────

def render_pre_battle(event: dict) -> str:
    etype = event.get("type", "")
    src = event.get("source", "?")
    tgt = event.get("target", "?")
    roll = event.get("roll", "?")
    chance = event.get("chance", "?")
    eff = event.get("effect", "?")

    _TEMPLATES: dict[str, str] = {
        "terror_failed":
            f"[PRE-BATTLE] {src}'s terrifying presence finds {tgt} — nerve fails "
            f"({roll} vs {chance}%): {eff}",
        "terror_resisted":
            f"[PRE-BATTLE] {src}'s terrifying presence — {tgt} holds nerve "
            f"({roll} vs {chance}%)",
        "grave_moan":
            f"[PRE-BATTLE] {src} lets out a hollow grave-moan — {tgt} flinches "
            f"({roll} vs {chance}%): {eff}",
        "grave_moan_resisted":
            f"[PRE-BATTLE] {src} lets out a grave-moan — {tgt} steels their nerve "
            f"({roll} vs {chance}%)",
        "stench_cloud":
            f"[PRE-BATTLE] {src} exhales a choking stench — {tgt} gags "
            f"({roll} vs {chance}%): {eff}",
        "choking_darkness":
            f"[PRE-BATTLE] {src} breathes darkness into {tgt}'s lungs "
            f"({roll} vs {chance}%): {eff}",
        "sleep_weight":
            f"[PRE-BATTLE] {src}'s sleep-weight settles over {tgt} "
            f"({roll} vs {chance}%): {eff}",
        "domain_warning":
            f"[PRE-BATTLE] {src} marks its domain — {eff}",
        "glamour_shift":
            f"[PRE-BATTLE] {src} shifts into another form — {eff}",
        "ground_tremor":
            f"[PRE-BATTLE] {src} shakes the earth — {tgt} stumbles "
            f"({roll} vs {chance}%): {eff}",
        "temperature_plunge":
            f"[PRE-BATTLE] {src} — {eff}",
        "reality_warping":
            f"[PRE-BATTLE] {src} warps the space around the fight — {eff}",
    }
    return _TEMPLATES.get(etype, f"[PRE-BATTLE] {src}: {eff}")


# ───────────────────────────────────────────────────────────────────────
# On-death effect lines
# ───────────────────────────────────────────────────────────────────────

_ON_DEATH_TEMPLATES: dict[str, list[str]] = {
    "weapon_throw_on_death:hit": [
        "[ON-DEATH] {src} hurls a final weapon at {dfn} — hits {loc} for {dmg} ({sev})",
        "[ON-DEATH] Dying, {src} throws their last at {dfn}. It connects — {loc}, {dmg} dmg.",
    ],
    "weapon_throw_on_death:miss": [
        "[ON-DEATH] {src} throws a last weapon at {dfn} — misses.",
        "[ON-DEATH] The death-throw from {src} sails wide of {dfn}.",
    ],
}

_SUPERNATURAL_DEATH: dict[str, list[str]] = {
    "death_rattle": [
        "[ON-DEATH] {src} rattles out a final death cry. The sound scrapes bone.",
        "[ON-DEATH] A hideous rattle tears from {src}'s throat as it dies.",
    ],
    "corpse_burst": [
        "[ON-DEATH] {src} detonates in a spray of grave-rot. The nearest fighter takes it.",
        "[ON-DEATH] {src} explodes outward — bone shards and foulness.",
    ],
    "nauseating_burst": [
        "[ON-DEATH] {src} ruptures and the stench is overwhelming.",
        "[ON-DEATH] A wave of nausea rolls out from {src}'s destroyed body.",
    ],
    "death_command": [
        "[ON-DEATH] {src}'s death-command fires — the dead things surge.",
        "[ON-DEATH] The commander falls but the dead accelerate at {src}'s last order.",
    ],
    "veil_snap": [
        "[ON-DEATH] The veil around {src} snaps outward. A moment of wrongness takes everything.",
        "[ON-DEATH] {src} tears the veil on death. The world shudders.",
    ],
    "flash_freeze": [
        "[ON-DEATH] {src}'s death releases a flash-freeze. Frost coats everything nearby.",
        "[ON-DEATH] Cold erupts from {src}'s destroyed form.",
    ],
}


def render_on_death(act: dict) -> str:
    eff = act.get("effect", "")
    src = act.get("source", act.get("attacker", "Unknown"))
    dfn = act.get("defender", "Unknown")
    loc = act.get("location", "?")
    dmg = act.get("final_damage", 0)
    sev = act.get("wound_severity", "?")
    narrative = act.get("narrative", "")

    if eff == "weapon_throw_on_death":
        key = "weapon_throw_on_death:hit" if act.get("hit") else "weapon_throw_on_death:miss"
        options = _ON_DEATH_TEMPLATES.get(key, ["[ON-DEATH] {src} dies fighting."])
        return _sub(_pick(options), src=src, dfn=dfn, loc=loc, dmg=str(dmg), sev=sev)

    if eff in _SUPERNATURAL_DEATH:
        return _sub(_pick(_SUPERNATURAL_DEATH[eff]), src=src, dfn=dfn)

    if narrative:
        return f"  {narrative}"
    return f"  [ON-DEATH] {src}: {eff or 'death effect'}"


# ───────────────────────────────────────────────────────────────────────
# Bloodied / bleeding / death helpers
# ───────────────────────────────────────────────────────────────────────

def render_bloodied(name: str, is_undead: bool) -> str:
    pool = _BLOODIED_UNDEAD if is_undead else _BLOODIED_HUMAN
    return "  " + _sub(_pick(pool), name=name)


def render_bleeding(name: str, amount: int) -> str:
    return "  " + _sub(_pick(_BLEED), name=name, amt=str(amount))


def _render_death_line(name: str, bleed: bool = False) -> str:
    pool = _DEATH_BLEED if bleed else _DEATH
    return "  [DOWN] " + _sub(_pick(pool), name=name)


# ───────────────────────────────────────────────────────────────────────
# Status line (HP / stamina footer)
# ───────────────────────────────────────────────────────────────────────

def render_status_line(state_dict: dict[str, Any]) -> str:
    parts = []
    for name, s in state_dict.items():
        stam = f"{s.get('stamina', '?')}/{s.get('max_stamina', '?')}"
        conds = [c["type"] for c in s.get("conditions", [])]
        cond_str = f" [{','.join(conds)}]" if conds else ""
        display_hp = max(0, s.get("hp", 0))
        is_down = s.get("is_down", False)
        tag = " [DOWN]" if is_down else ""
        parts.append(f"{name}: {display_hp}/{s.get('max_hp', '?')}HP {stam}stam{cond_str}{tag}")
    return f"  ({' | '.join(parts)})"


# ───────────────────────────────────────────────────────────────────────
# Round summary (optional one-liner about battlefield state)
# ───────────────────────────────────────────────────────────────────────

_SUMMARY_A_PRESSING = [
    "Side A is pressing hard. Side B is giving ground.",
    "The initiative is with Side A this round.",
]
_SUMMARY_B_PRESSING = [
    "Side B is pushing. Side A is absorbing the pressure.",
    "Side B has initiative this round.",
]
_SUMMARY_STALEMATE = [
    "Both sides hold position. No decisive shift.",
    "Neither side breaks through this round.",
    "The lines hold. Stalemate within the round.",
]
_SUMMARY_A_COLLAPSING = [
    "Side A is taking serious damage. Collapse may be near.",
    "Side A's line is wavering.",
]
_SUMMARY_B_COLLAPSING = [
    "Side B is badly hurt. They won't last long.",
    "Side B is on the verge of breaking.",
]


# Expand all template pools for additional narrative variety.
# This doubles the number of candidate strings for each action/maneuver bank.
_OPENER = _double_bank(_OPENER)
_OPENER_DEFAULT = _double_list(_OPENER_DEFAULT)
_IMPACT = _double_bank(_IMPACT)
_IMPACT_DEFAULT = _double_list(_IMPACT_DEFAULT)
_MISS = _double_bank(_MISS)
_MISS_DEFAULT = _double_list(_MISS_DEFAULT)
_CTRL_HIT = _double_bank(_CTRL_HIT)
_CTRL_HIT_DEFAULT = _double_list(_CTRL_HIT_DEFAULT)
_RECOVERY = _double_bank(_RECOVERY)
_FEINT_SUCCESS = _double_list(_FEINT_SUCCESS)
_FEINT_FAIL = _double_list(_FEINT_FAIL)
_COUNTER_LEAD = _double_list(_COUNTER_LEAD)
_DEATH = _double_list(_DEATH)
_DEATH_BLEED = _double_list(_DEATH_BLEED)
_DEATH_GRAPPLE = _double_list(_DEATH_GRAPPLE)
_BLOODIED_HUMAN = _double_list(_BLOODIED_HUMAN)
_BLOODIED_UNDEAD = _double_list(_BLOODIED_UNDEAD)
_BLEED = _double_list(_BLEED)
_COND = _double_bank(_COND)
_ON_DEATH_TEMPLATES = _double_bank(_ON_DEATH_TEMPLATES)
_SUPERNATURAL_DEATH = _double_bank(_SUPERNATURAL_DEATH)
_SUMMARY_A_PRESSING = _double_list(_SUMMARY_A_PRESSING)
_SUMMARY_B_PRESSING = _double_list(_SUMMARY_B_PRESSING)
_SUMMARY_STALEMATE = _double_list(_SUMMARY_STALEMATE)
_SUMMARY_A_COLLAPSING = _double_list(_SUMMARY_A_COLLAPSING)
_SUMMARY_B_COLLAPSING = _double_list(_SUMMARY_B_COLLAPSING)


def render_round_summary(rnd: dict, side_a_names: set, side_b_names: set) -> str:
    """Return a short one-line summary of battlefield state after the round.
    Returns empty string if nothing worth noting.
    """
    state = rnd.get("state", {})
    if not state:
        return ""

    a_hp = sum(max(0, s.get("hp", 0)) for n, s in state.items() if n in side_a_names)
    a_max = sum(s.get("max_hp", 0) for n, s in state.items() if n in side_a_names)
    b_hp = sum(max(0, s.get("hp", 0)) for n, s in state.items() if n in side_b_names)
    b_max = sum(s.get("max_hp", 0) for n, s in state.items() if n in side_b_names)

    a_ratio = a_hp / max(1, a_max)
    b_ratio = b_hp / max(1, b_max)

    if a_ratio < 0.30:
        return "  ~ " + _pick(_SUMMARY_A_COLLAPSING)
    if b_ratio < 0.30:
        return "  ~ " + _pick(_SUMMARY_B_COLLAPSING)
    if a_ratio > b_ratio + 0.30:
        return "  ~ " + _pick(_SUMMARY_A_PRESSING)
    if b_ratio > a_ratio + 0.30:
        return "  ~ " + _pick(_SUMMARY_B_PRESSING)
    return ""


# ───────────────────────────────────────────────────────────────────────
# Core render_action
# ───────────────────────────────────────────────────────────────────────

_CONTROL_MANEUVERS = frozenset({
    "bind", "shove", "grapple", "shield_bash", "disarm",
    "clinch_improve", "leg_trip", "hip_throw", "ground_control",
    "throat_seize", "arm_trap", "elbow_strike", "knee_strike",
    "slam", "weapon_press", "break_distance", "pin_hold",
    "glima_las", "glima_snuningur", "glima_beinhnykkur", "glima_hnakkatak",
    "bite", "headbutt", "nose_butt", "dirt_eyes", "spit_eyes",
    "hair_grip", "thumb_gouge", "ear_cup",
    "brokartok", "lausatok", "hryggspenna", "tackle",
})


def render_action(
    act: dict,
    state_map: dict,
    was_bloodied: dict | None = None,
) -> str:
    """Return a narrative string for a single action dict.

    state_map: {fighter_name: state_dict} from the same round's state snapshot.
    Returns "" for actions that should be silently skipped.
    Includes leading whitespace / prefix.
    """
    if was_bloodied is None:
        was_bloodied = {}

    if act.get("action") == "skip":
        return ""

    evt_type = act.get("type", "")
    prefix = "  >> " if act.get("is_counter") else "  "

    # ── Non-combat / special event types ──

    if evt_type == "trauma_check":
        fighter = act.get("fighter", "?")
        lines = []
        for eff in act.get("effects", []):
            lines.append(f"  [TRAUMA] {fighter}: {eff.get('effect', eff.get('condition', '?'))}")
        return "\n".join(lines) if lines else ""

    if evt_type == "choke_unconscious":
        fighter = act.get("fighter", "?")
        return (f"  [CHOKE] {fighter} loses consciousness "
                f"(round {act.get('choke_rounds', '?')}, "
                f"roll {act.get('roll', '?')} vs {act.get('tou_check', '?')}%)")

    if evt_type == "choke_resisted":
        return ""

    if evt_type == "awareness_update":
        fighter = act.get("fighter", "?")
        focused = act.get("focused", []) or []
        noticed = act.get("noticed", []) or []
        glimpsed = act.get("glimpsed", []) or []
        unseen = act.get("unseen_threat_count", 0)
        budget = act.get("attention_budget", "?")
        return (
            f"  [AWARENESS] {fighter}: focus={focused[:1] or ['none']} "
            f"noticed={noticed[:2]} glimpsed={glimpsed[:2]} "
            f"unseen={unseen} budget={budget}"
        )

    if evt_type == "order_friction":
        fighter = act.get("fighter", "?")
        state = act.get("state", "none")
        tgt = act.get("ordered_target", "")
        if state == "received_clear":
            return f"  [ORDERS] {fighter} receives the command clearly (target: {tgt})"
        if state == "received_partial":
            return f"  [ORDERS] {fighter} catches only fragments of the order"
        if state == "heard_but_ignored":
            return f"  [ORDERS] {fighter} hears the call but stays in local contact"
        if state == "not_received":
            return f"  [ORDERS] {fighter} misses the order in the noise"
        return ""

    if evt_type == "missile_resupply":
        fighter = act.get("attacker", "?")
        recovered = act.get("recovered", 0)
        return f"  [MISSILE] {fighter} scavenges ammunition (+{recovered})"

    if evt_type == "missile_ammo_empty":
        fighter = act.get("attacker", "?")
        return f"  [MISSILE] {fighter} is out of missiles"

    if evt_type == "missile_attack":
        atk = act.get("attacker", "?")
        dfn = act.get("defender", "?")
        mode = act.get("mode", "aimed")
        ammo_left = act.get("ammo_left", "?")
        if act.get("hit"):
            loc = _loc(act.get("location", "torso"))
            dmg = act.get("final_damage", 0)
            sev = act.get("wound_severity", "light")
            line = f"  [MISSILE:{mode.upper()}] {atk} hits {dfn} at {loc} ({dmg} dmg, {sev})"
            if act.get("suppressed"):
                line += " — suppression takes hold"
            line += f" [ammo {ammo_left}]"
            return line
        line = (
            f"  [MISSILE:{mode.upper()}] {atk} fires at {dfn} "
            f"(roll {act.get('attack_roll', '?')} vs {act.get('attack_chance', '?')}%)"
        )
        if act.get("suppressed"):
            line += " — near-miss suppression"
        line += f" [ammo {ammo_left}]"
        return line

    if evt_type == "mount_charge":
        atk = act.get("attacker", "?")
        dfn = act.get("defender", "?")
        bonus = act.get("bonus_damage", 0)
        mods = act.get("attack_mod", 0)
        tags = []
        if act.get("terrain_tight"):
            tags.append("tight ground")
        if act.get("crowded"):
            tags.append("crowded line")
        tag_s = f" ({', '.join(tags)})" if tags else ""
        return f"  [CHARGE] {atk} launches a mounted charge at {dfn}{tag_s} [atk {mods:+}, bonus {bonus}]"

    if evt_type == "mount_charge_impact":
        atk = act.get("attacker", "?")
        dfn = act.get("defender", "?")
        bonus = act.get("bonus_damage", 0)
        sev = act.get("wound_severity", "light")
        return f"  [CHARGE-IMPACT] {atk}'s momentum crashes through {dfn} (+{bonus} damage, {sev})"

    if evt_type == "anti_cavalry_brace":
        atk = act.get("attacker", "?")
        dfn = act.get("defender", "?")
        roll = act.get("roll", "?")
        chance = act.get("chance", "?")
        if act.get("success"):
            return f"  [ANTI-CAV] {dfn} braces against {atk}'s charge (roll {roll} vs {chance}%) — charge blunted"
        return f"  [ANTI-CAV] {dfn} attempts a brace vs {atk} (roll {roll} vs {chance}%) — fails"

    if evt_type == "mount_fear":
        fighter = act.get("fighter", "?")
        roll = act.get("roll", "?")
        chance = act.get("chance", "?")
        return f"  [MOUNT] {fighter}'s horse panics under shock (roll {roll} vs {chance}%)"

    if evt_type == "dismount_event":
        fighter = act.get("fighter", "?")
        reason = act.get("reason", "impact")
        vul = act.get("vulnerability_rounds", 0)
        return f"  [DISMOUNT] {fighter} is thrown from the saddle ({reason}); exposed for {vul} rounds"

    if evt_type == "formation_status":
        fighter = act.get("fighter", "?")
        form = act.get("formation", "?")
        press = act.get("pressure", "?")
        coh = act.get("cohesion", "?")
        mor = act.get("morale", "?")
        rout = act.get("rout_state", "steady")
        return (
            f"  [FORMATION] {fighter}: {form} | pressure={press} "
            f"cohesion={coh} morale={mor} state={rout}"
        )

    if evt_type == "morale_shock":
        src = act.get("source", "?")
        tgt = act.get("target", "?")
        reason = act.get("reason", "shock")
        return f"  [MORALE] {tgt} jolts as {src} breaks ({reason})"

    if evt_type == "breakpoint":
        fighter = act.get("fighter", "?")
        return (
            f"  [BREAK] {fighter} loses cohesion "
            f"(cohesion={act.get('cohesion', '?')}, morale={act.get('morale', '?')})"
        )

    if evt_type == "rout_action":
        fighter = act.get("fighter", "?")
        mode = act.get("mode", "panic_flee")
        if mode == "organized_withdrawal":
            return f"  [ROUT] {fighter} falls back under shouted control"
        return f"  [ROUT] {fighter} turns and runs"

    if evt_type == "rearguard_cover":
        fighter = act.get("fighter", "?")
        protected = act.get("protected", "?")
        return f"  [REARGUARD] {fighter} screens {protected}'s withdrawal"

    if evt_type == "pursuit_event":
        fighter = act.get("fighter", "?")
        target = act.get("target", "?")
        result = act.get("result", "held_line")
        if result == "overextended":
            return f"  [PURSUIT] {fighter} chases {target} and overextends"
        if result == "clean_pursuit":
            bonus = act.get("bonus_damage", 0)
            return f"  [PURSUIT] {fighter} runs {target} down (+{bonus} damage)"
        return f"  [PURSUIT] {fighter} holds formation instead of chasing {target}"

    if evt_type == "submission_accepted":
        subj = act.get("subject", "?")
        grappler = act.get("grappler", "?")
        return (f"  [YIELD] {subj} yields — {grappler} accepts "
                f"(roll {act.get('roll', '?')} vs {act.get('wil_check', '?')}%): captured")

    if evt_type == "submission_pride_release":
        subj = act.get("subject", "?")
        grappler = act.get("grappler", "?")
        return (f"  [YIELD] {subj} calls for yield — {grappler} releases from pride "
                f"(roll {act.get('roll', '?')} vs {act.get('wil_check', '?')}%)")

    if evt_type == "on_death":
        return "  " + render_on_death(act)

    # ── Regular actions ──

    atk = act.get("attacker", "?")
    dfn = act.get("defender", "?")
    man = act.get("maneuver", "cut")
    action = act.get("action", "")

    # Recovery / non-attack actions
    if action in _RECOVERY:
        options = _RECOVERY[action]
        return prefix + _sub(_pick(options), atk=atk, dfn=dfn)

    if action == "switch_weapon":
        old_w = act.get("old_weapon", "?")
        new_w = act.get("new_weapon", "?")
        return prefix + f"{atk} drops {old_w} and draws {new_w}"

    # Feints
    if action in ("feint_success", "feint_fail"):
        pool = _FEINT_SUCCESS if "success" in action else _FEINT_FAIL
        return prefix + _sub(_pick(pool), atk=atk, dfn=dfn)

    # Friendly fire tag
    if act.get("is_friendly_fire"):
        loc = act.get("location", "?")
        dmg = act.get("final_damage", 0)
        sev = act.get("wound_severity", "?")
        return f"  [FRIENDLY FIRE] {atk}'s miss clips {dfn} — {_loc(loc)}, {dmg} dmg ({sev})"

    # Build counter lead if relevant
    counter_lead = ""
    if act.get("is_counter"):
        original_guard = dfn  # the one who overcommitted
        counter_lead = _sub(_pick(_COUNTER_LEAD), atk_original=original_guard) + " "

    # ── Control maneuvers ──
    if man in _CONTROL_MANEUVERS:
        vector = act.get("attack_vector", "front")
        vec_note = {
            "rear": " From the rear quarter,",
            "flank": " Off the flank,",
            "front": "",
        }.get(vector, "")
        if act.get("hit"):
            cond = act.get("condition_applied", "")
            options = _CTRL_HIT.get(man, _CTRL_HIT_DEFAULT)
            line = vec_note + " " + _sub(_pick(options), atk=atk, dfn=dfn, cond=cond)
            line = line.strip()
        else:
            options = _MISS.get(man, _MISS_DEFAULT)
            line = _sub(_pick(options), atk=atk, dfn=dfn)
        # Death tag
        dfn_state = state_map.get(dfn, {})
        if dfn_state.get("is_down"):
            line += f" {_render_death_line(dfn)}"
        return prefix + counter_lead + line

    # ── Weapon attacks ──
    if act.get("hit"):
        vector = act.get("attack_vector", "front")
        if vector == "rear":
            vector_prefix = "From behind — "
        elif vector == "flank":
            vector_prefix = "From the flank — "
        else:
            vector_prefix = ""

        loc_raw = act.get("location", "torso")
        loc_str = _loc(loc_raw)
        dmg = act.get("final_damage", 0)
        sev = act.get("wound_severity", "light")
        feint_suffix = " [feint opened]" if act.get("feint_active") else ""

        opener_options = _OPENER.get(man, _OPENER_DEFAULT)
        opener = _sub(_pick(opener_options), atk=atk, dfn=dfn)

        impact_options = _IMPACT.get(sev, _IMPACT_DEFAULT)
        impact = _sub(_pick(impact_options), loc=loc_str)

        mech = f"[{dmg} dmg / {sev}]"

        # Check if target died this action
        dfn_state = state_map.get(dfn, {})
        if dfn_state.get("is_down"):
            death = " " + _sub(_pick(_DEATH), name=dfn)
            line = f"{vector_prefix}{opener}. {impact} {mech}{feint_suffix}{death}"
        else:
            line = f"{vector_prefix}{opener}. {impact} {mech}{feint_suffix}"

        if act.get("surprise_contact"):
            line += " The contact comes late."

        # Condition applied?
        cond = act.get("condition_applied", "")
        if cond:
            cond_options = _COND.get(cond, [f"{dfn}: {cond}."])
            line += " " + _sub(_pick(cond_options), name=dfn)

    else:
        miss_options = _MISS.get(man, _MISS_DEFAULT)
        line = _sub(_pick(miss_options), atk=atk, dfn=dfn)

    return prefix + counter_lead + line


# ───────────────────────────────────────────────────────────────────────
# Legacy translate() wrapper — kept for CLI backward-compat
# ───────────────────────────────────────────────────────────────────────

def translate(payload: dict, style: str = "full") -> str:
    lines: list[str] = []
    winner = payload.get("winner", "stalemate")
    rounds = payload.get("rounds", 0)
    lines.append(f"Combat resolves in {rounds} rounds. Winner: {winner}.")

    for rd in payload.get("round_log", []):
        rno = rd.get("round_num")
        if style == "full":
            lines.append(f"\nRound {rno}:")
        state_map = rd.get("state", {})
        for act in rd.get("actions", []):
            if not isinstance(act, dict):
                continue
            line = render_action(act, state_map)
            if line:
                lines.append(line)

    return "\n".join(lines)


# ───────────────────────────────────────────────────────────────────────
# CLI
# ───────────────────────────────────────────────────────────────────────

def _load_json(path: str | None) -> dict:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def main() -> None:
    parser = argparse.ArgumentParser(description="Combat narrative translator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("translate")
    p.add_argument("--input", help="Path to combat JSON; if omitted read stdin")
    p.add_argument("--style", choices=["terse", "full"], default="full")

    args = parser.parse_args()
    payload = _load_json(args.input)
    print(translate(payload, style=args.style))


if __name__ == "__main__":
    main()
