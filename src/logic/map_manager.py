from typing import List, Dict, Optional
from src.models.world_map import WorldMap
from src.models.march import March, MarchStatus
from src.models.tile import Tile, TileCategory
from src.models.army import Army
from src.models.champion import Champion
from src.factories.champion_factory import create_champion
from src.logic.battle.battle import Battle

class MapManager:
    """
    월드 맵과 행군 부대들을 총괄 관리하는 클래스
    """
    def __init__(self, world_map: WorldMap):
        self.world_map = world_map
        self.active_marches: List[March] = []
        self.armies: Dict[str, Army] = {}

    def create_army(self, user_id: str, champion: Champion) -> Army:
        army_id = f"army_{user_id}_{champion.name}"
        army = Army(army_id, user_id, champion)
        self.armies[army_id] = army
        return army

    def send_march(self, army: Army, target_pos: tuple, is_retreat: bool = False):
        """부대를 파견 (일반 행군 또는 후퇴)"""
        x, y = target_pos
        target_tile = self.world_map.get_tile(x, y)
        
        # 이동 가능한 타일인지 체크 (장애물/타인 건물 등)
        # 단, 후퇴 시에는 체크를 완화하거나 본진으로 무조건 이동하도록 설정 가능
        if not is_retreat and (not target_tile or not target_tile.can_pass(army.owner_id)):
            print(f"Error: {target_pos}로 행군할 수 없습니다. (장애물 또는 타인의 영지)")
            return None

        # 출발지 타일 업데이트
        if army.pos_x is not None and army.pos_y is not None:
            old_tile = self.world_map.get_tile(army.pos_x, army.pos_y)
            if old_tile and old_tile.occupying_army == army:
                old_tile.occupying_army = None

        march = March(army.owner_id, army, (army.pos_x or 0, army.pos_y or 0), target_pos)
        if is_retreat:
            march.status = MarchStatus.RETURNING
            print(f"[{army.owner_id}] {army.champion.name} 부대가 본진({target_pos})으로 후퇴합니다.")
        else:
            print(f"[{army.owner_id}] {army.champion.name} 부대가 {target_pos}로 이동을 시작했습니다.")
            
        self.active_marches.append(march)
        return march

    def update(self):
        """행군 상태 체크"""
        arrived_marches = [m for m in self.active_marches if m.is_arrived()]
        for march in arrived_marches:
            self._handle_arrival(march)
            self.active_marches.remove(march)

    def _handle_arrival(self, march: March):
        """목적지 도착 시 처리 (전투 및 점령)"""
        x, y = march.target_pos
        tile = self.world_map.get_tile(x, y)
        army = march.army
        
        if not tile: return

        # 0. 후퇴 완료 처리
        if march.status == MarchStatus.RETURNING:
            print(f"\n>>> [{army.owner_id}] 부대가 본진({x}, {y})에 무사히 후퇴했습니다.")
            army.set_position(x, y)
            army.status = "IDLE"
            march.status = MarchStatus.COMPLETED
            return

        print(f"\n>>> [{army.owner_id}] {army.champion.name} 부대가 ({x}, {y})에 도착!")

        # 1. 자원 타일의 수비군(NPC) 전투 체크
        if tile.category == TileCategory.RESOURCE and not tile.owner_id:
            print(f"--- [Lv.{tile.level} {tile.res_type.value}] 수비군 대치! ---")
            
            # 수비군 생성: Lv.N 다리우스 (유저 요청대로 기본 stat에 따른 HP 사용)
            npc_champ = create_champion("Darius")
            npc_champ.level = tile.level
            npc_champ.recalculate_stats()
            npc_champ.reset_status() # HP 풀로 채우기
            
            # 교전 시작
            battle = Battle(army.champion, npc_champ)
            battle.start()
            
            if army.champion.is_alive():
                print(f"결과: 점령 성공! 이제 ({x}, {y})는 {army.owner_id}의 영토입니다.")
                tile.occupy(army.owner_id)
                self._stay_at_tile(army, tile, x, y)
            else:
                print(f"결과: 점령 실패... 부대가 전멸 위기입니다. 본진으로 후퇴합니다.")
                # 전투 중 사망했더라도 시스템 상 부대를 유지하기 위해 HP 1로 부활(후퇴 편의상)
                army.champion.current_hp = 1 
                self.send_march(army, army.home_pos, is_retreat=True)
            
        # 2. 타인의 건물지 공격 (생략 가능, 현재는 자동 승리/점령으로 임시 처리)
        elif tile.owner_id and tile.owner_id != army.owner_id:
            print(f"--- [{tile.owner_id}]의 영지를 공격! ---")
            tile.occupy(army.owner_id)
            print(f"결과: 공격 승리!")
            self._stay_at_tile(army, tile, x, y)
        
        else:
            # 이미 내 땅이거나 빈 땅
            self._stay_at_tile(army, tile, x, y)

        march.status = MarchStatus.COMPLETED

    def _stay_at_tile(self, army: Army, tile: Tile, x: int, y: int):
        """부대를 해당 타일에 주둔시키고 위치 정보 업데이트"""
        tile.occupying_army = army
        army.set_position(x, y)
        army.status = "STATIONED"
        print(f"[{army.owner_id}] 부대가 ({x}, {y})에 주둔합니다.")
