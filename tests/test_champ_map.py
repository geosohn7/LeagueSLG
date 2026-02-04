from src.common.database import SessionLocal
from src.models.user_champion import UserChampion
from src.logic.champion_mapper import orm_to_champion



def main():
    db = SessionLocal()

    orm_champ = db.query(UserChampion).first()
    champ = orm_to_champion(orm_champ)

    print("Champion loaded from DB:")
    print(f"- name: {champ.name}")
    print(f"- level: {champ.level}")
    print(f"- exp: {champ.exp}")

    db.close()

if __name__ == "__main__":
    main()
