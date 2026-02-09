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
        self.battle_logs: Dict[str, List[dict]] = {}  # {user_id: [battle_result_dict]}


    def create_army(self, user_id: str, champions: List[Champion]) -> Army:
        """최대 3명의 챔피언으로 부대 생성"""
        champion_names = "_".join(c.name for c in champions[:3])
        army_id = f"army_{user_id}_{champion_names}"
        army = Army(army_id, user_id, champions)
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
        champion_names = ", ".join(c.name for c in army.champions)
        if is_retreat:
            march.status = MarchStatus.RETURNING
            print(f"[{army.owner_id}] [{champion_names}] 부대가 본진({target_pos})으로 후퇴합니다.")
        else:
            print(f"[{army.owner_id}] [{champion_names}] 부대가 {target_pos}로 이동을 시작했습니다.")
            
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

        champion_names = ", ".join(c.name for c in army.champions)
        print(f"\n>>> [{army.owner_id}] [{champion_names}] 부대가 ({x}, {y})에 도착!")

        # 1. 자원 타일의 수비군(NPC) 전투 체크
        if tile.category == TileCategory.RESOURCE and not tile.owner_id:
            print(f"--- [Lv.{tile.level} {tile.res_type.value}] 수비군 대치! ---")
            
            # 수비군 생성: 타일 레벨에 따라 1~3명
            npc_count = min(3, max(1, tile.level // 2))  # Lv1-2: 1명, Lv3-4: 2명, Lv5+: 3명
            npc_team = []
            for i in range(npc_count):
                npc_champ = create_champion("Darius")
                npc_champ.level = tile.level
                npc_champ.recalculate_stats()
                npc_champ.reset_status()
                npc_champ.name = f"수비군{i+1} (Lv.{tile.level})"
                npc_team.append(npc_champ)
            
            # NPC 병종 랜덤 선택
            import random
            npc_unit_type = random.choice(["cavalry", "spearman", "archer", "shieldman"])
            
            # [전투 시뮬레이션]
            from src.api.server import WebBattle 
            
            battle = WebBattle(army.champions, npc_team, army.unit_type, npc_unit_type)
            result = battle.run_to_end()
            
            # 전투 기록 저장
            if army.owner_id not in self.battle_logs:
                self.battle_logs[army.owner_id] = []
            
            battle_record = {
                "type": "PVE",
                "pos": (x, y),
                "result": result,
                "timestamp": str(result.get("timestamp", "")) 
            }
            self.battle_logs[army.owner_id].append(battle_record)

            winner_team = result["winner_team"]
            
            if winner_team == "left":  # 플레이어 팀 승리
                print(f"결과: 점령 성공! 이제 ({x}, {y})는 {army.owner_id}의 영토입니다.")
                tile.occupy(army.owner_id)
                self._stay_at_tile(army, tile, x, y)
            else:
                print(f"결과: 점령 실패... 부대가 전멸 위기입니다. 본진으로 후퇴합니다.")
                # 전투 중 사망했더라도 시스템 상 부대를 유지하기 위해 생존자 HP 1로 설정
                for champ in army.champions:
                    if champ.is_alive():
                        champ.current_hp = max(1, champ.current_hp)
                    else:
                        champ.current_hp = 1
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

    def get_pending_battles(self, user_id: str) -> List[dict]:
        """유저의 확인하지 않은 전투 기록 반환 후 삭제"""
        if user_id in self.battle_logs and self.battle_logs[user_id]:
            logs = self.battle_logs[user_id]
            self.battle_logs[user_id] = [] # Clear logs after fetching
            return logs
        return []

    def _stay_at_tile(self, army: Army, tile: Tile, x: int, y: int):
        """부대를 해당 타일에 주둔시키고 위치 정보 업데이트"""
        tile.occupying_army = army
        army.set_position(x, y)
        army.status = "STATIONED"
        print(f"[{army.owner_id}] 부대가 ({x}, {y})에 주둔합니다.")
