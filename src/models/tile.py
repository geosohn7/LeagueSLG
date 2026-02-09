from enum import Enum
from typing import Optional, List
from datetime import datetime
from src.models.building import Building
from src.models.army import Army

class TileCategory(Enum):
    RESOURCE = "자원"
    BUILDING = "건물"
    OBSTACLE = "장애물"

class ResourceType(Enum):
    FOOD = "농지"
    WOOD = "목재"
    IRON = "철광"
    STONE = "석재"
    NONE = "없음"

class Tile:
    """
    월드 맵의 개별 타일 클래스
    """
    def __init__(self, x: int, y: int, category: TileCategory = TileCategory.RESOURCE, 
                 res_type: ResourceType = ResourceType.NONE, level: int = 1):
        self.x = x
        self.y = y
        self.category = category
        self.res_type = res_type
        self.level = level
        
        self.owner_id: Optional[str] = None
        self.occupying_army: Optional[Army] = None  # 현재 주둔 중인 아군 부대
        
        # 중립 수비군 (자원 타일의 경우)
        self.guard_army: Optional[Army] = None 
        
        self.building: Optional[Building] = None
        self.is_building_root = False
        
        # SLG 특성: 내구도
        self.max_durability = 100 * level
        self.current_durability = self.max_durability
        
        # 자원 생산: 마지막 수집 시간
        self.last_collected: Optional[datetime] = None

    def can_pass(self, user_id: str) -> bool:
        """이동 가능 여부 체크"""
        if self.category == TileCategory.OBSTACLE:
            return False
        
        # 건물 타일인 경우 소유주만 통과 가능
        if self.category == TileCategory.BUILDING:
            if self.owner_id and self.owner_id != user_id:
                return False
        
        return True

    def get_hourly_production(self) -> int:
        """시간당 생산량 반환: (2*level - 1) * 100"""
        if self.category == TileCategory.RESOURCE and self.owner_id:
            return (2 * self.level - 1) * 100
        return 0

    def get_production(self) -> dict:
        """이 타일에서 생산되는 자원량 반환 (1시간 기준)"""
        if self.category == TileCategory.RESOURCE and self.owner_id:
            amount = self.get_hourly_production()
            return {self.res_type.name.lower(): amount}
        return {}
    
    def collect_resources(self) -> dict:
        """
        마지막 수집 이후 경과 시간에 따른 자원 수집.
        반환값: {"resource_type": collected_amount}
        """
        if self.category != TileCategory.RESOURCE or not self.owner_id:
            return {}
        
        now = datetime.now()
        
        # 첫 수집인 경우 (점령 직후)
        if self.last_collected is None:
            self.last_collected = now
            return {}
        
        # 경과 시간 계산 (초 단위)
        elapsed_seconds = (now - self.last_collected).total_seconds()
        hours_elapsed = elapsed_seconds / 3600.0
        
        # 생산량 계산
        hourly_rate = self.get_hourly_production()
        collected_amount = int(hourly_rate * hours_elapsed)
        
        if collected_amount > 0:
            self.last_collected = now
            resource_key = self.res_type.name.lower()
            return {resource_key: collected_amount}
        
        return {}

    def occupy(self, user_id: str):
        """타일을 점령 처리"""
        self.owner_id = user_id
        self.current_durability = self.max_durability
        # 점령 시 중립 수비군 제거
        self.guard_army = None
        # 자원 생산 시작 시점 기록
        self.last_collected = datetime.now()

    def __repr__(self):
        category_name = self.res_type.value if self.category == TileCategory.RESOURCE else self.category.value
        owner = self.owner_id if self.owner_id else "중립"
        return f"Tile({self.x}, {self.y}) - {category_name} Lv.{self.level} [{owner}]"
