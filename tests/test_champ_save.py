from src.common.database import SessionLocal
from src.models.user import User
from src.models.user_champion import UserChampion
from src.logic.champion_mapper import orm_to_champion, champion_to_orm

def main():
    db = SessionLocal()

    orm = db.query(UserChampion).first()
    champ = orm_to_champion(orm)

    print("Before battle:")
    print(f"- level={champ.level}, exp={champ.exp}")

    # 가짜 전투 보상
    champ.gain_exp(250)

    print("After battle:")
    print(f"- level={champ.level}, exp={champ.exp}")

    # 다시 DB에 저장
    champion_to_orm(champ, orm)
    db.add(orm) # prevent premature flushing
    db.commit()

    # 재조회
    db.refresh(orm)
    print("Reloaded from DB:")
    print(f"- level={orm.level}, exp={orm.exp}")

    db.close()

if __name__ == "__main__":
    main()
