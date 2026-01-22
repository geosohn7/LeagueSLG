from src.logic.effects.buff_effects import apply_buff_to_stats

class Buff:
    """
    버프 클래스: 시간(턴)이 지남에 따라 만료되고 능력치에 영향을 주는 효과
    """
    def __init__(
        self,
        buff_id: str,
        duration: int,
        value: float | None = None
    ):
        # 버프 식별 ID (예: 'slow', 'speed')
        self.buff_id = buff_id
        # 계산된 버프 위력 (% 수치)
        self.value = value
        # 남은 지속 턴수
        self.remaining_turns = duration

    def is_expired(self) -> bool:
        """버프 만료 여부를 확인"""
        return self.remaining_turns <= 0

    def tick(self):
        """턴 종료 시 지속 시간을 1 감소시킴"""
        if self.remaining_turns > 0:
            self.remaining_turns -= 1

    def apply_stats(self, stats):
        """
        주어진 능력치 리스트에 이 버프의 효과(BUFF_EFFECTS)를 적용하여 반환
        """
        # instance/buff_effects.py 에 정의된 로직을 호출
        return apply_buff_to_stats(self.buff_id, stats, self.value)
