from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from src.common.database import SessionLocal
from src.models.army_model import ArmyDb
from src.models.user_champion import UserChampion

class ArmyService:
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()

    def get_user_armies(self, user_id: int) -> List[Dict]:
        """
        유저의 모든 부대 구성을 조회합니다.
        Returns:
            [
                {
                    "slot_index": 0,
                    "unit_type": "cavalry",
                    "champions": [
                        {"id": 1, "key": "주몽", "level": 5},
                        ...
                    ]
                },
                ...
            ]
        """
        armies = self.db.query(ArmyDb).filter(ArmyDb.user_id == user_id).order_by(ArmyDb.slot_index).all()
        result = []
        
        for army in armies:
            # Refresh champions relation
            # self.db.refresh(army) 
            
            champs = []
            for uc in army.champions:
                champs.append({
                    "id": uc.id,
                    "key": uc.champion_key,
                    "level": uc.level,
                    "exp": uc.exp
                })
            
            result.append({
                "slot_index": army.slot_index,
                "unit_type": army.unit_type,
                "champions": champs
            })
            
        return result

    def save_army_configuration(self, user_id: int, slot_index: int, champion_ids: List[int], unit_type: str = "cavalry"):
        """
        특정 슬롯의 부대 구성을 저장합니다.
        기존에 다른 부대에 배치된 챔피언이 있다면 자동으로 그 부대에서 제외되고 이 부대로 이동합니다.
        """
        # 1. Validation
        if len(champion_ids) > 3:
            raise ValueError("한 부대에는 최대 3명의 챔피언만 배치할 수 있습니다.")
        
        if not (0 <= slot_index <= 4):
            raise ValueError("부대 슬롯은 0부터 4까지만 가능합니다.")

        # 2. Get or Create ArmyDb
        army = self.db.query(ArmyDb).filter(
            ArmyDb.user_id == user_id, 
            ArmyDb.slot_index == slot_index
        ).first()

        if not army:
            army = ArmyDb(user_id=user_id, slot_index=slot_index, unit_type=unit_type)
            self.db.add(army)
            self.db.commit()
            self.db.refresh(army)
        else:
            army.unit_type = unit_type 

        # 3. Champion Assignment Logic
        # 3-1. Verify ownership of all champions
        champions = self.db.query(UserChampion).filter(
            UserChampion.id.in_(champion_ids),
            UserChampion.user_id == user_id
        ).all()
        
        if len(champions) != len(champion_ids):
            # 요청한 ID 중 일부가 존재하지 않거나 내 소유가 아님
            found_ids = {c.id for c in champions}
            missing = set(champion_ids) - found_ids
            raise ValueError(f"유요하지 않은 챔피언 ID가 포함되어 있습니다: {missing}")

        # 3-2. Clear current champions in this army (Reset)
        # 현재 이 부대에 속해있지만, 이번 요청 목록에는 없는 챔피언들을 해제
        current_members = self.db.query(UserChampion).filter(UserChampion.army_db_id == army.id).all()
        for member in current_members:
            if member.id not in champion_ids:
                member.army_db_id = None
        
        # 3-3. Assign new champions (Force Move)
        # 이번에 포함될 챔피언들의 army_db_id를 이 부대로 설정
        # (이미 다른 부대에 있어도 덮어써짐 -> 자동 이동 효과)
        for champion in champions:
            if champion.army_db_id != army.id:
                champion.army_db_id = army.id
        
        self.db.commit()
        
        return {
            "slot_index": army.slot_index,
            "unit_type": army.unit_type,
            "champion_count": len(champions)
        }

    def close(self):
        self.db.close()
