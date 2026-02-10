from typing import Tuple
from sqlalchemy.orm import Session
from src.common.database import SessionLocal
from src.models.user import User
from src.models.user_champion import UserChampion
from src.factories.champion_factory import create_champion

class TroopService:
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()

    def assign_troops(self, user_id: int, champion_id: int, amount: int) -> Tuple[bool, str, int]:
        """
        예비 병력을 챔피언에게 배치 (HP 회복)
        Args:
            user_id: 유저 ID
            champion_id: UserChampion ID (챔피언 Key가 아님)
            amount: 배치할 병력 수
            
        Returns:
            (Success, Message, New HP)
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "User not found", 0
            
        champion = self.db.query(UserChampion).filter(UserChampion.id == champion_id, UserChampion.user_id == user_id).first()
        if not champion:
            return False, "Champion not found or not owned by user", 0

        # Calculate Max HP
        # DB에는 스탯이 없으므로, Factory를 통해 기본 스탯을 가져와서 계산해야 함
        champ_obj = create_champion(champion.champion_key)
        champ_obj.level = champion.level
        champ_obj.exp = champion.exp
        champ_obj.recalculate_stats()
        max_hp = champ_obj.max_hp
        
        current_hp = champion.current_hp if champion.current_hp is not None else max_hp # Default to max if None? No, default from model is 100, logic should fix.
        # But wait, model default is 100 which is weird.
        # We should treat 'None' or uninitialized as 0 or current value if reliable.
        # Let's assume current_hp is reliable.
        
        needed = max_hp - current_hp
        if needed <= 0:
            return False, "Champion is already at full HP", current_hp
            
        assign_amount = min(amount, needed)
        
        if user.reserve_troops < assign_amount:
            return False, f"Not enough reserve troops. Have {user.reserve_troops}, Need {assign_amount}", current_hp
            
        # Update DB
        user.reserve_troops -= assign_amount
        champion.current_hp += assign_amount
        
        self.db.commit()
        
        return True, f"Assigned {assign_amount} troops.", champion.current_hp

    def update_champion_hp(self, champion_db_id: int, hp: int):
        """전투 후 챔피언의 HP를 업데이트"""
        champion = self.db.query(UserChampion).filter(UserChampion.id == champion_db_id).first()
        if champion:
            champion.current_hp = hp
            self.db.commit()

    def heal_all_champions(self, user_id: int) -> dict:
        """
        가용한 예비 병력으로 모든 챔피언을 최대한 치료합니다.
        Returns:
            {
                "healed_count": int,
                "total_consumed": int,
                "remaining_reserve": int,
                "details": list[str]
            }
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
             return {"error": "User not found"}
             
        champions = self.db.query(UserChampion).filter(UserChampion.user_id == user_id).all()
        
        total_consumed = 0
        healed_count = 0
        details = []
        
        for champion in champions:
            if user.reserve_troops <= 0:
                break
                
            # Create temp object to calc max stats
            champ_obj = create_champion(champion.champion_key)
            champ_obj.level = champion.level
            champ_obj.exp = champion.exp
            champ_obj.recalculate_stats()
            max_hp = champ_obj.max_hp
            
            current_hp = champion.current_hp if champion.current_hp is not None else 0
            needed = max_hp - current_hp
            
            if needed <= 0:
                continue
                
            assign_amount = min(user.reserve_troops, needed)
            
            # Apply
            user.reserve_troops -= assign_amount
            champion.current_hp = current_hp + assign_amount
            
            total_consumed += assign_amount
            healed_count += 1
            details.append(f"{champion.champion_key}: +{assign_amount}")
            
        self.db.commit()
        
        return {
            "healed_count": healed_count,
            "total_consumed": total_consumed,
            "remaining_reserve": user.reserve_troops,
            "details": details
        }

    def close(self):
        self.db.close()
