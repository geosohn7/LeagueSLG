from src.models.champion import Champion
from src.models.user_champion import UserChampion

# 임시 기본 스탯 (나중에 데이터화)
DEFAULT_BASE_STAT = [100, 10, 5, 0, 0, 3]
DEFAULT_STAT_GROWTH = [10, 2, 1, 0, 0, 1]

def orm_to_champion(orm: UserChampion) -> Champion:
    champ = Champion(
        name=orm.champion_key,
        base_stat=DEFAULT_BASE_STAT,
        stat_growth=DEFAULT_STAT_GROWTH,
        level=orm.level,
        exp=orm.exp,
    )
    return champ

