from src.logic.battle.battle import Battle
from src.common.report_generator import generate_report
from src.game.user import User
from src.db_manager import DatabaseManager
from src.logic.troop_service import TroopService
from src.logic.army_service import ArmyService
from src.logic.map_manager import MapManager
from src.models.world_map import WorldMap
from src.factories.champion_factory import create_champion
import webbrowser
import os

#  --- DB CODE --- #
from src.common.database import Base, engine
#  --- DB CODE --- #

def print_army_info(army):
    print(f"\n[Army: {army.id}] Unit Type: {army.unit_type}")
    for champ in army.champions:
        print(f"  - {champ.getName()} (Lv.{champ.level}) HP: {champ.getCurrHealth()}/{champ.max_hp}")

if __name__ == "__main__":
    # 0. Clean up old DB for Schema Update (Dev Mode)
    db_path = "db/game_data.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("🗑️ Old database removed for schema update.")
        except Exception as e:
            print(f"⚠️ Could not remove old database: {e}")

    # 1. DB Initialization
    Base.metadata.create_all(bind=engine)
    db_manager = DatabaseManager()
    
    # 2. User Setup
    print("--- 1. User Setup ---")
    user = User("Geo", db_manager) # Default: Gold 100, Silver 1000
    print(f"User: {user.username} (ID: {user.user_id})")
    
    # Show initial resources
    initial_info = db_manager.get_user_info(user.user_id)
    print(f"Initial Resources: Gold {initial_info['resources']['gold']} (Premium), Silver {initial_info['resources']['silver']} (Common)")

    # Add champions if missing
    if not user.champions:
        print("Adding default champions...")
        user.add_champion("Garen")
        user.add_champion("Darius")
        user.add_champion("Lux")
        user.add_champion("Ashe")
        # Reload to ensure we have the objects
        user = User("Geo", db_manager)

    # 2.5. Resource Management (Silver Mine)
    print("\n--- 2. Resource Management ---")
    from src.logic.resource_manager import ResourceManager
    resource_manager = ResourceManager(db_manager)
    
    # Simulate time passing (Silver Generation)
    # Force update last collection time to 1 hour ago
    import datetime
    user_obj = db_manager.get_or_create_user("Geo") # get ID
    # We need to hack the DB entry or just trust the manager collects from now.
    # Let's just manually add some silver to simulate mining for this test
    db_manager.update_user_resource(user.user_id, "silver", 500)
    print("⛏️  Mined 500 Silver from Silver Mine!")
    
    current_info = db_manager.get_user_info(user.user_id)
    print(f"Current Resources: Gold {current_info['resources']['gold']}, Silver {current_info['resources']['silver']}")

    # 3. Troop Management (Heal)
    print("\n--- 3. Troop Management ---")
    troop_service = TroopService()
    
    # Give some reserve troops for testing
    current_reserve = db_manager.update_user_troops(user.user_id, 5000)
    print(f"Current Reserve Troops: {current_reserve}")

    # Heal all champions
    heal_result = troop_service.heal_all_champions(user.user_id)
    print(f"Heal Result: {heal_result}")

    # 3.5. Champion Gacha (3 Types)
    print("\n--- 3.5. Champion Gacha (Silver/Gold/Pickup) ---")
    from src.logic.gacha_service import GachaService
    gacha_service = GachaService(db_manager)
    
    # Give full resources for testing
    db_manager.update_user_resource(user.user_id, "gold", 400) # Gold: 100(base) + 400 = 500
    db_manager.update_user_resource(user.user_id, "silver", 1000) # Silver: 1500 (1000 base + 500 mined) + 1000 = 2500
    
    # 1. Silver Gacha
    print(f"\n[Silver Gacha] Cost: 500 Silver")
    success, msg, result = gacha_service.pull_champion(user.user_id, "silver_gacha")
    if success:
        print(f"🎉 Result: {msg} (Rem Silver: {result['remaining_currency']})")
    
    # 2. Gold Gacha
    print(f"\n[Gold Gacha] Cost: 100 Gold")
    success, msg, result = gacha_service.pull_champion(user.user_id, "gold_gacha")
    if success:
         print(f"🎉 Result: {msg} (Rem Gold: {result['remaining_currency']})")

    # 3. Pickup Gacha
    print(f"\n[Pickup Gacha - Ahri/Katarina] Cost: 200 Gold")
    success, msg, result = gacha_service.pull_champion(user.user_id, "pickup_gacha")
    if success:
         print(f"🎉 Result: {msg} (Rem Gold: {result['remaining_currency']})")
    else:
         print(f"❌ Failed: {msg}")
    
    # 4. Army Configuration
    print("\n--- 3. Army Configuration ---")
    army_service = ArmyService()
    
    # Get user's champions to find IDs
    user_champs = db_manager.get_user_champions(user.user_id)
    garen_info = next((c for c in user_champs if c['champion_key'] == "Garen"), None)
    lux_info = next((c for c in user_champs if c['champion_key'] == "Lux"), None)
    ashe_info = next((c for c in user_champs if c['champion_key'] == "Ashe"), None)
    
    if garen_info and lux_info and ashe_info:
        # Assign Garen, Lux, Ashe to Army Slot 0
        army_config = army_service.save_army_configuration(
            user.user_id, 
            slot_index=0, 
            champion_ids=[garen_info['id'], lux_info['id'], ashe_info['id']],
            unit_type="archer" # Changed to Archer for testing
        )
        print(f"Army Configured: {army_config}")
    
    # 5. Deploy to Map
    print("\n--- 4. Deploy to Map ---")
    world_map = WorldMap(width=10, height=10) # Dummy map
    map_manager = MapManager(world_map)
    
    player_army = map_manager.deploy_army_from_db(user.user_id, slot_index=0)
    if not player_army:
        print("Failed to deploy army.")
        exit(1)
        
    print_army_info(player_army)

    # 6. Create Enemy Army (NPC)
    print("\n--- 5. Preparing Enemy ---")
    # 3v3 Enemy Team: Darius, Katarina, Draven (if Draven exists, else use Jhin/Caitlyn)
    # Checking json: Katarina exists. Draven not found. Use Jhin.
    enemy_keys = ["Darius", "Katarina", "Jhin"]
    enemy_champs = []
    
    for key in enemy_keys:
        champ = create_champion(key)
        champ.level = 3
        champ.recalculate_stats()
        champ.current_hp = champ.max_hp
        enemy_champs.append(champ)
    
    # Create NPC Army wrapper
    enemy_army = map_manager.create_army("NPC_Noxus", enemy_champs)
    enemy_army.unit_type = "cavalry" 
    
    print_army_info(enemy_army)

    # 7. Battle Simulation
    print("\n--- 6. Battle Start ---")
    battle = Battle(player_army, enemy_army)
    battle.start()

    # 8. Report & Save
    generate_report(battle, "reports/battle_report.html")
    print("\nReport generated: reports/battle_report.html")
    
    # Open report
    report_abs_path = os.path.abspath("reports/battle_report.html")
    webbrowser.open(f"file:///{report_abs_path}")
    
    # Save HP state (MapManager handles this typically, but here we run battle manually)
    # We need to manually invoke save because MapManager isn't managing the battle loop here
    print("\n--- 7. Saving State ---")
    map_manager._save_army_status(player_army)

    troop_service.close()
    army_service.close()