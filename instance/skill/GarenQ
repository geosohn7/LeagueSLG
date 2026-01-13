from classes.skill import Skill
from utils.buffType import BuffType

class GarenQ(Skill):
    def __init__(self):
        super().__init__("Decisive Strike")

    def cast(self, caster, target):

        caster.removeBuff(BuffType.SLOW)

        caster.addBuff(
            BuffType.SPEED,
            duration=3.0,
            value=0.35
        )

        target.addBuff(
            BuffType.SILENCE,
            duration=1.5
        )

        bonus_damage = 30 + caster.getStat("attack")
        print(f"Next attack bonus damage: {bonus_damage}")
