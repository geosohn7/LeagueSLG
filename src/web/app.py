from flask import Flask, render_template, jsonify, request
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.common.database import Base, engine
from src.db_manager import DatabaseManager
from src.game.user import User
from src.logic.gacha_service import GachaService
from src.logic.resource_manager import ResourceManager
from src.logic.map_manager import MapManager
from src.models.world_map import WorldMap
from src.models.building import BuildingType
from src.models.army_model import ArmyDb
from src.factories.champion_factory import create_champion
import os

app = Flask(__name__)

# Initialize DB and Services
Base.metadata.create_all(bind=engine)
db_manager = DatabaseManager()
gacha_service = GachaService(db_manager)
resource_manager = ResourceManager(db_manager)

# Initialize Map (10x10)
world_map = WorldMap(width=10, height=10)
map_manager = MapManager(world_map)

# Hardcoded user for demo
DEMO_USERNAME = "Geo"
user_id = db_manager.get_or_create_user(DEMO_USERNAME)

# Place Main Castle if not exists
has_castle = False
for y in range(world_map.height):
    for x in range(world_map.width):
        tile = world_map.get_tile(x, y)
        if tile.building and tile.building.type == BuildingType.MAIN_CASTLE and tile.building.owner_id == user_id:
            has_castle = True
            break
    if has_castle: break

if not has_castle:
    # Try to place at (1,1) or find empty spot
    if world_map.can_place_building(BuildingType.MAIN_CASTLE, (1, 1)):
        world_map.place_building(BuildingType.MAIN_CASTLE, user_id, (1, 1))
    else:
        # Simple fallback search
        for y in range(world_map.height):
             for x in range(world_map.width):
                 if world_map.place_building(BuildingType.MAIN_CASTLE, user_id, (x, y)):
                     break

@app.route('/')
def index():
    return render_template('gacha.html')

@app.route('/map')
def map_view():
    return render_template('map.html')

@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    info = db_manager.get_user_info(user_id)
    if not info:
        return jsonify({"error": "User not found"}), 404
    return jsonify(info)

@app.route('/api/gacha/pull', methods=['POST'])
def pull_champion():
    data = request.json
    gacha_type = data.get('gacha_type', 'gold_gacha')
    
    success, msg, result = gacha_service.pull_champion(user_id, gacha_type)
    
    if success:
        return jsonify({
            "success": True,
            "message": msg,
            "result": result
        })
    else:
        return jsonify({
            "success": False,
            "message": msg
        }), 400

@app.route('/api/mine/collect', methods=['POST'])
def collect_silver():
    # Simulate mining for demo
    amount = resource_manager.collect_silver(user_id)
    # If amount is 0 (due to time limit), let's cheat for demo
    if amount == 0:
        db_manager.update_user_resource(user_id, "silver", 100)
        amount = 100
        
    return jsonify({
        "success": True,
        "amount": amount,
        "message": f"은전 {amount}개를 채굴했습니다!"
    })

# --- Map APIs ---

@app.route('/api/map/data', methods=['GET'])
def get_map_data():
    # 1. Ensure User has an Army (Create Dummy if needed)
    armies = map_manager.get_user_armies(user_id)
    if not armies:
        # 주몽을 기본 영웅으로 하는 부대 생성
        jumong = create_champion("주몽")
        jumong.level = 1
        jumong.recalculate_stats()
        jumong.reset_status()
        new_army = map_manager.create_army(user_id, [jumong])
        new_army.set_position(1, 1) # 성 위치에서 시작
        armies = [new_army]

    # 2. Serialize Tiles
    tiles_data = []
    for y in range(world_map.height):
        row = []
        for x in range(world_map.width):
            tile = world_map.get_tile(x, y)
            row.append({
                "x": x, "y": y,
                "type": tile.category.value,
                "level": tile.level,
                "resource": tile.res_type.value if tile.res_type else None
            })
        tiles_data.append(row)

    # 3. Serialize Armies
    armies_data = []
    # Player Armies
    for army in armies:
        armies_data.append({
            "id": army.id,
            "owner": "player",
            "x": army.pos_x,
            "y": army.pos_y,
            "name": f"Army ({army.troop_count})"
        })
    
    # NPC/Other Armies (from map_manager.armies dict)
    for army_id, army in map_manager.armies.items():
        if army.owner_id != user_id and army.is_alive() and army.pos_x is not None:
             armies_data.append({
                "id": army.id,
                "owner": "enemy",
                "x": army.pos_x,
                "y": army.pos_y,
                "name": "Enemy"
            })

    return jsonify({
        "width": world_map.width,
        "height": world_map.height,
        "tiles": tiles_data,
        "armies": armies_data
    })

@app.route('/api/map/march', methods=['POST'])
def march_army():
    data = request.json
    target_x = data.get('x')
    target_y = data.get('y')
    
    # Get player's first army for now
    armies = map_manager.get_user_armies(user_id)
    if not armies:
        return jsonify({"success": False, "message": "가용한 부대가 없습니다."}), 400
    
    my_army = armies[0]
    
    # Simple Teleport for Web Demo (Real march logic is async)
    # We will simulate instant arrival here to make UI responsive
    my_army.set_position(target_x, target_y)
    
    return jsonify({
        "success": True,
        "message": f"부대가 ({target_x}, {target_y})로 행군을 완료했습니다.",
        "new_pos": {"x": target_x, "y": target_y}
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
