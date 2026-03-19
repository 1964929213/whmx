# genetic.py

import random
import copy
from typing import List, Dict, Any

# 从 calculator 模块导入 calculate 函数
from calculator import calculate  # 请确保该函数已定义，并可正常导入


def genetic(characters_list: List[Dict[str, Any]], k: int, pop_size=100, ngen=100, cxpb=0.8, mutpb=0.2) -> List[int]:
    num_characters = len(characters_list)
    num_per_team = 6
    num_total = num_per_team * k  # 每个个体是 6*k 个不重复的索引

    if num_characters < num_total:
        raise ValueError(f"角色数量不足！需要至少 {num_total} 个角色，当前只有 {num_characters} 个。")

    # =========================
    # 1. 辅助函数：创建单个个体（6*k 个不重复索引）
    # =========================

    def create_individual():
        return random.sample(range(num_characters), num_total)

    # =========================
    # 2. 适应度函数
    # =========================

    def evaluate(individual):
        # 按顺序拆成 k 个队伍，每队 6 人
        teams = [individual[i * num_per_team:(i + 1) * num_per_team] for i in range(k)]
        scores = []
        for team_indices in teams:
            team = [characters_list[idx] for idx in team_indices]
            try:
                score = calculate(team)
                scores.append(score)
            except Exception as e:
                print(f"[适应度计算错误] 队伍伤害计算失败: {e}")
                scores.append(-float('inf'))
        if not scores:
            return -float('inf')
        return min(scores)  # 我们要最大化这个最小值

    # =========================
    # 3. 选择：锦标赛选择
    # =========================

    def select(population, fitnesses, tournsize=3):
        selected = []
        for _ in range(len(population)):
            candidates = random.sample(list(zip(population, fitnesses)), tournsize)
            winner = max(candidates, key=lambda x: x[1])[0]
            selected.append(winner)
        return selected

    # =========================
    # 4. 交叉：顺序交叉（Order Crossover, OX）—— 保证子代不重复
    # =========================

    def crossover(parent1, parent2):
        size = len(parent1)
        a, b = sorted(random.sample(range(size), 2))

        # 创建子代，初始化为 None
        child1 = [None] * size
        child2 = [None] * size

        # 复制中间段
        child1[a:b] = parent1[a:b]
        child2[a:b] = parent2[a:b]

        # 填充 child1 的剩余部分（从 parent2 中取，跳过已在 child1 中的元素）
        def fill_child(child, parent_source, parent_target_segment):
            ptr = b  # 从 b 位置开始循环
            for i in range(size):
                pos = (b + i) % size
                if child[pos] is None:
                    gene = parent_source[ptr % size]
                    while gene in child:
                        ptr += 1
                        gene = parent_source[ptr % size]
                    child[pos] = gene
            return child

        child1 = fill_child(child1, parent2, parent1[a:b])
        child2 = fill_child(child2, parent1, parent2[a:b])

        return child1, child2

    # =========================
    # 5. 变异：随机交换两个位置的元素（保证不重复）
    # =========================

    def mutate(individual, indpb=0.2):
        if random.random() < indpb:
            idx1, idx2 = random.sample(range(len(individual)), 2)
            individual[idx1], individual[idx2] = individual[idx2], individual[idx1]
        return individual

    # =========================
    # 6. 主遗传算法流程
    # =========================

    population = [create_individual() for _ in range(pop_size)]

    for gen in range(ngen):
        # 评估适应度
        fitnesses = [evaluate(ind) for ind in population]

        # 找当前最优
        best_idx = fitnesses.index(max(fitnesses))
        best_fitness = fitnesses[best_idx]
        best_ind = population[best_idx]

        print(f"🧬 第 {gen + 1}/{ngen} 代 | 当前最优适应度（最小队伍伤害）: {best_fitness:.4f}")

        # 选择
        selected = select(population, fitnesses)

        # 生成下一代
        next_population = []
        for i in range(0, pop_size, 2):
            p1 = selected[i]
            p2 = selected[(i + 1) % pop_size]

            if random.random() < cxpb:
                c1, c2 = crossover(p1, p2)
            else:
                c1, c2 = p1[:], p2[:]

            c1 = mutate(c1, mutpb)
            c2 = mutate(c2, mutpb)

            next_population.append(c1)
            if len(next_population) < pop_size:
                next_population.append(c2)

        population = next_population

    # =========================
    # 7. 返回最终最优个体
    # =========================

    final_fitnesses = [evaluate(ind) for ind in population]
    best_idx = final_fitnesses.index(max(final_fitnesses))
    best_individual = population[best_idx]

    return best_individual