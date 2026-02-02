import random
from typing import List, Optional, Tuple
from src.models.tile import Tile, TileCategory, ResourceType
from src.models.building import Building, BuildingType
from src.models.army import Army

class WorldMap:
    """
    전체 월드 맵 관리 클래스
    """
    def __init__(self, width: int = 20, height: int = 20):
        self.width = width
        self.height = height
        self.grid: List[List[Tile]] = []
        self._generate_map()

    def _generate_map(self):
        """맵 생성 로직: 자원 타일과 장애물 밸런스 배치"""
        for y in range(self.height):
            row = []
            for x in range(self.width):
                rand = random.random()
                
                if rand < 0.15: # 15% 확률로 장애물 (산, 강 등)
                    tile = Tile(x, y, category=TileCategory.OBSTACLE)
                else: # 나머지는 자원 타일
                    res_type = random.choice([ResourceType.FOOD, ResourceType.WOOD, ResourceType.IRON, ResourceType.STONE])
                    level = random.randint(1, 4)
                    if random.random() < 0.1: level = random.randint(5, 8) # 10% 확률로 고레벨
                    
                    tile = Tile(x, y, category=TileCategory.RESOURCE, res_type=res_type, level=level)
                
                row.append(tile)
            self.grid.append(row)

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None

    def can_place_building(self, b_type: BuildingType, root_pos: Tuple[int, int]) -> bool:
        size = b_type.value[1]
        rx, ry = root_pos
        for dy in range(size):
            for dx in range(size):
                tile = self.get_tile(rx + dx, ry + dy)
                if not tile or tile.category == TileCategory.OBSTACLE or tile.building:
                    return False
        return True

    def place_building(self, b_type: BuildingType, owner_id: str, root_pos: Tuple[int, int]) -> Optional[Building]:
        if not self.can_place_building(b_type, root_pos):
            return None
        
        building_id = f"{b_type.name}_{root_pos[0]}_{root_pos[1]}"
        new_building = Building(building_id, b_type, owner_id, root_pos)
        
        for x, y in new_building.occupied_tiles:
            tile = self.get_tile(x, y)
            tile.category = TileCategory.BUILDING # 카테고리 변경
            tile.building = new_building
            tile.owner_id = owner_id
            if (x, y) == root_pos:
                tile.is_building_root = True
        return new_building

    def display_ascii(self):
        for row in self.grid:
            line = ""
            for tile in row:
                if tile.category == TileCategory.OBSTACLE: line += "⛰️ "
                elif tile.building:
                    if tile.building.type == BuildingType.MAIN_CASTLE: line += "🏰" if tile.is_building_root else "▩ "
                    else: line += "🏠"
                elif tile.owner_id: line += "■ "
                else:
                    # 자원 약자 표시
                    res_map = {ResourceType.FOOD: "🌾", ResourceType.WOOD: "🌲", ResourceType.IRON: "⚒️", ResourceType.STONE: "💎"}
                    line += res_map.get(tile.res_type, "□ ")
            print(line)

    def __repr__(self):
        return f"WorldMap({self.width}x{self.height})"
