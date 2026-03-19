import json
import os
import numpy as np
from character import KEY_ORDER


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

                _ = parts[0]  # 忽略
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