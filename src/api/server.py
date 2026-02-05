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
    "db_manager": DatabaseManager()
}

def initialize_game():
    """Initialize the game world if not already done"""
    if game_state["world_map"] is None:
        world_map = WorldMap(width=20, height=20)
        map_manager = MapManager(world_map)
        game_state["world_map"] = world_map
        game_state["map_manager"] = map_manager
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
    user_info = db_manager.get_user_info(user_db_id)
    champions = db_manager.get_user_champions(user_db_id)
    
    return {
        "user_id": user_id,
        "db_id": user_db_id,
        "gold": user_info.get("gold", 1000),
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
    게임 상태 업데이트 (행군 도착 처리 등)
    Flutter에서 주기적으로 호출
    """
    map_manager = game_state["map_manager"]
    map_manager.update()
    
    return {"message": "Game state updated", "active_marches": len(map_manager.active_marches)}

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
    def __init__(self, left: Champion, right: Champion):
        super().__init__(left, right)
        self.logs = []

    def _log(self, msg: str):
        pass

    def _process_turn(self, actor: Champion, target: Champion):
        turn_data = {
            "turn": self.turn,
            "actor": actor.name,
            "target": target.name,
            "left_hp": self.left.current_hp,
            "right_hp": self.right.current_hp
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
            "message": f"{actor.name}의 {action_name}! ({damage:.1f} 데미지)",
            "left_hp": self.left.current_hp,
            "right_hp": self.right.current_hp
        })
        
        self.logs.append(turn_data)
        actor.on_turn_end()

    def run_to_end(self):
        while self._both_alive() and self.turn < 100:
            first, second = self._get_turn_order()
            self._process_turn(first, second)
            if not second.is_alive():
                break
            self._process_turn(second, first)
            self.turn += 1
        
        winner = self.left.name if self.left.is_alive() else self.right.name
        return {
            "winner": winner, 
            "logs": self.logs,
            "left": {"name": self.left.name, "max_hp": self.left.max_hp},
            "right": {"name": self.right.name, "max_hp": self.right.max_hp}
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

# =========================
# Server Entry Point
# =========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
