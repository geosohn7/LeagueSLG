from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
import os

# Add the parent directory to sys.path to import existing classes
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.factories.champion_factory import create_champion, _load_champion_data
from src.logic.battle.battle import Battle
from src.models.champion import Champion
from src.models.world_map import WorldMap
from src.logic.map_manager import MapManager
from src.logic.building_manager import BuildingManager
from src.logic.troop_manager import TroopManager
from src.models.tile import TileCategory, ResourceType
from src.models.building import BuildingType
from src.db_manager import DatabaseManager

app = FastAPI()

# Mount Static Files (optional for web version)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Allow CORS for Flutter development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Global Game State
# =========================
# In production, this should be stored in a database
# For now, we'll use in-memory state
game_state = {
    "world_map": None,
    "map_manager": None,
    "building_manager": None,
    "troop_manager": None,
    "db_manager": DatabaseManager()
}

def initialize_game():
    """Initialize the game world if not already done"""
    if game_state["world_map"] is None:
        world_map = WorldMap(width=20, height=20)
        map_manager = MapManager(world_map)
        building_manager = BuildingManager(game_state["db_manager"])
        troop_manager = TroopManager(game_state["db_manager"], building_manager)
        
        game_state["world_map"] = world_map
        game_state["map_manager"] = map_manager
        game_state["building_manager"] = building_manager
        game_state["troop_manager"] = troop_manager
        print("✅ Game world initialized (20x20)")

# Initialize on startup
initialize_game()

# =========================
# Pydantic Models
# =========================
class BattleRequest(BaseModel):
    left_id: str
    right_id: str

class MarchRequest(BaseModel):
    user_id: str
    champion_key: str
    target_x: int
    target_y: int

class BuildingPlaceRequest(BaseModel):
    user_id: str
    building_type: str  # "MAIN_CASTLE" or "BARRACKS"
    x: int
    y: int

# =========================
# Map Endpoints
# =========================
@app.get("/map")
async def get_map():
    """
    전체 맵 데이터를 Flutter로 전송
    Returns: 맵 크기, 타일 배열 정보
    """
    world_map = game_state["world_map"]
    
    tiles_data = []
    for y in range(world_map.height):
        for x in range(world_map.width):
            tile = world_map.get_tile(x, y)
            tile_info = {
                "x": tile.x,
                "y": tile.y,
                "category": tile.category.name,
                "level": tile.level,
                "owner_id": tile.owner_id,
            }
            
            # 자원 타일인 경우
            if tile.category == TileCategory.RESOURCE:
                tile_info["resource_type"] = tile.res_type.name
            
            # 건물이 있는 경우
            if tile.building:
                tile_info["building"] = {
                    "type": tile.building.type.name,
                    "name": tile.building.name,
                    "level": tile.building.level,
                    "is_root": tile.is_building_root
                }
            
            # 주둔 부대가 있는 경우
            if tile.occupying_army:
                army = tile.occupying_army
                tile_info["army"] = {
                    "id": army.id,
                    "owner_id": army.owner_id,
                    "champion_name": army.champion.name,
                    "troops": army.troop_count,
                    "max_troops": army.max_troop_count,
                    "status": army.status
                }
            
            tiles_data.append(tile_info)
    
    return {
        "width": world_map.width,
        "height": world_map.height,
        "tiles": tiles_data
    }

@app.get("/map/tile/{x}/{y}")
async def get_tile_detail(x: int, y: int):
    """특정 타일의 상세 정보 조회"""
    world_map = game_state["world_map"]
    tile = world_map.get_tile(x, y)
    
    if not tile:
        raise HTTPException(status_code=404, detail="Tile not found")
    
    return {
        "x": tile.x,
        "y": tile.y,
        "category": tile.category.name,
        "resource_type": tile.res_type.name if tile.category == TileCategory.RESOURCE else None,
        "level": tile.level,
        "owner_id": tile.owner_id,
        "durability": tile.current_durability,
        "max_durability": tile.max_durability,
        "production": tile.get_production()
    }

# =========================
# User Endpoints
# =========================
@app.get("/user/{user_id}")
async def get_user_status(user_id: str):
    """
    유저의 현재 상태 조회 (자원, 보유 챔피언 등)
    """
    db_manager = game_state["db_manager"]
    
    # DB에서 유저 정보 가져오기 (없으면 생성)
    user_db_id = db_manager.get_or_create_user(user_id)
    
    # 상태 업데이트 (건물/징병 완료 체크)
    game_state["building_manager"].check_upgrades(user_db_id)
    game_state["troop_manager"].check_drafts(user_db_id)
    game_state["building_manager"].collect_gold(user_db_id)

    user_info = db_manager.get_user_info(user_db_id)
    champions = db_manager.get_user_champions(user_db_id)
    
    return {
        "user_id": user_id,
        "db_id": user_db_id,
        "resources": user_info.get("resources", {}),
        "champions": champions
    }

@app.post("/user/{user_id}/champion/add")
async def add_champion_to_user(user_id: str, champion_key: str):
    """유저에게 챔피언 추가"""
    db_manager = game_state["db_manager"]
    user_db_id = db_manager.get_or_create_user(user_id)
    db_manager.add_champion_to_user(user_db_id, champion_key)
    
    return {"message": f"Champion {champion_key} added to user {user_id}"}

# =========================
# March & Army Endpoints
# =========================
@app.post("/map/march")
async def send_march(request: MarchRequest):
    """
    부대를 특정 좌표로 행군시킴
    """
    map_manager = game_state["map_manager"]
    world_map = game_state["world_map"]
    
    # 챔피언 생성 및 부대 편성
    champion = create_champion(request.champion_key)
    champion.level = 1
    champion.recalculate_stats()
    champion.reset_status()
    
    army = map_manager.create_army(request.user_id, champion)
    
    # 유저의 본진 찾기 (임시로 (0, 0) 사용, 실제로는 DB에서 조회)
    army.set_position(0, 0)
    army.home_pos = (0, 0)
    
    # 행군 명령
    target_pos = (request.target_x, request.target_y)
    march = map_manager.send_march(army, target_pos)
    
    if not march:
        raise HTTPException(status_code=400, detail="Cannot march to that location")
    
    return {
        "message": "March started",
        "army_id": army.id,
        "target": target_pos,
        "arrival_time": march.arrival_time.isoformat()
    }

@app.get("/map/marches")
async def get_active_marches():
    """현재 진행 중인 모든 행군 조회"""
    map_manager = game_state["map_manager"]
    
    marches_data = []
    for march in map_manager.active_marches:
        marches_data.append({
            "army_id": march.army.id,
            "owner_id": march.army.owner_id,
            "champion_name": march.army.champion.name,
            "from": march.start_pos,
            "to": march.target_pos,
            "status": march.status.name,
            "arrival_time": march.arrival_time.isoformat()
        })
    
    return {"marches": marches_data}

@app.post("/map/update")
async def update_game_state():
    """
    게임 상태 업데이트 (행군 도착 처리 + 자원 수집)
    Flutter에서 주기적으로 호출
    """
    map_manager = game_state["map_manager"]
    world_map = game_state["world_map"]
    db_manager = game_state["db_manager"]
    building_manager = game_state["building_manager"]
    troop_manager = game_state["troop_manager"]
    
    # 1. 행군 처리
    map_manager.update()
    
    # 2. 자원 수집 (모든 소유 타일에서)
    collected_by_user = {}  # {user_id: {resource_type: amount}}
    
    for y in range(world_map.height):
        for x in range(world_map.width):
            tile = world_map.get_tile(x, y)
            if tile and tile.owner_id:
                collected = tile.collect_resources()
                if collected:
                    if tile.owner_id not in collected_by_user:
                        collected_by_user[tile.owner_id] = {}
                    
                    for res_type, amount in collected.items():
                        if res_type not in collected_by_user[tile.owner_id]:
                            collected_by_user[tile.owner_id][res_type] = 0
                        collected_by_user[tile.owner_id][res_type] += amount
    
    # 3. DB에 자원 반영 및 건물/징병 상태 업데이트
    active_users = set(collected_by_user.keys())
    
    # 모든 유저를 Loop 돌 수 없으므로, 자원이 걷힌 유저 + 접속 유저 위주로 해야하지만
    # MVP에서는 자원 획득 유저에 대해서만 체크하도록 단순화하거나, 모든 유저 ID를 DB에서 가져와야 함.
    # 여기서는 일단 "자원을 획득한 유저"에 대해서만 업데이트 수행 (최적화 이슈 있음)
    # --> 더 나은 방법: BuildingManager 내부에 active_upgrade_list 등을 유지하는 것.
    # 일단은 자원 수집 루프 내에서 처리.
    
    for user_id, resources in collected_by_user.items():
        user_db_id = db_manager.get_or_create_user(user_id)
        
        # 자원 추가
        for res_type, amount in resources.items():
            db_manager.update_user_resource(user_db_id, res_type, amount)
            
        # 건물 업그레이드 체크
        building_manager.check_upgrades(user_db_id)
        # 징병 완료 체크
        troop_manager.check_drafts(user_db_id)
        
        # 골드 자동 수집 (민가)
        # TODO: 타일 없는 유저도 골드 수집이 필요하다면 별도 로직 필요
        building_manager.collect_gold(user_db_id)
    
    return {
        "message": "Game state updated", 
        "active_marches": len(map_manager.active_marches),
        "resources_collected": collected_by_user
    }

# =========================
# Building Endpoints
# =========================
@app.post("/map/building/place")
async def place_building(request: BuildingPlaceRequest):
    """맵에 건물 배치"""
    world_map = game_state["world_map"]
    
    # BuildingType enum으로 변환
    try:
        building_type = BuildingType[request.building_type]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid building type")
    
    root_pos = (request.x, request.y)
    building = world_map.place_building(building_type, request.user_id, root_pos)
    
    if not building:
        raise HTTPException(status_code=400, detail="Cannot place building at that location")
    
    return {
        "message": "Building placed",
        "building_id": building.id,
        "type": building.type.name,
        "position": root_pos
    }

# =========================
# Champion Endpoints (기존)
# =========================
@app.get("/champions")
async def get_champions():
    data = _load_champion_data()
    return [{"id": k, "name": v["name"], "base_stat": v["base_stat"]} for k, v in data.items()]

# =========================
# Battle Endpoints (기존)
# =========================
class WebBattle(Battle):
    """3v3 웹 배틀 (로그 수집용)"""
    def __init__(self, left_team: List[Champion], right_team: List[Champion], 
                 left_unit_type: str = "cavalry", right_unit_type: str = "cavalry"):
        # 임시 Army 객체 생성 (Battle이 Army를 요구하므로)
        from src.models.army import Army
        temp_left_army = Army("temp_left", "player", left_team, left_unit_type)
        temp_right_army = Army("temp_right", "npc", right_team, right_unit_type)
        
        super().__init__(temp_left_army, temp_right_army)
        self.logs = []

    def _log(self, msg: str):
        pass  # 콘솔 출력 비활성화

    def _process_turn(self, actor: Champion, enemy_team: List[Champion]):
        """개별 챔피언의 턴 동작을 처리하고 로그 수집"""
        import random
        
        # 타겟 선택
        alive_enemies = [c for c in enemy_team if c.is_alive()]
        if not alive_enemies:
            return
        
        target = random.choice(alive_enemies)
        
        turn_data = {
            "turn": self.turn,
            "actor": actor.name,
            "target": target.name,
            "left_hp": sum(c.current_hp for c in self.left_team if c.is_alive()),
            "right_hp": sum(c.current_hp for c in self.right_team if c.is_alive())
        }
        
        actor.on_turn_start()
        
        skill = actor.roll_skills()
        if skill:
            action_name = skill.name
            old_hp = target.current_hp
            skill.cast(self, actor, target)
            damage = old_hp - target.current_hp
        else:
            action_name = "일반 공격"
            atk = actor.getStat('ATK')
            df = target.getStat('DEF')
            damage = (atk * atk) / max(1, df)
            target.take_damage(damage)

        turn_data.update({
            "action": action_name,
            "damage": damage,
            "message": f"{actor.name}의 {action_name}! → {target.name} ({damage:.1f} 데미지)",
            "left_hp": sum(c.current_hp for c in self.left_team if c.is_alive()),
            "right_hp": sum(c.current_hp for c in self.right_team if c.is_alive())
        })
        
        self.logs.append(turn_data)
        actor.on_turn_end()

    def run_to_end(self):
        """전투를 끝까지 실행하고 결과 반환"""
        from datetime import datetime
        
        while self._both_teams_alive() and self.turn < 100:
            all_champions = self._get_turn_order()
            
            for champion in all_champions:
                if not champion.is_alive():
                    continue
                
                enemy_team = self.right_team if champion in self.left_team else self.left_team
                
                if not self._team_alive(enemy_team):
                    break
                
                self._process_turn(champion, enemy_team)
            
            self.turn += 1
        
        # 승리 팀 결정
        if self._team_alive(self.left_team):
            winner_team = "left"
            winners = self.left_team
        else:
            winner_team = "right"
            winners = self.right_team
        
        winner_names = ", ".join(c.name for c in winners if c.is_alive())
        
        return {
            "winner_team": winner_team,
            "winner": winner_names,  # 하위 호환성
            "logs": self.logs,
            "left": [{"name": c.name, "max_hp": c.max_hp, "current_hp": c.current_hp} for c in self.left_team],
            "right": [{"name": c.name, "max_hp": c.max_hp, "current_hp": c.current_hp} for c in self.right_team],
            "timestamp": datetime.now().isoformat()
        }

@app.post("/simulate")
async def simulate_battle(request: BattleRequest):
    try:
        left = create_champion(request.left_id)
        right = create_champion(request.right_id)
        
        battle = WebBattle(left, right)
        result = battle.run_to_end()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/battle/results/{user_id}")
async def get_battle_results(user_id: str):
    """
    유저의 완료된(보지 않은) 전투 결과 조회
    """
    map_manager = game_state["map_manager"]
    if not map_manager:
        return []
    
    # MapManager에 추가한 get_pending_battles 메서드 사용
    return map_manager.get_pending_battles(user_id)

# =========================
# Server Entry Point
# =========================
# =========================
# Resource & Building Endpoints
# =========================
@app.get("/building/list/{user_id}")
async def list_buildings(user_id: str):
    """유저의 자원 및 건물 현황 조회"""
    db_manager = game_state["db_manager"]
    building_manager = game_state["building_manager"]
    troop_manager = game_state["troop_manager"]
    
    # DB 조회
    user_db_id = db_manager.get_or_create_user(user_id)
    buildings = db_manager.get_user_internal_buildings(user_db_id)
    
    # 기본 건물 목록 (없는 경우 Lv0으로 표시하기 위함)
    all_types = [
        BuildingManager.HOUSE,
        BuildingManager.BARRACKS, 
        BuildingManager.FARM, 
        BuildingManager.MINE, 
        BuildingManager.WALL,
        BuildingManager.SMITHY,
        BuildingManager.HOSPITAL,
        BuildingManager.TRADING_POST
    ]
    existing_types = {b["type"] for b in buildings}
    
    for b_type in all_types:
        if b_type not in existing_types:
            buildings.append({
                "type": b_type,
                "level": 0,
                "status": "IDLE",
                "finish_time": None
            })
            
    # 업그레이드 비용 정보 추가
    for b in buildings:
        b["next_cost"] = building_manager.get_upgrade_cost(b["type"], b["level"])
        
    return {
        "buildings": buildings,
        "max_troops": troop_manager.get_max_troops(user_db_id)
    }

class UpgradeRequest(BaseModel):
    user_id: str
    building_type: str

@app.post("/building/upgrade")
async def upgrade_building(request: UpgradeRequest):
    """건물 업그레이드 시작"""
    db_manager = game_state["db_manager"]
    building_manager = game_state["building_manager"]
    
    user_db_id = db_manager.get_or_create_user(request.user_id)
    success, msg = building_manager.start_upgrade(user_db_id, request.building_type)
    
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.post("/building/instant_finish")
async def instant_finish_building(request: UpgradeRequest):
    """건물 즉시 완료 (골드 소모)"""
    db_manager = game_state["db_manager"]
    building_manager = game_state["building_manager"]
    
    user_db_id = db_manager.get_or_create_user(request.user_id)
    success, msg = building_manager.instant_finish(user_db_id, request.building_type)
    
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

# =========================
# Troop Endpoints
# =========================
class DraftRequest(BaseModel):
    user_id: str
    amount: int

@app.post("/troops/draft")
async def draft_troops(request: DraftRequest):
    """징병 시작"""
    db_manager = game_state["db_manager"]
    troop_manager = game_state["troop_manager"]
    
    user_db_id = db_manager.get_or_create_user(request.user_id)
    success, msg = troop_manager.start_draft(user_db_id, request.amount)
    
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

class AssignRequest(BaseModel):
    user_id: str
    champion_key: str
    amount: int

@app.post("/troops/assign")
async def assign_troops_to_champion(request: AssignRequest):
    """예비 병력을 장수에게 배치 (HP 회복)"""
    db_manager = game_state["db_manager"]
    map_manager = game_state["map_manager"]
    troop_manager = game_state["troop_manager"]
    
    user_db_id = db_manager.get_or_create_user(request.user_id)
    
    # 1. 장수(Army) 찾기 (MapManager에서)
    target_army = None
    # armies dictionary was added to MapManager but might not be fully populated or keyed correctly
    # Let's search in active_marches or scan tile? No, armies are better.
    # We need a way to find specific user's specific champion army.
    # For MVP, let's iterate tiles or keep an army list in MapManager.
    # Assuming MapManager.armies is populated.
    
    # Find army by owner_id and champion name
    for army in map_manager.armies.values():
        if army.owner_id == request.user_id and army.champion.name == request.champion_key:
            target_army = army
            break
            
    if not target_army:
         raise HTTPException(status_code=404, detail="Champion army not found.")
         
    # 2. 위치 확인 (본성/거점에 있어야 함 - 일단은 내 성 or 내 타일이면 허용)
    tile = game_state["world_map"].get_tile(target_army.pos_x, target_army.pos_y)
    if not tile or tile.owner_id != request.user_id:
         raise HTTPException(status_code=400, detail="Champion must be in your territory.")
         
    # 3. 최대 HP 체크
    max_hp = target_army.champion.max_hp
    current_hp = target_army.champion.current_hp
    needed = max_hp - current_hp
    
    if needed <= 0:
        raise HTTPException(status_code=400, detail="Champion HP is already full.")
        
    assign_amount = min(request.amount, needed)
    
    # 4. 병력 차감 (Manager)
    db_manager.update_user_troops(user_db_id, -assign_amount)
    
    # 5. HP 회복
    target_army.champion.current_hp += assign_amount
    target_army.troop_count = target_army.champion.current_hp # Sync troop count
    
    return {
        "message": f"Assigned {assign_amount} troops.",
        "champion": target_army.champion.name,
        "current_hp": target_army.champion.current_hp,
        "remaining_reserve": db_manager.get_user_info(user_db_id).get("reserve_troops", 0)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
