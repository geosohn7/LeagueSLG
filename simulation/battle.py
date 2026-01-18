from typing import List
from classes.champion import Champion
from classes.skill import Skill


class Battle:
    def __init__(self, left: Champion, right: Champion):
        self.left = left
        self.right = right
        self.turn: int = 1
        self.log: List[str] = []

    # ------------------------
    # Battle lifecycle
    # ------------------------
    def start(self):
        self._log(f"Battle Start: {self.left.name} vs {self.right.name}")

        while self._both_alive():
            self._log(f"\n[ Turn {self.turn} ]")

            self._process_turn(self.left, self.right)
            if not self.right.is_alive():
                break

            self._process_turn(self.right, self.left)
            self.turn += 1

        self._finish()
    
    def _both_alive(self, left:Champoin, right:Champion) -> bool:
        return left.is_alive() and right.is_alive()

    # ------------------------
    # Turn
    # ------------------------
    def _process_turn(self, actor: Champion, target: Champion):
        self._log(f"{actor.name}'s turn")

        actor.on_turn_start()
        if not actor.is_alive():
            return

        skill=actor.roll_skills()

        if skill:
            self._use_skill(actor, target, skill)

        self._basic_attack(actor, target)

        actor.on_turn_end()
        target.on_turn_end()

    # ------------------------
    # Action
    # ------------------------
    def _use_skill(self, attacker: Champion, defender: Champion, skill: Skill):
        self._log(
            f"{attacker.name} uses {skill.name}!"
        )

        skill.cast(self,attacker,defender)

        self._log(
            #f"→ {skill.damage} damage "  --> this one need to be done with cast() method
            f"(HP: {defender.getStat('HP')})"
        )
        
    def _basic_attack(self, attacker: Champion, defender: Champion):
        damage = max(
            0,
            attacker.getStat('ATK') - defender.getStat('DEF')
        )

        defender.take_damage(damage)

        self._log(
            f"{attacker.name} attacks {defender.name} "
            f"→ {damage} damage "
            f"(HP: {defender.current_hp})"
        )
    

    # ------------------------
    # Finish
    # ------------------------
    def _finish(self):
        winner = self.left

    # ------------------------
    # Log
    # ------------------------
    def _log(self, msg: str):
        print(msg)
    