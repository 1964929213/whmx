import numpy as np
from character import DEFENSE, IDX_CRITICAL_RATE, IDX_CRITICAL_DAMAGE, IDX_DEFENSIVE_PENETRATION, IDX_IGNORE_DEFENSE, IDX_ATTACK_POWER_AMPLIFICATION, IDX_DAMAGE_AMPLIFICATION, IDX_RECEIVED_DAMAGE_AMPLIFICATION, IDX_PHYSICAL_AMPLIFICATION, IDX_MAGIC_AMPLIFICATION, KEY_ORDER


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