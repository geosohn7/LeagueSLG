from typing import List
from utils.stats import Stats
from classes.skill import Skill
from classes.buff import Buff
from utils.buffType import BuffType
# from systems.calculate_stats import apply_buffs
# from systems.calculate_stats import calculate_stats
import time


class Champion:
    # None = None 뭘 하려는지는 알겠는데, 그게 에러를 내고 있음
    def __init__(
            self, 
            name:str='',
            base_stat:List[int]=[],
            stat_growth:List[float]=[],
            level:int=1,
            minions:tuple[str, int]=('',0),
            skills:List[Skill]=[] 
    ):
        self.name: str = name
        self.base_stat = base_stat or [0,0,0,0,0,0]
        self.stat_growth = stat_growth or [0,0,0,0,0,0]
        self.level = level
        self.minion_type, self.minion_count = minions
        self.skill = skills or []
        self.buffs: list[Buff] = []
        

        self.recalculate_stats()
        self.hp: float = self.getStat('HP') or 0.0
        

    # I would rather add here if it keep gets the error
    def calculate_stats(self, base_stat, stat_growth, level):
        lv = level - 1
        return [
            int(base_stat[i] + stat_growth[i] * lv)
            for i in range(len(base_stat))
        ]


    def apply_buffs(self, stats, buffs):
        result = stats.copy()

        return result
    
    def recalculate_stats(self):
        before_buff = self.calculate_stats(
            self.base_stat,
            self.stat_growth,
            self.level
        )

        final = self.apply_buffs(before_buff, self.buffs)

        self.stat = {
            "HP": final[0],
            "ATK": final[1],
            "DEF": final[2],
            "SPATK": final[3],
            "SPDEF": final[4],
            "SPD": final[5],
        }

    # 스킬의 발동확률
    def roll_skills(self) -> Skill:
        for skill in self.skills:
            if not skill.can_use(self):
                continue
    
            if skill.roll(self):
                return skill



    # returns the name of champion
    def getName(self) -> str:
        return self.name

    # returns the tuple of minion type(str) and minion count(int) of current champinon
    def getMinion(self) -> tuple:
        return (self.minion_type, self.minion_count) 
    
    # returns the stat value based on string input of which stat is needed
    def getStat(self, name: str) -> float:
        return self.stat[name.upper()]
    
    def getCurrHealth(self) -> float:
        return self.hp

    # in-game logic methods (CC is part of Buff -- subset)
    def addBuff(self, buff_type:str, duration:float):
        self.buffs.append(Buff(buff_type, duration))

    def removeBuff(self, buff_type:str):
        self.buffs = [
            b for b in self.buffs
            if b.buff_type != buff_type
        ]
    
    def is_silenced(self) -> bool:
        return any(
            buff.buff_type == BuffType.SILENCE
            for buff in self.buffs
        )
    
    def is_stunned(self) -> bool:
        return any(
            buff.buff_type == BuffType.STUN
            for buff in self.buffs
        )

    def is_slowed(self) -> bool:
        return any(
            buff.buff_type == BuffType.SLOW
            for buff in self.buffs
        )
    
    def is_alive(self) -> bool:
        return self.hp > 0

    # hiddlen helpers
    #   it calculates the hp after damage taken and returns the remaining health
    def _take_damage(self, damage:float) -> float:
        self.hp = self.hp - damage
        return self.hp

    # main engine (run every frame/tick)
    def update(self):
        self.buffs = [buff for buff in self.buffs if not buff.is_expired()]
        self.recalculate_stats()
    # def update(self):
    #     self.buffs = [buff for buff in self.buffs if not buff.is_expired()]
    #     if len(self.buffs) != before:
    #         self.recalculate_stats()
