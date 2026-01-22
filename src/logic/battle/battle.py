from typing import List
from src.models.champion import Champion
from src.models.skill import Skill


class Battle:
    """
    배틀 시뮬레이터: 두 챔피언 간의 전투 흐름을 조율
    """
    def __init__(self, left: Champion, right: Champion):
        self.left = left
        self.right = right
        self.turn = 1
        self.history = [] # 전투 기록 저장

    def start(self):
        """전투를 시작하고 승자가 결정될 때까지 루프를 실행"""
        self._log(f"전투 시작: {self.left.name} vs {self.right.name}")

        while self._both_alive():
            self._log(f"\n[ 제 {self.turn} 턴 ]")

            # 속도(SPD)에 기반하여 턴 순서를 결정
            first, second = self._get_turn_order()

            # 첫 번째 행동자 처리
            self._process_turn(first, second)
            if not second.is_alive():
                break

            # 두 번째 행동자 처리
            self._process_turn(second, first)
            self.turn += 1

        self._finish()

    def _get_turn_order(self):
        """SPD 능력치를 비교하여 먼저 행동할 유닛을 정함. 동률일 경우 50% 확률로 결정"""
        left_speed = self.left.getStat('SPD')
        right_speed = self.right.getStat('SPD')

        if left_speed > right_speed:
            return self.left, self.right
        elif right_speed > left_speed:
            return self.right, self.left
        else:
            # 속도가 같을 경우 무작위 결정
            import random
            if random.random() < 0.5:
                return self.left, self.right
            else:
                return self.right, self.left

    def _both_alive(self) -> bool:
        """두 챔피언이 모두 살아있는지 확인"""
        return self.left.is_alive() and self.right.is_alive()

    def _process_turn(self, actor: Champion, target: Champion):
        """개별 유닛의 턴 동작을 처리 (턴 시작 -> 스킬/평타 -> 턴 종료)"""
        self._log(f"--- {actor.name}의 행동 ---")

        # 턴 시작 (버프 갱신)
        actor.on_turn_start()
        if not actor.is_alive():
            return

        # 스킬 확률 체크 및 시전
        skill = actor.roll_skills()
        if skill:
            self._use_skill(actor, target, skill)
        else:
            # 스킬 미발동 시 일반 공격
            self._basic_attack(actor, target)

        # 턴 종료 (지속시간 감소)
        actor.on_turn_end()

    def _use_skill(self, attacker: Champion, defender: Champion, skill: Skill):
        """스킬을 사용하고 결과를 로그에 남김"""
        self._log(f"[{attacker.name}] {skill.name} 시전!")
        old_hp = defender.current_hp
        skill.cast(self, attacker, defender)
        damage = old_hp - defender.current_hp
        self._log(f"   (HP: {defender.current_hp:.1f})")
        
        self.history.append({
            "turn": self.turn,
            "actor": attacker.name,
            "target": defender.name,
            "action": skill.name,
            "damage": round(damage, 1),
            "left_hp": round(self.left.current_hp, 1),
            "right_hp": round(self.right.current_hp, 1)
        })

    def _basic_attack(self, attacker: Champion, defender: Champion):
        """일반 공격으로 데미지를 입힘 (공식: ATK * ATK / DEF)"""
        atk = attacker.getStat('ATK')
        df = defender.getStat('DEF')
        damage = (atk * atk) / max(1, df)
        defender.take_damage(damage)

        self._log(
            f"[{attacker.name}] 일반 공격 → {damage:.1f} 데미지 "
            f"(HP: {defender.current_hp:.1f})"
        )

        self.history.append({
            "turn": self.turn,
            "actor": attacker.name,
            "target": defender.name,
            "action": "일반 공격",
            "damage": round(damage, 1),
            "left_hp": round(self.left.current_hp, 1),
            "right_hp": round(self.right.current_hp, 1)
        })

    def _finish(self):
        """전투 종료 후 승자를 발표"""
        winner = self.left if self.left.is_alive() else self.right
        self._log(f"\n최종 승자: {winner.name} (턴 수: {self.turn})")
        
        # 승리 시 경험치 획득 (패배자의 레벨 * 50)
        loser = self.right if winner == self.left else self.left
        exp_gain = loser.level * 50
        winner.gain_exp(exp_gain)

    def _log(self, msg: str):
        """전투 상황을 콘솔에 출력"""
        print(msg)
