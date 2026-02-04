from typing import List, Dict, Any
from src.common.database import SessionLocal
from src.models.user import User
from src.models.user_champion import UserChampion
from src.models.battle_log import BattleLog
import json


class DatabaseManager:
    """
    기존 DatabaseManager 인터페이스를 유지하는
    SQLAlchemy 기반 어댑터
    """

    # -------------------------
    # User
    # -------------------------
    def get_or_create_user(self, username: str) -> int:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user:
                return user.id

            user = User(username=username)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user.id
        finally:
            db.close()

    def get_user_info(self, user_id: int) -> Dict[str, Any] | None:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            return {
                "id": user.id,
                "username": user.username,
                "gold": getattr(user, "gold", 1000),
            }
        finally:
            db.close()

    # -------------------------
    # Champion
    # -------------------------
    def add_champion_to_user(self, user_id: int, champion_key: str):
        db = SessionLocal()
        try:
            champ = UserChampion(
                user_id=user_id,
                champion_key=champion_key,
                level=1,
                exp=0,
            )
            db.add(champ)
            db.commit()
        finally:
            db.close()

    def get_user_champions(self, user_id: int) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            champs = (
                db.query(UserChampion)
                .filter(UserChampion.user_id == user_id)
                .all()
            )

            return [
                {
                    "id": c.id,
                    "user_id": c.user_id,
                    "champion_key": c.champion_key,
                    "level": c.level,
                    "exp": c.exp,
                }
                for c in champs
            ]
        finally:
            db.close()

    def update_champion_data(self, champion_id: int, level: int, exp: int):
        db = SessionLocal()
        try:
            champ = db.query(UserChampion).filter(
                UserChampion.id == champion_id
            ).first()

            if not champ:
                return

            champ.level = level
            champ.exp = exp
            db.commit()
        finally:
            db.close()


    def update_champion_data_by_key(
        self,
        user_id: int,
        champion_key: str,
        level: int,
        exp: int,
    ):
        db = SessionLocal()
        try:
            champ = (
                db.query(UserChampion)
                .filter(
                    UserChampion.user_id == user_id,
                    UserChampion.champion_key == champion_key,
                )
                .first()
            )
            if not champ:
                return

            champ.level = level
            champ.exp = exp
            db.commit()
        finally:
            db.close()

    def save_battle_log(
        self,
        user_id: int,
        battle,
    ):
        """
        battle: Battle 인스턴스
        """
        db = SessionLocal()
        try:
            log = BattleLog(
                user_id=user_id,
                left_champion=battle.left.name,
                right_champion=battle.right.name,
                winner=battle.winner.name,
                turn_count=battle.turn,
                history_json=json.dumps(
                    battle.history,
                    ensure_ascii=False
                ),
            )
            db.add(log)
            db.commit()
        finally:
            db.close()