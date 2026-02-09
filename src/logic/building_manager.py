from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from src.db_manager import DatabaseManager

class BuildingManager:
    """
    내정 건물(Internal Buildings) 관리 로직
    - 건설/업그레이드 비용 및 시간 관리
    - 건물 효과(버프) 제공
    """
    
    # 건물 타입 상수
    BARRACKS = "Barracks"     # 징병소 (병력 최대치 증가 + 징병 효율 증가)
    FARM = "Farm"             # 농장 (식량 생산 증가)
    MINE = "Mine"             # 광산 (철광/석재 생산 증가)
    WALL = "Wall"             # 성벽 (수비군 방어력 증가)
    HOUSE = "House"           # 민가 (골드 생산)
    TRADING_POST = "Trading Post" # 무역소 (무역 기능 해금)
    SMITHY = "Smithy"         # 대장간 (챔피언 공격력 증가)
    HOSPITAL = "Hospital"     # 병원 (패배 시 병력 손실 감소)

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_upgrade_cost(self, building_type: str, current_level: int) -> Dict[str, int]:
        """레벨별 업그레이드 비용 계산 (간소화된 공식)"""
        next_level = current_level + 1
        base_cost = 100 * next_level 
        
        if building_type == self.BARRACKS:
            # 징병소: 목재 100, 철광 50 (기본) -> 레벨 비례
            return {"wood": 100 * next_level, "iron": 50 * next_level}
        elif building_type == self.FARM:
            return {"wood": int(base_cost * 0.8), "iron": int(base_cost * 0.5), "stone": int(base_cost * 0.5)}
        elif building_type == self.MINE:
            return {"wood": base_cost, "iron": base_cost, "stone": base_cost}
        elif building_type == self.WALL:
            return {"wood": base_cost * 2, "iron": base_cost, "stone": base_cost * 3}
        elif building_type == self.HOUSE:
            # 민가: 목재 50, 석재 50 (기본)
            return {"wood": 50 * next_level, "stone": 50 * next_level}
        elif building_type == self.TRADING_POST:
            # 무역소: 목재 500, 석재 500 (기본 - 비쌈)
            return {"wood": 500 * next_level, "stone": 500 * next_level}
        elif building_type == self.SMITHY:
            # 대장간: 철광 중심
            return {"wood": 80 * next_level, "iron": 150 * next_level}
        elif building_type == self.HOSPITAL:
            # 병원: 목재, 석재 중심
            return {"wood": 100 * next_level, "stone": 100 * next_level, "food": 50 * next_level}
        
        return {}

    def get_upgrade_time(self, current_level: int) -> int:
        """업그레이드 소요 시간 (초 단위)"""
        # 테스트를 위해 짧게 설정 (레벨 * 10초)
        return (current_level + 1) * 10

    def get_instant_finish_cost(self, remaining_seconds: int) -> int:
        """즉시 완료에 필요한 골드 계산 (10초당 10골드)"""
        return max(10, (remaining_seconds // 10) * 10)

    def instant_finish(self, user_id: int, building_type: str) -> Tuple[bool, str]:
        """건설 중인 건물을 골드로 즉시 완료"""
        building = self.db_manager.get_or_create_internal_building(user_id, building_type)
        
        if building.status != "UPGRADING":
            return False, "Building is not upgrading."
        
        if not building.finish_time:
            return False, "No finish time set."
        
        # 남은 시간 계산
        now = datetime.now()
        remaining = (building.finish_time - now).total_seconds()
        
        if remaining <= 0:
            # 이미 완료됨 -> check_upgrades가 처리할 것
            return False, "Upgrade already complete."
        
        # 골드 비용 계산
        gold_cost = self.get_instant_finish_cost(int(remaining))
        
        # 골드 확인
        user_info = self.db_manager.get_user_info(user_id)
        if not user_info:
            return False, "User not found."
        
        if user_info["resources"].get("gold", 0) < gold_cost:
            return False, f"Not enough gold. Need {gold_cost}."
        
        # 골드 차감 및 즉시 완료
        self.db_manager.update_user_resource(user_id, "gold", -gold_cost)
        new_level = building.level + 1
        self.db_manager.update_building_status(user_id, building_type, new_level, "IDLE", None)
        
        return True, f"Instant finish! {building_type} is now Lv.{new_level}. Cost: {gold_cost} gold."

    def start_upgrade(self, user_id: int, building_type: str) -> Tuple[bool, str]:
        """건물 업그레이드 시작"""
        # 1. 건물 정보 조회
        building = self.db_manager.get_or_create_internal_building(user_id, building_type)
        
        if building.status == "UPGRADING":
            return False, "Building is already upgrading."

        # 2. 비용 확인
        cost = self.get_upgrade_cost(building_type, building.level)
        user_info = self.db_manager.get_user_info(user_id)
        if not user_info:
            return False, "User not found."
            
        user_res = user_info["resources"]
        
        # 자원 부족 체크
        for res, amount in cost.items():
            if user_res.get(res, 0) < amount:
                return False, f"Not enough {res}."

        # 3. 자원 차감
        for res, amount in cost.items():
            self.db_manager.update_user_resource(user_id, res, -amount)

        # 4. 업그레이드 상태 설정
        duration = self.get_upgrade_time(building.level)
        finish_time = datetime.now() + timedelta(seconds=duration)
        
        self.db_manager.update_building_status(
            user_id, building_type, building.level, "UPGRADING", finish_time
        )
        
        return True, f"Upgrade started. Finishes at {finish_time}"

    def check_upgrades(self, user_id: int):
        """완료된 업그레이드 처리"""
        buildings = self.db_manager.get_user_internal_buildings(user_id)
        now = datetime.now()
        
        for b in buildings:
            if b["status"] == "UPGRADING" and b["finish_time"]:
                finish_time = datetime.fromisoformat(b["finish_time"])
                if now >= finish_time:
                    # 업그레이드 완료 처리
                    new_level = b["level"] + 1
                    self.db_manager.update_building_status(
                        user_id, b["type"], new_level, "IDLE", None
                    )
                    print(f"User {user_id}: {b['type']} upgraded to Lv.{new_level}")

    def get_buffs(self, user_id: int) -> Dict[str, float]:
        """유저의 건물 버프 효과 계산"""
        buildings = self.db_manager.get_user_internal_buildings(user_id)
        buffs = {
            "max_troops": 0,        # 병력 최대치 (Barracks)
            "prod_food": 0.0,       # 식량 생산량 증가율 (Farm)
            "prod_mineral": 0.0,    # 광물 생산량 증가율 (Mine)
            "defense": 0.0,         # 방어력 증가율 (Wall)
            "gold_gen": 0,          # 시간당 골드 생산량 (House)
            "draft_speed_bonus": 0.0, # 징병 시간 감소율 (Barracks)
            "draft_cost_bonus": 0.0,  # 징병 비용 감소율 (Barracks)
            "trading_unlocked": False, # 무역 기능 해금 (Trading Post)
            "attack_bonus": 0.0,    # 공격력 증가율 (Smithy)
            "troop_save_rate": 0.0  # 패배 시 병력 보존율 (Hospital)
        }
        
        for b in buildings:
            lvl = b["level"]
            if lvl == 0: continue
            
            if b["type"] == self.BARRACKS:
                buffs["max_troops"] += lvl * 100
                # 징병 효율: 레벨당 2%, 최대 50%
                bonus = min(0.5, lvl * 0.02)
                buffs["draft_speed_bonus"] += bonus
                buffs["draft_cost_bonus"] += bonus
            elif b["type"] == self.FARM:
                buffs["prod_food"] += lvl * 0.05
            elif b["type"] == self.MINE:
                buffs["prod_mineral"] += lvl * 0.05
            elif b["type"] == self.WALL:
                buffs["defense"] += lvl * 0.05
            elif b["type"] == self.HOUSE:
                buffs["gold_gen"] += lvl * 100
            elif b["type"] == self.TRADING_POST:
                buffs["trading_unlocked"] = True
            elif b["type"] == self.SMITHY:
                # 대장간: 레벨당 3% 공격력 증가, 최대 30%
                buffs["attack_bonus"] += min(0.3, lvl * 0.03)
            elif b["type"] == self.HOSPITAL:
                # 병원: 레벨당 5% 병력 보존, 최대 50%
                buffs["troop_save_rate"] += min(0.5, lvl * 0.05)
                
        return buffs

    def collect_gold(self, user_id: int):
        """민가(House)에서 생산된 골드 수집"""
        buffs = self.get_buffs(user_id)
        hourly_rate = buffs.get("gold_gen", 0)
        
        if hourly_rate <= 0:
            return
            
        user_info = self.db_manager.get_user_info(user_id)
        if not user_info: return
        
        self.db_manager.update_user_gold_generation(user_id, hourly_rate)
