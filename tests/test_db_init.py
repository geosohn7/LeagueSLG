from src.common.database import SessionLocal
from src.models.user import User
from src.models.user_champion import UserChampion

def main():
    db = SessionLocal()

    # 1️⃣ 유저 생성
    user = User(username="test_user")
    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"Created user: id={user.id}, username={user.username}")

    # 2️⃣ 챔피언 지급
    champ = UserChampion(
        user_id=user.id,
        champion_key="garen",
        level=1,
        exp=0
    )
    db.add(champ)
    db.commit()
    db.refresh(champ)

    print(
        f"Added champion: {champ.champion_key} "
        f"(level={champ.level}, exp={champ.exp})"
    )

    # 3️⃣ 다시 조회
    champs = (
        db.query(UserChampion)
        .filter(UserChampion.user_id == user.id)
        .all()
    )

    print("Loaded champions from DB:")
    for c in champs:
        print(f"- {c.champion_key} (lv {c.level}, exp {c.exp})")

    db.close()

if __name__ == "__main__":
    main()
