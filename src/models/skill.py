import random

class Skill:
    """
    스킬 베이스 클래스: 데이터 기반의 기본 동작과 로직을 정의
    """
    def __init__(self, skill_id: str, data: dict):
        self.id = skill_id
        self.name = data.get("name", skill_id)
        # 발동 확률 (0.0 ~ 1.0)
        self.prob = data.get("probability", 1.0)
        # 스킬 기본 위력 (공격력과 곱해짐)
        self.power = data.get("power", 0)
        # 스킬 데이터 전체 (버프 목록 등 포함)
        self.data = data

    def can_use(self, caster) -> bool:
        """
        침묵이나 기절 같은 CC 상태를 체크하여 사용 가능 여부를 반환
        """
        # 기절 혹은 침묵 상태라면 스킬 사용 불가
        if caster.is_stunned() or caster.is_silenced():
            return False
        return True

    def roll(self, caster) -> bool:
        """
        정해진 확률에 따라 스킬 발동 여부를 결정
        """
        return random.random() < self.prob
    
    def cast(self, battle, caster, target):
        """
        스킬의 실제 효과를 실행
        기본 구현은 데미지 계산, 버프 제거, 버프 자동 적용을 포함
        """
        # 1. 특정 버프 제거 (Cleanse 로직)
        # JSON 예시: "removes": ["slow"]
        removes = self.data.get("removes", [])
        for buff_id in removes:
            # 해당 버프가 있는지 확인
            has_buff = any(b.buff_id == buff_id for b in caster.buffs)
            if has_buff:
                caster.removeBuff(buff_id)
                battle._log(f"  {caster.name}의 {buff_id} 효과 제거")

        # 2. 데미지 계산 및 적용
        if self.power > 0:
            # 공식: (스킬 위력 * 시전자 공격력^2) / 대상 방어력
            atk = caster.getStat('ATK')
            df = target.getStat('DEF')
            damage = (self.power * (atk * atk)) / max(1, df)
            target.take_damage(damage)
            battle._log(f"→ {self.name} {damage:.1f} 데미지!")

        # 3. JSON에 정의된 버프 목록을 자동 적용
        buff_list = self.data.get("buffs", [])
        from src.factories.buff_factory import create_buff
        
        for b_data in buff_list:
            b_id = b_data.get("type")
            duration = b_data.get("duration", 1)
            # 버프 수치 계산용 계수 (예: 0.3 이면 30%)
            skill_coeff = b_data.get("value", 1.0)
            # 가중치를 받을 스탯 (기본값 주문력)
            scaling_stat = b_data.get("scaling_stat", "SPATK")
            b_target_type = b_data.get("target", "defender")
            
            # 팩토리를 통해 시전자 스탯이 반영된 동적 버프를 생성
            new_buff = create_buff(b_id, duration, caster, skill_coeff, scaling_stat)
            
            # 타겟팅 (defender: 상대방, attacker: 자기자신)
            actual_target = target if b_target_type == "defender" else caster
            actual_target.buffs.append(new_buff)
            actual_target.recalculate_stats()
            
            battle._log(f"  {actual_target.name}에게 {new_buff.buff_id} 적용 (효과: {new_buff.value:.2f}%)")
