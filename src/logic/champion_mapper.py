from src.models.champion import Champion
from src.models.user_champion import UserChampion
from data.champion_loader import load_champions
from src.models.user_champion import UserChampion

def orm_dict_to_champion(row: dict):
    """
    DatabaseManager(dict) → Champion
    """
    orm = UserChampion(
        id=row["id"],
        user_id=row["user_id"],
        champion_key=row["champion_key"],
        level=row["level"],
        exp=row["exp"],
    )
    return orm_to_champion(orm)

def orm_to_champion(orm: UserChampion) -> Champion:
    champions = load_champions()

    # DB에 저장된 champion_key 사용
    key = orm.champion_key
    


    data = champions.get(key)

    if not data:
        # Fallback to default hero if key is still unknown
        print(f"[Mapper] Unknown key '{key}', falling back to '주몽'")
        data = champions.get("주몽")
        if not data:
             raise ValueError(f"CRITICAL: Default hero '주몽' not found in champions.json")

    champ = Champion(
        name=data["name"],
        base_stat=data["base_stat"],
        stat_growth=data["stat_growth"],
        level=orm.level,
        exp=orm.exp,
        minions=tuple(data.get("minions", ("", 0))),
        image=data.get("images", {}),
    )

    return champ


def champion_to_orm(champ: Champion, orm: UserChampion):
    orm.level = champ.level
    orm.exp = champ.exp
