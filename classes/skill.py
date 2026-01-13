from abc import ABC, abstractmethod

class Skill(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def cast(self, caster, target=None):
        pass

# usage:
# class GarenQ(Skill):
#     def __init__(self):
#         super().__init__("Decisive Strike")

#     def cast(self, caster, target):
#         # 1. 둔화 제거
#         caster.remove_cc("slow")

#         # 2. 이동속도 증가
#         caster.add_buff("move_speed", percent=35, duration=3)

#         # 3. 다음 기본 공격 강화
#         caster.empower_next_attack(
#             bonus_damage=30 + caster.stat[0],  # 예시
#             silence_duration=1.5
#         )
