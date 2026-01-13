from typing import List
from utils.stats import Stats
from classes.skill import Skill
from classes.buff import Buff
from utils.buffType import BuffType
import time


class Champion:
    def __init__(
        self, 
        name:str='', 
        stat:List[int]=[0,0,0,0,0], 
        minions:tuple[str, int]=('',0),
        skill:List[Skill]=[]
    ):
        self.name: str = name
        self.stat: List[int] = stat
        self.minion_type, self.minion_count = minions
        self.skills = skill
        self.buffs: list[Buff] = []

    # returns the name of champion
    def getName(self) -> str:
        return self.name

    # returns the tuple of minion type(str) and minion count(int) of current champinon
    def getMinion(self) -> tuple:
        return (self.minion_type, self.minion_count) 
    
    # returns the stat value based on string input of which stat is needed
    def getStat(self, lfstat:str) -> int:
        stat_enum = Stats[lfstat.upper()]
        return self.stat[stat_enum.value]

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


    # main engine (run every frame/tick)
    def update(self):
        self.buffs = [buff for buff in self.buffs if not buff.is_expired()]
