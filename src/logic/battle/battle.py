from typing import List, TYPE_CHECKING
import random
from src.models.champion import Champion
from src.models.skill import Skill

if TYPE_CHECKING:
    from src.models.army import Army


class Battle:
    """
    3v3 배틀 시뮬레이터: 두 팀(각 최대 3명)의 전투 흐름을 조율
    병종 상성 시스템: 기병<창병<궁병<방패병<기병
    """
    # 병종 상성 정의: key가 value를 카운터함
    UNIT_COUNTERS = {
        "spearman": "cavalry",    # 창병 > 기병
        "archer": "spearman",     # 궁병 > 창병
        "shieldman": "archer",    # 방패병 > 궁병
        "cavalry": "shieldman"    # 기병 > 방패병
    }
    
    def __init__(self, left_army: 'Army', right_army: 'Army'):
        self.left_army = left_army
        self.right_army = right_army
        self.left_team = left_army.champions[:3]  # 최대 3명
        self.right_team = right_army.champions[:3]
        self.turn = 1
        self.history = []         # 전투 기록 저장
        self.winner_team = None   # 승리 팀 (left/right)
        
        # 병종 상성 버프/디버프 적용
        self.apply_unit_type_modifiers()

    def apply_unit_type_modifiers(self):
        """
        병종 상성에 따라 스탯 버프/디버프 적용
        A < B인 경우: A는 -20%, B는 +20%
        """
        left_type = self.left_army.unit_type
        right_type = self.right_army.unit_type
        
        # 같은 병종이면 상성 없음
        if left_type == right_type:
            return
        
        # 왼쪽이 오른쪽을 카운터하는지 확인
        if self.UNIT_COUNTERS.get(left_type) == right_type:
            # 왼쪽 승리: 왼쪽 +20%, 오른쪽 -20%
            print(f"⚔️ 병종 상성! {left_type} > {right_type}")
            for champ in self.left_team:
                champ.addBuff("unit_advantage", duration=999, value=0.2)
            for champ in self.right_team:
                champ.addBuff("unit_disadvantage", duration=999, value=0.2)
        # 오른쪽이 왼쪽을 카운터하는지 확인
        elif self.UNIT_COUNTERS.get(right_type) == left_type:
            # 오른쪽 승리: 오른쪽 +20%, 왼쪽 -20%
            print(f"⚔️ 병종 상성! {right_type} > {left_type}")
            for champ in self.right_team:
                champ.addBuff("unit_advantage", duration=999, value=0.2)
            for champ in self.left_team:
                champ.addBuff("unit_disadvantage", duration=999, value=0.2)

    def start(self):
        """전투를 시작하고 한 팀이 전멸할 때까지 루프를 실행"""
        left_names = ", ".join(c.name for c in self.left_team)
        right_names = ", ".join(c.name for c in self.right_team)
        self._log(f"교전 시작: [{left_names}] vs [{right_names}]")

        while self._both_teams_alive():
            self._log(f"\n[ 제 {self.turn} 합 ]")

            # 모든 살아있는 챔피언을 속도순으로 정렬
            all_champions = self._get_turn_order()

            # 각 챔피언이 순서대로 행동
            for champion in all_champions:
                if not champion.is_alive():
                    continue
                
                # 상대 팀 확인
                enemy_team = self.right_team if champion in self.left_team else self.left_team
                
                # 상대 팀이 전멸했으면 종료
                if not self._team_alive(enemy_team):
                    break
                
                # 턴 처리
                self._process_turn(champion, enemy_team)

            self.turn += 1

        self._finish()

    def _get_turn_order(self) -> List[Champion]:
        """모든 살아있는 챔피언을 SPD 순으로 정렬"""
        alive_champions = []
        for champion in self.left_team + self.right_team:
            if champion.is_alive():
                alive_champions.append(champion)
        
        # SPD 내림차순 정렬 (동률 시 랜덤)
        alive_champions.sort(key=lambda c: (c.getStat('SPD'), random.random()), reverse=True)
        return alive_champions

    def _both_teams_alive(self) -> bool:
        """양 팀 모두 최소 1명 이상 생존"""
        return self._team_alive(self.left_team) and self._team_alive(self.right_team)

    def _team_alive(self, team: List[Champion]) -> bool:
        """팀 내 최소 1명 생존 여부"""
        return any(c.is_alive() for c in team)

    def _get_alive_enemies(self, enemy_team: List[Champion]) -> List[Champion]:
        """살아있는 적 목록"""
        return [c for c in enemy_team if c.is_alive()]

    def _process_turn(self, actor: Champion, enemy_team: List[Champion]):
        """개별 챔피언의 턴 동작을 처리"""
        self._log(f"--- {actor.name}의 공세 ---")

        # 턴 시작 (버프 갱신)
        actor.on_turn_start()
        if not actor.is_alive():
            return

        # 타겟 선택: 살아있는 적 중 랜덤
        alive_enemies = self._get_alive_enemies(enemy_team)
        if not alive_enemies:
            return
        
        target = random.choice(alive_enemies)

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
        self._log(f"[{attacker.name}] {skill.name} 발동! → {defender.name}")
        old_hp = defender.current_hp
        skill.cast(self, attacker, defender)
        damage = old_hp - defender.current_hp
        self._log(f"   (잔여 병력: {defender.current_hp:.0f})")
        
        self.history.append({
            "turn": self.turn,
            "actor": attacker.name,
            "target": defender.name,
            "action": skill.name,
            "damage": round(damage, 0),
            "left_hp": sum(c.current_hp for c in self.left_team if c.is_alive()),
            "right_hp": sum(c.current_hp for c in self.right_team if c.is_alive())
        })

    def _basic_attack(self, attacker: Champion, defender: Champion):
        """일반 공격으로 데미지를 입힘 (공식: ATK * ATK / DEF)"""
        atk = attacker.getStat('ATK')
        df = defender.getStat('DEF')
        damage = (atk * atk) / max(1, df)
        defender.take_damage(damage)

        self._log(
            f"[{attacker.name}] 공격 → {defender.name} ({damage:.0f}명 손실, "
            f"잔여 병력: {defender.current_hp:.0f})"
        )

        self.history.append({
            "turn": self.turn,
            "actor": attacker.name,
            "target": defender.name,
            "action": "일반 공격",
            "damage": round(damage, 0),
            "left_hp": sum(c.current_hp for c in self.left_team if c.is_alive()),
            "right_hp": sum(c.current_hp for c in self.right_team if c.is_alive())
        })

    def _finish(self):
        """전투 종료 후 승자를 발표"""
        if self._team_alive(self.left_team):
            self.winner_team = "left"
            winners = self.left_team
            losers = self.right_team
        else:
            self.winner_team = "right"
            winners = self.right_team
            losers = self.left_team

        winner_names = ", ".join(c.name for c in winners if c.is_alive())
        self._log(f"\n최종 승자: {winner_names} (턴 수: {self.turn})")
        
        # 승리 팀 경험치 획득 (패배 팀의 평균 레벨 * 50)
        avg_loser_level = sum(c.level for c in losers) / max(1, len(losers))
        exp_gain = int(avg_loser_level * 50)
        
        for winner in winners:
            if winner.is_alive():
                winner.gain_exp(exp_gain)

    def _log(self, msg: str):
        """전투 상황을 콘솔에 출력"""
        print(msg)

