from utils.buffType import BuffType
from classes.buff import Buff

# champions.py 처럼 버프 인스턴스 모음집

class AttackUpBuff(Buff):
    def __init__(self, value: float, duration: float):
        super().__init__(BuffType.ATK_UP, duration)
        self.value = value

    def apply_stats(self, stats):
        stats[1] += self.value
        return stats

