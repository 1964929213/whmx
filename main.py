from genetic import genetic
from data_loader import load_characters
import os

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    characters_dir = os.path.join(BASE_DIR, "data", "characters")
    characters_list = load_characters(characters_dir)

    k = 1  # 比如分成 2 个队伍
    try:
        best_individual = genetic(characters_list, k=k)
        print(f"\n🏆 最优个体（6×k={len(best_individual)} 个不重复角色索引）：{best_individual}")

        # 查看每个队伍是谁
        best_team_members = [characters_list[i] for i in best_individual]
        for i in range(k):
            team = best_team_members[i*6 : (i+1)*6]
            names = [char['name'] for char in team]
            print(f"队伍 {i+1} 成员: {', '.join(names)}")
    except Exception as e:
        print(f"遗传算法运行失败: {e}")