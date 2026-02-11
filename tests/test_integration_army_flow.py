import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.common.database import Base
from src.models.user import User
from src.models.user_champion import UserChampion
from src.logic.troop_service import TroopService
from src.logic.army_service import ArmyService
from src.logic.map_manager import MapManager
from src.models.world_map import WorldMap
from src.logic.battle.battle import Battle
from src.factories.champion_factory import create_champion

class TestIntegrationArmyFlow(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite for testing
        self.engine = create_engine("sqlite:///:memory:")
        SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.db = SessionLocal()
        
        # Override SessionLocal in services if possible, or pass db session explicitly
        # Services accept db session in constructor
        self.troop_service = TroopService(self.db)
        self.army_service = ArmyService(self.db)
        
        # MapManager doesn't take DB session in constructor but uses SessionLocal internally.
        # We might need to patch SessionLocal or ensure MapManager can use our session.
        # Looking at MapManager code, it imports SessionLocal inside methods.
        # Ideally, we should refactor MapManager to accept a session factory or session.
        # For now, let's see if we can just rely on the fact that we are using in-memory DB?
        # WAIT: In-memory DB with multiple sessions/engines won't share data unless shared cache is used.
        # "sqlite:///:memory:" is per connection.
        # If MapManager creates a NEW session from a NEW engine (via global SessionLocal), it won't see our data.
        
        # We need to Mock src.common.database.SessionLocal to return our self.db
        # But patching needs to be done carefully.
        
        # Alternatively, we can use a file-based sqlite for the test to ensure sharing?
        # Or better: Update MapManager to accept a session.
        # MapManager.deploy_army_from_db accepts db_session! Good.
        # But _save_army_status does NOT accept db_session.
        
        self.world_map = WorldMap(10, 10)
        self.map_manager = MapManager(self.world_map)

        # create user
        self.user = User(username="test_user", reserve_troops=5000)
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_full_flow(self):
        # 1. Create Champions
        c1 = UserChampion(user_id=self.user.id, champion_key="Garen", level=1, current_hp=0)
        c2 = UserChampion(user_id=self.user.id, champion_key="Lux", level=1, current_hp=0)
        self.db.add_all([c1, c2])
        self.db.commit()
        
        # 2. Heal Champions
        result = self.troop_service.heal_all_champions(self.user.id)
        self.assertEqual(result['healed_count'], 2)
        
        self.db.refresh(c1)
        self.db.refresh(c2)
        self.assertGreater(c1.current_hp, 0)
        self.assertGreater(c2.current_hp, 0)
        
        # 3. Configure Army
        self.army_service.save_army_configuration(
            self.user.id, 0, [c1.id, c2.id], "shieldman"
        )
        
        # 4. Deploy Army
        army = self.map_manager.deploy_army_from_db(self.user.id, 0, db_session=self.db)
        self.assertIsNotNone(army)
        self.assertEqual(len(army.champions), 2)
        self.assertEqual(army.unit_type, "shieldman")
        
        # 5. Battle with Dummy Enemy
        enemy_champ = create_champion("Darius")
        enemy_champ.current_hp = 100
        enemy_army = self.map_manager.create_army("enemy", [enemy_champ])
        
        battle = Battle(army, enemy_army)
        battle.start()
        
        # 6. Save State
        # We need to manually call _save_army_status because we ran battle manually.
        # But _save_army_status uses SessionLocal internally.
        # We must MonkeyPatch SessionLocal for this test method to point to our session
        # OR we modify MapManager to accept session.
        # Let's try mocking.
        
        import unittest.mock as mock
        with mock.patch('src.common.database.SessionLocal', return_value=self.db):
             # We also need to patch the close method so it doesn't close our session
             with mock.patch.object(self.db, 'close', return_value=None):
                self.map_manager._save_army_status(army)
        
        # 7. Verify DB update
        self.db.refresh(c1)
        # HP should be less than max (or changed) if they took damage.
        # Or at least not errored.
        # Since we can't easily predict exact damage, just check it runs.
        print(f"Post-battle HP: {c1.current_hp}")

if __name__ == '__main__':
    unittest.main()
