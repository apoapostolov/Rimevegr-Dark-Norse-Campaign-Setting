import sys
import os

# Add the project root and current directory to sys.path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "../../"))

from scripts.band_manager import load_band
from scripts.bestiary_loader import load_enemy
from scripts.combat_sim import run_skirmish

def run():
    # Load band
    band = load_band("data/band_state.yaml")
    
    # Build combat roster and select first 6 fighters
    side_a = band.get_combat_roster()[:6]
    
    # Load UND_DRAUGR_01 three times and rename
    side_b = []
    for suffix in ["A", "B", "C"]:
        enemy = load_enemy("UND_DRAUGR_01")
        enemy.name = f"Restless Dead {suffix}"
        side_b.append(enemy)

    # Run skirmish
    winner, rounds, logs = run_skirmish(side_a, side_b, max_rounds=30)

    # Prints: winner, rounds, side_a survivors count, side_b survivors count
    survivors_a = [f for f in side_a if f.vitality > 0]
    survivors_b = [f for f in side_b if f.vitality > 0]
    print(f"Winner: {winner}")
    print(f"Rounds: {rounds}")
    print(f"Side A survivors: {len(survivors_a)}")
    print(f"Side B survivors: {len(survivors_b)}")

    # Prints first 12 action lines from round 1-2 in compact form
    print("\nFirst 12 actions (R1-R2):")
    early_actions = [log for log in logs if log['round'] <= 2]
    for log in early_actions[:12]:
        attacker = log.get('attacker', 'Unknown')
        defender = log.get('defender', 'Unknown')
        maneuver = log.get('maneuver', 'N/A')
        hit = log.get('hit', False)
        print(f"R{log['round']}: {attacker} -> {defender} ({maneuver}, hit={hit})")

    # Retargeting check
    # We want to see if attackers target different defenders than their initial target
    # Track first target for each character
    first_targets = {}
    retarget_count = 0
    for log in logs:
        attacker = log.get('attacker')
        defender = log.get('defender')
        if not attacker or not defender: continue
        
        if attacker not in first_targets:
            first_targets[attacker] = defender
        elif defender != first_targets[attacker]:
            retarget_count += 1
            
    print(f"\nCount of actions with retargeting: {retarget_count}")

if __name__ == "__main__":
    run()
