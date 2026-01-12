from typing import List


class Champion:
    def __init__(self, name:str, stat:List[int]):
        self.name: str = name
        self.atk: int = stat[0]
        self.defs: int = stat[1]
        self.spatk: int = stat[2]
        self.spdefs: int = stat[3]
        self.spd: int = stat[4]