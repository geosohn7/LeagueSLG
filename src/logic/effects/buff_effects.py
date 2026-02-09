"""
BUFF_EFFECTS: 버프 ID별 실제 능력치 변화 공식이 담긴 딕셔너리
모든 수치는 % 단위로 처리됨 (val=6.0 이면 6% 변화)
"""

BUFF_EFFECTS = {
    # 이동 속도 증가: SPD * (1 + 6/100)
    "speed": lambda stats, val: [stats[0], stats[1], stats[2], stats[3], stats[4], int(stats[5] * (1 + (val/100)))],
    # 이동 속도 감소: SPD * (1 - 6/100)
    "slow": lambda stats, val: [stats[0], stats[1], stats[2], stats[3], stats[4], int(stats[5] * (1 - (val/100)))],
    # 공격력 증가
    "attack": lambda stats, val: [stats[0], int(stats[1] * (1 + (val/100))), stats[2], stats[3], stats[4], stats[5]],
    # 방어력 증가
    "defense": lambda stats, val: [stats[0], stats[1], int(stats[2] * (1 + (val/100))), stats[3], stats[4], stats[5]],
    
    # 진영 시너지: 모든 스탯 증가 (val=0.1이면 10% 증가)
    "faction_synergy": lambda stats, val: [
        int(stats[0] * (1 + val)),  # HP
        int(stats[1] * (1 + val)),  # ATK
        int(stats[2] * (1 + val)),  # DEF
        int(stats[3] * (1 + val)),  # SPATK
        int(stats[4] * (1 + val)),  # SPDEF
        int(stats[5] * (1 + val))   # SPD
    ],
    
    # 병종 우위: 모든 스탯 증가 (val=0.2이면 20% 증가)
    "unit_advantage": lambda stats, val: [
        int(stats[0] * (1 + val)),  # HP
        int(stats[1] * (1 + val)),  # ATK
        int(stats[2] * (1 + val)),  # DEF
        int(stats[3] * (1 + val)),  # SPATK
        int(stats[4] * (1 + val)),  # SPDEF
        int(stats[5] * (1 + val))   # SPD
    ],
    
    # 병종 열위: 모든 스탯 감소 (val=0.2이면 20% 감소)
    "unit_disadvantage": lambda stats, val: [
        int(stats[0] * (1 - val)),  # HP
        int(stats[1] * (1 - val)),  # ATK
        int(stats[2] * (1 - val)),  # DEF
        int(stats[3] * (1 - val)),  # SPATK
        int(stats[4] * (1 - val)),  # SPDEF
        int(stats[5] * (1 - val))   # SPD
    ],
    
    # 상태이상은 스탯 수치에는 직접 영향을 주지 않으므로 stats를 그대로 보존
    "stun": lambda stats, val: stats,
    "silence": lambda stats, val: stats,
}

def apply_buff_to_stats(buff_id, stats, value):
    """
    ID에 맞는 계산 공식을 찾아 능력치 리스트를 변환
    """
    effect = BUFF_EFFECTS.get(buff_id)
    if effect:
        # value가 None인 경우를 대비해 0으로 초기화
        return effect(stats, value or 0)
    return stats
