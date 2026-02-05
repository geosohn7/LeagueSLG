from enum import Enum
from typing import Optional, List, Tuple

class BuildingType(Enum):
    MAIN_CASTLE = ("주성", 3)  # 이름, 크기(Size x Size)
    BARRACKS = ("막사", 1)

class Building:
    """
    맵 위에 건설되는 건물 클래스
    """
    def __init__(self, building_id: str, b_type: BuildingType, owner_id: str, root_pos: Tuple[int, int]):
        self.id = building_id
        self.type = b_type
        self.name = b_type.value[0]
        self.size = b_type.value[1]
        self.owner_id = owner_id
        self.root_pos = root_pos  # 건물의 좌측 상단 좌표 (x, y)
        
        self.level = 1
        self.max_hp = 1000 * self.level
        self.current_hp = self.max_hp
        
        # 실제 점유하고 있는 모든 타일 좌표 리스트 계산
        self.occupied_tiles: List[Tuple[int, int]] = []
        for dy in range(self.size):
            for dx in range(self.size):
                self.occupied_tiles.append((root_pos[0] + dx, root_pos[1] + dy))

    def is_destroyed(self) -> bool:
        return self.current_hp <= 0

    def __repr__(self):
        return f"Building({self.name}, Owner: {self.owner_id}, Size: {self.size}x{self.size}, Pos: {self.root_pos})"
