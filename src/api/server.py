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
from src.models.army_model import ArmyDb  # Added to resolve relationship
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
# initialize_game()  <-- Moving this to startup event or keeping it, but we need DB tables first

@app.on_event("startup")
async def startup_event():
    print("🚀 Server starting up...")
    
    # 1. Ensure DB Tables exist
    from src.common.database import Base, engine
    # Import models to register them with Base
    from src.models import user, user_champion, battle_log, user_internal_building, army_model
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables checked/created")
    
    # 2. Initialize Game State
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
    
    army = map_manager.create_army(request.user_id, [champion])
    
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
# Champion Roster Endpoints (NEW)
# =========================
@app.get("/user/{user_id}/champions")
async def get_user_champion_roster(user_id: str):
    """
    보유 장수 목록 조회 (카드 리스트용)
    Returns: 간략한 정보 (이름, 레벨, 이미지, 등급)
    """
    db_manager = game_state["db_manager"]
    user_db_id = db_manager.get_or_create_user(user_id)
    
    champions = db_manager.get_user_champions(user_db_id)
    champion_data = _load_champion_data()
    
    roster = []
    for champ in champions:
        key = champ["champion_key"]
        data = champion_data.get(key, {})
        
        roster.append({
            "id": champ["id"],
            "key": key,
            "name": data.get("name", key),
            "level": champ["level"],
            "exp": champ["exp"],
            "faction": data.get("faction", "Unknown"),
            "images": data.get("images", {}),
            # 등급은 base_stat 합계로 간단히 계산 (임시)
            "rating": sum(data.get("base_stat", [0]*6))
        })
    
    return {"user_id": user_id, "champions": roster}

@app.get("/user/{user_id}/champion/{champion_id}")
async def get_champion_detail(user_id: str, champion_id: int):
    """
    장수 상세 정보 조회
    Returns: 능력치, 아이템, 관련 인연, 설명
    """
    from src.logic.bond_manager import BondManager
    from src.logic.champion_mapper import orm_dict_to_champion
    
    db_manager = game_state["db_manager"]
    user_db_id = db_manager.get_or_create_user(user_id)
    
    # 챔피언 DB 조회
    champions = db_manager.get_user_champions(user_db_id)
    champ_data = next((c for c in champions if c["id"] == champion_id), None)
    
    if not champ_data:
        raise HTTPException(status_code=404, detail="Champion not found")
    
    # Champion 객체로 변환
    champion = orm_dict_to_champion(champ_data)
    champion_static_data = _load_champion_data().get(champ_data["champion_key"], {})
    
    # 인연 정보 조회
    bond_manager = BondManager()
    related_bonds = bond_manager.get_related_bonds(champion.name)
    
    return {
        "id": champion_id,
        "name": champion.name,
        "level": champion.level,
        "exp": champion.exp,
        "faction": champion.faction,
        "stats": champion.stat,
        "base_stat": champion.base_stat,
        "stat_growth": champion.stat_growth,
        "max_hp": champion.max_hp,
        "current_hp": champion.current_hp,
        "description": champion_static_data.get("description", "설명이 없습니다."),
        "images": champion_static_data.get("images", {}),
        "items": [{"name": getattr(item, "name", "Unknown")} for item in champion.items],
        "bonds": related_bonds,
        "skills": [{"name": skill.name} for skill in champion.skills]
    }

# =========================
# Gacha Endpoints
# =========================
@app.get("/gacha/config")
async def get_gacha_config():
    """가챠 설정 정보 조회"""
    from src.logic.gacha_service import GachaService
    db_manager = game_state["db_manager"]
    service = GachaService(db_manager)
    
    # 설정 파일 로드 (서비스 내부 메서드 활용 불가하므로 직접 로드하거나 서비스에 getter 추가 필요)
    # 여기서는 서비스 인스턴스의 변수 직접 접근 (Python)
    return service.gacha_config

class GachaPullRequest(BaseModel):
    user_id: str
    gacha_type: str

@app.post("/gacha/pull")
async def pull_gacha(request: GachaPullRequest):
    """가챠 실행"""
    from src.logic.gacha_service import GachaService
    db_manager = game_state["db_manager"]
    # 유저 DB ID 조회
    user_db_id = db_manager.get_or_create_user(request.user_id)
    
    service = GachaService(db_manager)
    success, msg, result = service.pull_champion(user_db_id, request.gacha_type)
    
    # [테스트용] 잔액 부족 시 자동 충전 후 재시도
    if not success and "Not enough" in msg:
        print(f"⚠️ [TEST MODE] Insufficient funds for {request.user_id}. Adding resources...")
        db_manager.update_user_resource(user_db_id, "gold", 5000)
        db_manager.update_user_resource(user_db_id, "silver", 10000)
        # 재시도
        success, msg, result = service.pull_champion(user_db_id, request.gacha_type)

    if not success:
        raise HTTPException(status_code=400, detail=msg)
    
    # 챔피언 상세 정보 추가 (편의성)
    data = _load_champion_data()
    champ_info = data.get(result["name"], {})
    
    return {
        "success": True,
        "message": msg,
        "result": {
            "name": result["name"],
            "image": champ_info.get("images", {}).get("portrait", ""),
            "faction": champ_info.get("faction", "Unknown"),
            "rating": sum(champ_info.get("base_stat", [0]*6)),
            "remaining_currency": result["remaining_currency"],
            "currency_type": result["currency_type"]
        }
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
    from src.logic.troop_service import TroopService
    
    troop_service = TroopService()
    try:
        # Champion Key가 아닌 DB ID가 필요하지만, Request에는 champion_key가 들어옴.
        # 따라서 User ID와 Champion Key로 DB ID를 찾아야 함.
        # TroopService가 이를 처리하거나 여기서 찾아서 넘겨야 함.
        # TroopService.assign_troops는 champion_id (DB ID)를 요구함.
        
        # 여기서 찾아보자.
        db_manager = game_state["db_manager"]
        user_db_id = db_manager.get_or_create_user(request.user_id)
        
        # Find champion DB ID by key
        champions = db_manager.get_user_champions(user_db_id)
        target_champ = next((c for c in champions if c["champion_key"] == request.champion_key), None)
        
        if not target_champ:
             raise HTTPException(status_code=404, detail="Champion not found.")
             
        success, msg, current_hp = troop_service.assign_troops(user_db_id, target_champ["id"], request.amount)
        
        if not success:
            raise HTTPException(status_code=400, detail=msg)
            
        return {
            "message": msg,
            "champion": request.champion_key,
            "current_hp": current_hp,
            # Reserve troops logic in TroopService updates User model, but we need to return it?
            # It's better to fetch fresh user info or just return.
            "remaining_reserve": "Check /user/{id}" 
        }
    finally:
        troop_service.close()

@app.post("/troops/heal_all")
async def heal_all_champions(request: DraftRequest):
    """
    모든 챔피언을 일괄 치료 (DraftRequest 재사용: user_id만 필요, amount 무시)
    """
    from src.logic.troop_service import TroopService
    
    troop_service = TroopService()
    try:
        db_manager = game_state["db_manager"]
        user_db_id = db_manager.get_or_create_user(request.user_id)
        
        result = troop_service.heal_all_champions(user_db_id)
        
        if "error" in result:
             raise HTTPException(status_code=400, detail=result["error"])
             
        return result
    finally:
        troop_service.close()

# =========================
# Army Management Endpoints
# =========================
class ArmyConfigRequest(BaseModel):
    user_id: str
    slot_index: int
    champion_ids: List[int]
    unit_type: str = "cavalry"

@app.get("/army/{user_id}")
async def get_user_armies(user_id: str):
    """
    유저의 모든 부대 구성 조회
    Returns: 슬롯별 배치된 챔피언 목록
    """
    from src.logic.army_service import ArmyService
    
    db_manager = game_state["db_manager"]
    user_db_id = db_manager.get_or_create_user(user_id)
    
    service = ArmyService()
    try:
        armies = service.get_user_armies(user_db_id)
        return {"user_id": user_id, "armies": armies}
    finally:
        service.close()

@app.post("/army/configure")
async def configure_army(request: ArmyConfigRequest):
    """
    부대 구성 저장/변경
    - slot_index: 0~4 (최대 5개 부대)
    - champion_ids: 배치할 챔피언 ID 목록 (최대 3명)
    - unit_type: 병종 (cavalry, spearman, archer, shieldman)
    """
    from src.logic.army_service import ArmyService
    
    db_manager = game_state["db_manager"]
    user_db_id = db_manager.get_or_create_user(request.user_id)
    
    service = ArmyService()
    try:
        result = service.save_army_configuration(
            user_id=user_db_id,
            slot_index=request.slot_index,
            champion_ids=request.champion_ids,
            unit_type=request.unit_type
        )
        return {"message": "부대 구성이 저장되었습니다.", **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        service.close()

@app.post("/army/deploy")
async def deploy_army_to_map(request: MarchRequest):
    """
    DB에 저장된 부대를 맵에 배치하고 행군 명령을 내림
    - user_id: 유저 ID
    - champion_key: 여기서는 slot_index로 사용 (정수형 문자열, 예: "0")
    - target_x, target_y: 목표 좌표
    """
    map_manager = game_state["map_manager"]
    db_manager = game_state["db_manager"]
    
    user_db_id = db_manager.get_or_create_user(request.user_id)
    
    try:
        slot_index = int(request.champion_key)
    except ValueError:
        raise HTTPException(status_code=400, detail="champion_key에 슬롯 번호(0~4)를 입력하세요.")
    
    # DB에서 부대 구성 로드 → 게임 로직 Army 객체 생성
    army = map_manager.deploy_army_from_db(user_db_id, slot_index)
    
    if not army:
        raise HTTPException(status_code=404, detail="해당 슬롯에 부대가 없거나 챔피언이 배치되지 않았습니다.")
    
    # 본진 설정 (임시로 (0, 0))
    army.set_position(0, 0)
    army.home_pos = (0, 0)
    
    # 행군 명령
    target_pos = (request.target_x, request.target_y)
    march = map_manager.send_march(army, target_pos)
    
    if not march:
        raise HTTPException(status_code=400, detail="해당 위치로 행군할 수 없습니다.")
    
    return {
        "message": "부대 출격!",
        "army_id": army.id,
        "champions": [c.name for c in army.champions],
        "target": target_pos,
        "arrival_time": march.arrival_time.isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
