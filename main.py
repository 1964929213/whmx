import json
import os
import numpy as np


DEFENSE = 2351

IDX_CRITICAL_RATE = 8
IDX_CRITICAL_DAMAGE = 9
IDX_DEFENSIVE_PENETRATION = 10
IDX_IGNORE_DEFENSE = 11
IDX_ATTACK_POWER_AMPLIFICATION = 12
IDX_DAMAGE_AMPLIFICATION = 13
IDX_RECEIVED_DAMAGE_AMPLIFICATION = 14
IDX_PHYSICAL_AMPLIFICATION = 15
IDX_MAGIC_AMPLIFICATION = 16

KEY_ORDER = [
    "normal_attack", 
    "combo_attack", 
    "alert_attack", 
    "counter_attack",
    "pursuit_attack", 
    "skill_damage", 
    "extra_damage", 
    "dot_damage",

    "critical_rate", 
    "critical_damage", 
    "defensive_penetration", 
    "ignore_defense",

    "attack_power_amplification", 
    "damage_amplification", 
    "received_damage_amplification",
    "physical_amplification",
    "magic_amplification"
]


def load_a_character(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not exists: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def load_characters(directory):
    characters_list = []
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Not a directory: {directory}")

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            try:
                parts = filename.split('_')
                if len(parts) != 3:
                    print(f"Filename error: {filename}")
                    continue

                _ = parts[0]
                x_part = parts[1]
                y_part = parts[2].split('.')[0]

                filepath = os.path.join(directory, filename)
                data = load_a_character(filepath)

                char_dict = decomposition(data)

                char_dict["level"] = int(x_part)
                char_dict["advanced"] = int(y_part)

                characters_list.append(char_dict)

            except Exception as e:
                print(f"Fail to load {filename}: {e}")

    return characters_list


def decomposition(data):
    name = data["name"]
    damage_types = data.get("damage_types", {"physical": 0.0, "magic": 0.0, "true": 0.0})
    survival_types = data.get("survival_types", {"shield": 0.0, "heal": 0.0, "damage_reduction": 0.0})
    base_stats = np.array([data.get("base_stats", {}).get(k, 0.0) for k in KEY_ORDER])
    damage_contributions = np.array([data.get("damage_contributions", {}).get(k, 0.0) for k in KEY_ORDER])
    team_buffs = np.array([data.get("team_buffs", {}).get(k, 0.0) for k in KEY_ORDER])

    return {
        "name": name,
        "damage_types": damage_types,
        "survival_types": survival_types,
        "base_stats": base_stats,
        "damage_contributions": damage_contributions,
        "team_buffs": team_buffs
    }


def calculate(characters_list):
    total_damage = 0.0
    team_buff = np.sum([char["team_buffs"] for char in characters_list], axis=0)

    for char in characters_list:
        base_stats = char["base_stats"]
        damage_contributions = char["damage_contributions"]
        damage_types = char["damage_types"]
        self_buff = team_buff + base_stats

        critical_rate = min(self_buff[IDX_CRITICAL_RATE], 1.0)
        critical_damage = self_buff[IDX_CRITICAL_DAMAGE]
        defensive_penetration = self_buff[IDX_DEFENSIVE_PENETRATION]
        ignore_defense = min(self_buff[IDX_IGNORE_DEFENSE], 1.0)
        attack_power_amplification = self_buff[IDX_ATTACK_POWER_AMPLIFICATION]
        damage_amplification = self_buff[IDX_DAMAGE_AMPLIFICATION]
        received_damage_amplification = self_buff[IDX_RECEIVED_DAMAGE_AMPLIFICATION]
        physical_amplification = self_buff[IDX_PHYSICAL_AMPLIFICATION]
        magic_amplification = self_buff[IDX_MAGIC_AMPLIFICATION]

        self_damage = np.dot(self_buff[:8], damage_contributions[:8])

        self_damage *= (1 + critical_rate * critical_damage)

        defense_term = 700 + DEFENSE * (1 - ignore_defense) * defensive_penetration
        defense_base = 700 + DEFENSE * (1 - ignore_defense)
        self_damage *= defense_term / defense_base

        self_damage *= (1 + attack_power_amplification)
        self_damage *= (1 + damage_amplification)
        self_damage *= (1 + received_damage_amplification)

        self_damage *= (
            damage_types["physical"] * (1 + physical_amplification)
            + damage_types["magic"] * (1 + magic_amplification)
            + damage_types["true"]
        )

        total_damage += self_damage

    return total_damage


def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    characters_dir = os.path.join(BASE_DIR, "data", "characters")

    try:
        characters_list = load_characters(characters_dir)
        print(f"{len(characters_list)} characters loaded.\n")

        total = calculate(characters_list)
        print(f"\nTotal damage: {total:.4f}")
            
    except Exception as e:
        print(f"Calculation failed: {e}")


if __name__ == "__main__":
    main()