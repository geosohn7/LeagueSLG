import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.common.database import Base
from src.models.user import User
from src.models.user_champion import UserChampion
from src.models.army_model import ArmyDb
from src.logic.army_service import ArmyService

class TestArmyService(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite for testing
        self.engine = create_engine("sqlite:///:memory:")
        SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.db = SessionLocal()
        self.army_service = ArmyService(self.db)

        # Setup User
        self.user = User(username="test_user")
        self.db.add(self.user)
        self.db.commit()

        # Setup Champions
        self.champions = []
        for i in range(5):
            champ = UserChampion(user_id=self.user.id, champion_key=f"Champ_{i}")
            self.db.add(champ)
            self.champions.append(champ)
        self.db.commit()
        # Refresh to get IDs
        for c in self.champions:
            self.db.refresh(c)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_save_army_configuration(self):
        # Army 1: Add 2 champions
        champ_ids = [self.champions[0].id, self.champions[1].id]
        self.army_service.save_army_configuration(self.user.id, 0, champ_ids, "archer")
        
        # Verify
        armies = self.army_service.get_user_armies(self.user.id)
        self.assertEqual(len(armies), 1)
        self.assertEqual(len(armies[0]['champions']), 2)
        self.assertEqual(armies[0]['unit_type'], "archer")

    def test_max_champions_per_army(self):
        # Try to add 4 champions (Should fail)
        champ_ids = [c.id for c in self.champions[:4]]
        with self.assertRaises(ValueError):
            self.army_service.save_army_configuration(self.user.id, 0, champ_ids)

    def test_max_armies_limit(self):
        # Try to add army to slot 5 (Should fail, range 0-4)
        with self.assertRaises(ValueError):
            self.army_service.save_army_configuration(self.user.id, 5, [])

    def test_champion_redeployment(self):
        # Add Champ 0 to Army 0
        self.army_service.save_army_configuration(self.user.id, 0, [self.champions[0].id])
        
        # Add Champ 0 to Army 1 (Should affect Army 0)
        self.army_service.save_army_configuration(self.user.id, 1, [self.champions[0].id])
        
        # Verify Army 0 is empty
        # Checking logic: Army 0 still exists but has 0 champions?
        # get_user_armies returns list of armies.
        armies = self.army_service.get_user_armies(self.user.id)
        # We expect 2 armies now (slot 0 and slot 1)
        self.assertEqual(len(armies), 2)
        
        army0 = next(a for a in armies if a['slot_index'] == 0)
        army1 = next(a for a in armies if a['slot_index'] == 1)
        
        self.assertEqual(len(army0['champions']), 0)
        self.assertEqual(len(army1['champions']), 1)
        self.assertEqual(army1['champions'][0]['id'], self.champions[0].id)

if __name__ == '__main__':
    unittest.main()
