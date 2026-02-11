import unittest
from unittest.mock import MagicMock
from src.logic.gacha_service import GachaService

class TestGachaService(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.gacha = GachaService(self.mock_db)
        # Mock champion data
        self.gacha.champion_data = {
            "Garen": {"images": {}},
            "Lux": {"images": {}}
        }

    def test_pull_champion_success(self):
        # Setup: User has 1000 gold
        self.mock_db.get_user_info.return_value = {
            'resources': {'gold': 1000}
        }
        self.mock_db.update_user_resource.return_value = True

        # Execute
        success, msg, result = self.gacha.pull_champion(user_id=1)

        # Verify
        self.assertTrue(success)
        self.assertIn(result['name'], ["Garen", "Lux"])
        self.assertEqual(result['remaining_gold'], 900)
        
        # Verify DB calls
        self.mock_db.update_user_resource.assert_called_with(1, "gold", -100)
        self.mock_db.add_champion_to_user.assert_called()

    def test_pull_champion_not_enough_gold(self):
        # Setup: User has 50 gold
        self.mock_db.get_user_info.return_value = {
            'resources': {'gold': 50}
        }

        # Execute
        success, msg, result = self.gacha.pull_champion(user_id=1)

        # Verify
        self.assertFalse(success)
        self.assertIn("Not enough gold", msg)
        self.mock_db.update_user_resource.assert_not_called()

if __name__ == '__main__':
    unittest.main()
