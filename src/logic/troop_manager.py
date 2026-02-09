from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from src.db_manager import DatabaseManager
from src.logic.building_manager import BuildingManager

class TroopManager:
    """
    병력 관리 로직 (징병, 배치)
    - 징병: 자원 소모 -> 대기열 -> 예비 병력 추가
    - 배치: 예비 병력 -> 장수에게 할당 (HP 회복)
    """
    
    def __init__(self, db_manager: DatabaseManager, building_manager: BuildingManager):
        self.db_manager = db_manager
        self.building_manager = building_manager
        
        # 간단한 메모리 기반 징병 대기열 
        # {user_id: [{"finish_time": datetime, "amount": int}]}
        self.draft_queues: Dict[int, List[dict]] = {}

    def get_max_troops(self, user_id: int) -> int:
        """최대 보유 가능 예비 병력 수 (기본 + 건물 보너스)"""
        base_cap = 1000
        buffs = self.building_manager.get_buffs(user_id)
        return int(base_cap + buffs.get("max_troops", 0))
    
    def get_user_troops(self, user_id: int) -> int:
        user_info = self.db_manager.get_user_info(user_id)
        if user_info:
            return user_info.get("reserve_troops", 0)
        return 0

    def start_draft(self, user_id: int, amount: int) -> Tuple[bool, str]:
        """징병 시작"""
        if amount <= 0:
            return False, "Amount must be positive."
            
        # 1. 최대 병력 제한 확인
        current_troops = self.get_user_troops(user_id)
        max_troops = self.get_max_troops(user_id)
        
        # 징병 중인 병력도 포함해야 정확하지만, 일단 단순화
        if current_troops + amount > max_troops:
            return False, f"Capacity exceeded. Max: {max_troops}"
            
        # 버프 가져오기
        buffs = self.building_manager.get_buffs(user_id)
        cost_discount = buffs.get("draft_cost_bonus", 0.0)
        speed_discount = buffs.get("draft_speed_bonus", 0.0)
        
        # 2. 자원 확인 (1병력 = 식1, 목1, 철1)
        # 할인 적용 (최소 0)
        unit_cost = max(0, int(1 * (1 - cost_discount)))
        if unit_cost == 0 and cost_discount < 1.0: 
             # 완전히 무료가 아니라면 최소 1? 일단 정책상 0 가능하게 둠
             pass
             
        total_cost_per_res = unit_cost * amount
        cost = {"food": total_cost_per_res, "wood": total_cost_per_res, "iron": total_cost_per_res}
        
        user_info = self.db_manager.get_user_info(user_id)
        user_res = user_info["resources"]
        
        for res, cost_amount in cost.items():
            if user_res.get(res, 0) < cost_amount:
                return False, f"Not enough {res}. Need {cost_amount}"
                
        # 3. 자원 소모
        for res, cost_amount in cost.items():
            self.db_manager.update_user_resource(user_id, res, -cost_amount)
            
        # 4. 대기열 추가 (1병력 = 1초)
        # 시간 단축 적용 (최소 1초)
        base_duration = amount # seconds
        duration = max(1, int(base_duration * (1 - speed_discount)))
        
        finish_time = datetime.now() + timedelta(seconds=duration)
        
        if user_id not in self.draft_queues:
            self.draft_queues[user_id] = []
            
        self.draft_queues[user_id].append({
            "finish_time": finish_time,
            "amount": amount
        })
        
        return True, f"Drafting {amount} troops. Finishes at {finish_time}"
        
    def check_drafts(self, user_id: int):
        """징병 완료 확인"""
        if user_id not in self.draft_queues:
            return
            
        queue = self.draft_queues[user_id]
        now = datetime.now()
        completed_indices = []
        
        for i, item in enumerate(queue):
            if now >= item["finish_time"]:
                # 징병 완료 -> 예비 병력 추가
                self.db_manager.update_user_troops(user_id, item["amount"])
                print(f"User {user_id}: Drafted {item['amount']} troops.")
                completed_indices.append(i)
        
        # 완료된 항목 제거 (뒤에서부터)
        for i in reversed(completed_indices):
            queue.pop(i)

    def assign_troops(self, user_id: int, champion_key: str, amount: int) -> Tuple[bool, str]:
        """예비 병력을 장수에게 배치 (HP 회복)"""
        if amount <= 0:
            return False, "Amount must be positive."
            
        # 1. 예비 병력 확인
        reserve = self.get_user_troops(user_id)
        if reserve < amount:
            return False, f"Not enough reserve troops. Available: {reserve}"
            
        # 2. 장수 정보 확인 (DB에서 가져와야 함)
        # 현재 DB에는 UserChampion 모델이 단순히 레벨만 저장하고 있음.
        # 실제 active army는 MapManager에 있으므로 거기를 참조해야 함.
        # 혹은 UserChampion DB에 current_hp를 저장해야 하는데, 
        # 지금 구조상으로는 MapManager를 통해 Army 객체에 접근하는게 맞음.
        
        # 임시: MapManager 주입이 안되어 있으므로, DB 상으로는 처리 불가.
        # API 레벨에서 MapManager와 연동해야 함.
        
        # 여기서는 "가능 여부"만 체크하고 실제 할당은 API/MapManager에서?
        # 아니면 TroopManager가 MapManager를 참조? -> Circular Dependency 조심
        
        # 로직 분리: TroopManager는 "예비 병력 차감"만 담당
        self.db_manager.update_user_troops(user_id, -amount)
        return True, "Troops assigned."
