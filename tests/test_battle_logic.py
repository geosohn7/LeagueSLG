import unittest
from unittest.mock import MagicMock
from src.logic.battle.battle import Battle
from src.models.champion import Champion
from src.models.skill import Skill
from src.models.army import Army

class TestBattleLogic(unittest.TestCase):

    def test_skill_and_basic_attack_chain(self):
        # Create mock champions
        attacker = Champion("Attacker", base_stat=[1000, 100, 10, 0, 10, 100]) # HP, ATK, DEF, AP, MR, SPD
        attacker.recalculate_stats()
        attacker.current_hp = 1000
        
        defender = Champion("Defender", base_stat=[1000, 10, 10, 0, 10, 100])
        defender.recalculate_stats()
        defender.current_hp = 1000

        # Mock Skill
        mock_skill = MagicMock(spec=Skill)
        mock_skill.name = "TestSkill"
        # Skill deals 100 damage
        def skill_effect(battle, user, target):
            target.take_damage(100)
        mock_skill.cast = MagicMock(side_effect=skill_effect)

        # Force skill activation
        attacker.skills = [mock_skill]
        attacker.roll_skills = MagicMock(return_value=mock_skill)

        # Create Armies
        left_army = MagicMock(spec=Army)
        left_army.champions = [attacker]
        left_army.unit_type = "infantry"
        
        right_army = MagicMock(spec=Army)
        right_army.champions = [defender]
        right_army.unit_type = "infantry"

        # Initialize Battle
        battle = Battle(left_army, right_army)
        
        # Capture HP before turn
        hp_before = defender.current_hp
        
        # Execute one turn for attacker
        battle._process_turn(attacker, [defender])
        
        # Verify Skill was used
        mock_skill.cast.assert_called_once()
        
        # Calculate expected damage
        # Skill Damage: 100
        # Basic Attack: (100 * 100) / 10 = 1000 damage
        # Total expected damage: 1100
        # Defender has 1000 HP, so should be dead (0 HP) or negative if logic allows
        
        expected_hp = 1000 - 100 - 1000 
        # Since take_damage uses max(0, current_hp - damage), it stops at 0.
        
        self.assertEqual(defender.current_hp, 0)
        
        # Check history has 2 entries (Skill + Basic Attack)
        # Note: Depending on Battle implementation, history might be appended twice.
        self.assertEqual(len(battle.history), 2)
        self.assertEqual(battle.history[0]['action'], "TestSkill")
        self.assertEqual(battle.history[1]['action'], "일반 공격")

if __name__ == '__main__':
    unittest.main()
