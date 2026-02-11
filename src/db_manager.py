from typing import List, Dict, Any
from datetime import datetime
from src.common.database import SessionLocal
from src.models.user import User
from src.models.user_champion import UserChampion
from src.models.user_champion import UserChampion
from src.models.battle_log import BattleLog
from src.models.user_internal_building import UserInternalBuilding
import json


class DatabaseManager:
    """
    기존 DatabaseManager 인터페이스를 유지하는
    SQLAlchemy 기반 어댑터
    """

    # -------------------------
    # Building & Troops
    # -------------------------
    def get_user_internal_buildings(self, user_id: int) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            buildings = db.query(UserInternalBuilding).filter(UserInternalBuilding.user_id == user_id).all()
            return [
                {
                    "type": b.building_type,
                    "level": b.level,
                    "status": b.status,
                    "finish_time": b.finish_time.isoformat() if b.finish_time else None
                }
                for b in buildings
            ]
        finally:
            db.close()

    def get_or_create_internal_building(self, user_id: int, building_type: str) -> UserInternalBuilding:
        db = SessionLocal()
        try:
            building = db.query(UserInternalBuilding).filter(
                UserInternalBuilding.user_id == user_id,
                UserInternalBuilding.building_type == building_type
            ).first()
            
            if not building:
                building = UserInternalBuilding(user_id=user_id, building_type=building_type, level=0)
                db.add(building)
                db.commit()
                db.refresh(building)
            return building
        finally:
            db.close()

    def update_building_status(self, user_id: int, building_type: str, level: int, status: str, finish_time=None):
        db = SessionLocal()
        try:
            building = db.query(UserInternalBuilding).filter(
                UserInternalBuilding.user_id == user_id,
                UserInternalBuilding.building_type == building_type
            ).first()
            
            if building:
                building.level = level
                building.status = status
                building.finish_time = finish_time
                db.commit()
        finally:
            db.close()

    def update_user_troops(self, user_id: int, amount: int) -> int:
        """예비 병력 증감. 최종 병력 수 반환"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user: return 0
            
            user.reserve_troops = max(0, user.reserve_troops + amount)
            db.commit()
            return user.reserve_troops
        finally:
            db.close()


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
                "resources": {
                    "gold": user.gold,     # Premium
                    "silver": user.silver, # Common
                    "food": user.food,
                    "wood": user.wood,
                    "iron": user.iron,
                    "stone": user.stone,
                },
                "reserve_troops": user.reserve_troops
            }
        finally:
            db.close()

    def update_user_silver_generation(self, user_id: int, hourly_rate: int):
        """시간 경과에 따른 은(Silver) 지급 (기존 Gold 대체)"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user: return
            
            now = datetime.now()
            
            # 첫 수집(혹은 초기화)인 경우
            if not user.last_silver_collected:
                user.last_silver_collected = now
                db.commit()
                return

            # 경과 시간 계산
            elapsed = (now - user.last_silver_collected).total_seconds()
            hours = elapsed / 3600.0
            
            # 최소 1분(60초) 이상 지났을 때만 처리 (DB 부하 방지)
            if elapsed < 60:
                return

            # 은 계산
            earned_silver = int(hours * hourly_rate)
            
            if earned_silver > 0:
                user.silver += earned_silver
                user.last_silver_collected = now
                db.commit()
        finally:
            db.close()

    def update_user_resource(self, user_id: int, resource_type: str, amount: int) -> bool:
        """유저의 특정 자원을 증감합니다. amount가 음수면 감소."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            valid_resources = ["gold", "silver", "food", "wood", "iron", "stone"]
            if resource_type not in valid_resources:
                return False
            
            current = getattr(user, resource_type, 0)
            new_value = max(0, current + amount)  # 음수 방지
            setattr(user, resource_type, new_value)
            db.commit()
            return True
        finally:
            db.close()

    def set_user_resources(self, user_id: int, resources: Dict[str, int]) -> bool:
        """유저의 자원을 일괄 설정합니다."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            for key, value in resources.items():
                if hasattr(user, key):
                    setattr(user, key, max(0, value))
            db.commit()
            return True
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
                    "army_db_id": c.army_db_id,
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