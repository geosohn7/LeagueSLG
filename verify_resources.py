from src.common.database import Base, engine
from src.db_manager import DatabaseManager
from src.game.user import User
from src.logic.resource_manager import ResourceManager
from src.logic.gacha_service import GachaService
# Import models to ensure they are registered with Base
from src.models.army_model import ArmyDb
import os

def verify_resources():
    # 0. Clean DB
    db_path = "db/game_data.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("🗑️ DB Removed.")
        except:
            pass
    
    # 1. Init
    Base.metadata.create_all(bind=engine)
    db = DatabaseManager()
    
    # 2. User Setup
    user = User("Tester", db)
    info = db.get_user_info(user.user_id)
    print(f"Init: Gold {info['resources']['gold']}, Silver {info['resources']['silver']}")
    
    # 3. Silver Mining
    rm = ResourceManager(db)
    # Simulate mining (force update in DB or just use db manager to add)
    db.update_user_resource(user.user_id, "silver", 500)
    
    info = db.get_user_info(user.user_id)
    print(f"After Mining 500: Silver {info['resources']['silver']}")
    
    if info['resources']['silver'] == 1500: # 1000 + 500
        print("✅ Silver Mining Verified")
    else:
        print("❌ Silver Mining Failed")

    # 4. Gacha Tests
    gacha = GachaService(db)
    
    # 4.1. Silver Recruitment (Cost 500)
    print("\n--- Testing Silver Gacha ---")
    info = db.get_user_info(user.user_id)
    print(f"Current Silver: {info['resources']['silver']}")
    
    success, msg, res = gacha.pull_champion(user.user_id, "silver_gacha")
    if success:
         print(f"✅ Silver Gacha: {msg} (Rem: {res['remaining_currency']})")
    else:
         print(f"❌ Silver Gacha Failed: {msg}")

    # 4.2. Premium recruitment (Cost 100)
    print("\n--- Testing Premium Gacha ---")
    info = db.get_user_info(user.user_id)
    print(f"Current Gold: {info['resources']['gold']}")
    
    success, msg, res = gacha.pull_champion(user.user_id, "gold_gacha")
    if success:
         print(f"✅ Gold Gacha Verified: {msg} (Rem: {res['remaining_currency']})")
    else:
         print(f"❌ Gold Gacha Failed: {msg}")

    # 5. Insufficient Checks
    # Try Gold again (Should fail if 0)
    success, msg, res = gacha.pull_champion(user.user_id, "gold_gacha")
    if not success:
        print("✅ Insufficient Gold Check Verified")
    else:
        print("❌ Insufficient Gold Check Failed")

if __name__ == "__main__":
    verify_resources()
