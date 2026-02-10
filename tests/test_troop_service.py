import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.common.database import Base
from src.models.user import User
from src.models.user_champion import UserChampion
from src.models.army_model import ArmyDb
from src.logic.troop_service import TroopService

class TestTroopService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.db = SessionLocal()
        self.service = TroopService(self.db)

        # Setup User with max troops
        self.user = User(username="test_user", reserve_troops=1000)
        self.db.add(self.user)
        self.db.commit()

        # Setup Champion (HP 0)
        self.champ = UserChampion(user_id=self.user.id, champion_key="Garen", level=1, current_hp=0)
        self.db.add(self.champ)
        self.db.commit()
        self.db.refresh(self.champ)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_assign_troops_success(self):
        # Assign 500 troops
        success, msg, new_hp = self.service.assign_troops(self.user.id, self.champ.id, 500)
        self.assertTrue(success)
        self.assertEqual(new_hp, 500)
        
        # Verify DB
        self.db.refresh(self.user)
        self.db.refresh(self.champ)
        self.assertEqual(self.user.reserve_troops, 500)
        self.assertEqual(self.champ.current_hp, 500)

    def test_assign_troops_not_enough_reserve(self):
        # Set reserve to 10 troops
        self.user.reserve_troops = 10
        self.db.commit()

        # Try to assign 2000 troops (need ~600, have 10)
        success, msg, new_hp = self.service.assign_troops(self.user.id, self.champ.id, 2000)
        self.assertFalse(success)
        self.assertIn("Not enough reserve troops", msg)
        self.assertEqual(self.champ.current_hp, 0)

    def test_assign_troops_full_hp(self):
        # Fill HP first (Garen lv1 max HP ~600)
        # Let's say max hp is not easily mocked without stat logic.
        # But Garen base HP is around 600.
        self.service.assign_troops(self.user.id, self.champ.id, 500)
        
        # Try to assign more (should cap at max)
        # We need to know max hp.
        from src.factories.champion_factory import create_champion
        max_hp = create_champion("Garen").max_hp
        
        # Assign remaining needed
        needed = max_hp - 500
        success, msg, new_hp = self.service.assign_troops(self.user.id, self.champ.id, needed + 100)
        
        self.assertTrue(success) # It succeeds by capping amount
        self.assertEqual(new_hp, max_hp)
        
        # Verify reserve consumed only needed amount
        self.db.refresh(self.user)
        self.assertEqual(self.user.reserve_troops, 1000 - 500 - needed)

    def test_heal_all_champions(self):
        # Create another champion (HP 0)
        champ2 = UserChampion(user_id=self.user.id, champion_key="Lux", level=1, current_hp=0)
        self.db.add(champ2)
        self.db.commit()
        
        # User has 1000 reserve. Garen needs ~600, Lux needs ~something.
        # Heal all
        result = self.service.heal_all_champions(self.user.id)
        
        self.assertEqual(result["healed_count"], 2)
        self.assertTrue(result["total_consumed"] > 0)
        
        # Verify both have full HP (or near full if reserve ran out, but 1000 should be enough for lv1s)
        # Garen Lv1 ~620, Lux Lv1 ~500. Total ~1120. Reserve 1000.
        # One might not be fully healed.
        
        self.db.refresh(self.champ)
        self.db.refresh(champ2)
        
        # Check if at least some healing happened
        self.assertTrue(self.champ.current_hp > 0)
        self.assertTrue(champ2.current_hp > 0)
        self.assertEqual(self.user.reserve_troops, 0) # Should consume all

if __name__ == '__main__':
    unittest.main()
