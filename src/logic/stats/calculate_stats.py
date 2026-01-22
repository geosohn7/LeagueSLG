


def calculate_stats(base_stat, stat_growth, level):
    lv = level - 1
    return [
        int(base_stat[i] + stat_growth[i] * lv)
        for i in range(len(base_stat))
    ]


def apply_buffs(stats, buffs):
    result = stats.copy()

    return result
