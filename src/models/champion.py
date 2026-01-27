from typing import List
from src.models.skill import Skill
from src.models.buff import Buff

class Champion:
    """
    챔피언 클래스: 능력치 관리, 스킬 시전, 버프 효과 적용 등 담당
    """
    def __init__(
            self, 
            name: str = '',
            base_stat: List[int] = [],
            stat_growth: List[float] = [],
            level: int = 1,
            exp: int = 0,
            minions: tuple[str, int] = ('', 0),
            skills: List[Skill] = [],
            image: dict = {}
    ):
        self.name: str = name
        self.images: dict = image or {}
        # 능력치 순서: [HP, ATK, DEF, SPATK, SPDEF, SPD]
        self.base_stat = base_stat or [0, 0, 0, 0, 0, 0]
        self.stat_growth = stat_growth or [0, 0, 0, 0, 0, 0]
        self.level = level
        self.exp = exp
        self.minion_type, self.minion_count = minions
        self.skills = skills or []
        self.buffs: list[Buff] = []
        # 장착 아이템 목록 (최대 3개)
        self.items: list = []
        self.MAX_ITEMS = 3

        # 초기 능력치 계산
        self.recalculate_stats()

        # 현재 체력 설정 (기본 스탯의 HP 기준)
        self.max_hp = base_stat[0]
        self.current_hp = self.max_hp

    def reset_status(self):
        """
        챔피언의 상태를 초기화 (HP 풀회복 및 모든 버프 제거)
        """
        self.current_hp = self.max_hp
        self.buffs = []
        # 아이템은 기본적으로 유지한다. 필요 시 아이템 제거 로직을 호출하세요.
        self.recalculate_stats()

    def calculate_stats(self, base_stat, stat_growth, level):
        """
        레벨에 따른 기본 능력치 계산 (공식: 베이스 + 성장치 * (레벨-1))
        """
        lv = level - 1
        return [
            int(base_stat[i] + stat_growth[i] * lv)
            for i in range(len(base_stat))
        ]

    def apply_buffs(self, stats, buffs):
        """
        현재 챔피언에게 걸린 버프들을 순회하며 최종 능력치에 반영
        """
        result = stats.copy()
        for buff in buffs:
            if buff.is_expired():
                continue
            result = buff.apply_stats(result)
        return result
    
    def recalculate_stats(self):
        """
        레벨업이나 버프 변경 시 호출되어 현재 능력치(self.stat)를 갱신
        """
        before_buff = self.calculate_stats(
            self.base_stat,
            self.stat_growth,
            self.level
        )
        final = self.apply_buffs(before_buff, self.buffs)
        
        # 가독성을 위해 사전(dict) 형태로 저장
        self.stat = {
            "HP": final[0],
            "ATK": final[1],
            "DEF": final[2],
            "SPATK": final[3],
            "SPDEF": final[4],
            "SPD": final[5],
        }

    def roll_skills(self) -> Skill:
        """
        챔피언의 스킬들을 확률에 따라 체크하고, 발동된 스킬을 반환
        """
        for skill in self.skills:
            if not skill.can_use(self):
                continue
            if skill.roll(self):
                return skill
        return None

    def take_damage(self, amount: float):
        """
        데미지를 입고 현재 체력을 감소시킴
        """
        self.current_hp = max(0, self.current_hp - amount)
        return self.current_hp

    def getName(self) -> str:
        return self.name

    def getMinion(self) -> tuple:
        return (self.minion_type, self.minion_count) 
    
    def getStat(self, name: str) -> float:
        """
        특정 능력치 이름을 입력받아 현재 값을 반환 (예: 'ATK', 'SPD')
        """
        return self.stat[name.upper()]
    
    def getCurrHealth(self) -> float:
        return self.current_hp

    def addBuff(self, buff_id: str, duration: int, value: float | None = None):
        """
        새로운 버프를 추가 (duration은 턴 단위 정수)
        """
        self.buffs.append(Buff(buff_id, duration, value))
        self.recalculate_stats() # 능력치를 즉시 반영

    def removeBuff(self, buff_id: str):
        """
        특정 ID의 버프를 즉시 제거
        """
        self.buffs = [
            b for b in self.buffs
            if b.buff_id != buff_id
        ]
        self.recalculate_stats()
    
    def is_silenced(self) -> bool:
        """침묵 상태 여부 확인 (스킬 사용 불가)"""
        return any(buff.buff_id == "silence" for buff in self.buffs)
    
    def is_stunned(self) -> bool:
        """기절 상태 여부 확인 (행동 불가)"""
        return any(buff.buff_id == "stun" for buff in self.buffs)

    def is_slowed(self) -> bool:
        """둔화 상태 여부 확인 (이동 속도 감소)"""
        return any(buff.buff_id == "slow" for buff in self.buffs)
    
    def is_alive(self) -> bool:
        """생존 여부 확인"""
        return self.current_hp > 0

    def update(self):
        """만료된 버프를 제거하고 능력치를 재계산"""
        self.buffs = [buff for buff in self.buffs if not buff.is_expired()]
        self.recalculate_stats()

    def on_turn_start(self):
        """턴이 시작될 때 호출 (버프 갱신 등)"""
        self.update()

    def on_turn_end(self):
        """턴이 종료될 때 호출. 버프의 지속 턴수를 감소시킴"""
        for buff in self.buffs:
            buff.tick()
        self.update()

    def gain_exp(self, amount: int):
        """경험치를 획득하고 필요 시 레벨업 수행"""
        self.exp += amount
        print(f"[{self.name}] {amount} 경험치 획득! (현재: {self.exp})")
        
        while self.exp >= self.get_required_exp():
            self.level_up()

    def get_required_exp(self) -> int:
        """현재 레벨에서 다음 레벨로 가기 위해 필요한 경험치 (공식: level * level * 100)"""
        return self.level * self.level * 100

    def level_up(self):
        """레벨업 처리 및 능력치 재계산"""
        self.exp -= self.get_required_exp()
        self.level += 1
        print(f"[{self.name}] 레벨업! {self.level-1} -> {self.level}")
        self.recalculate_stats()
        # 레벨업 시 HP 완전 회복
        self.max_hp = self.stat["HP"]
        self.current_hp = self.max_hp

    # -----------------------
    # Item management methods
    # -----------------------
    def equip_item(self, item):
        """
        아이템을 장착: 최대 `MAX_ITEMS` 까지 허용.
        - item은 객체 또는 문자열(item_id)를 허용.
        - 객체인 경우 해당 객체의 `apply_on_equip(self)`를 호출.
        """
        # lazy import to avoid circular dependency
        from src.factories import item_factory

        # item_id 문자열이 주어지면 객체로 변환
        if isinstance(item, str):
            item = item_factory.create_item(item)

        if len(self.items) >= self.MAX_ITEMS:
            raise ValueError(f"Cannot equip more than {self.MAX_ITEMS} items")

        # 장착 전 행동(아이템이 제공하는 stat 보정 등 적용)
        try:
            item.apply_on_equip(self)
        except Exception:
            # 아이템이 해당 메서드를 구현하지 않으면 무시
            pass

        self.items.append(item)
        # 능력치 재계산
        try:
            self.recalculate_stats()
        except Exception:
            pass

        return True

    def unequip_item(self, item_identifier):
        """
        아이템 해제: item_identifier는 item 객체, item id(str), 또는 인덱스(int)를 허용.
        제거 시 item.remove_on_unequip(self) 를 호출합니다(구현되어 있다면).
        """
        target = None
        # 찾기: 객체
        if item_identifier in self.items:
            target = item_identifier
        else:
            # 문자열 id로 매칭
            if isinstance(item_identifier, str):
                for it in self.items:
                    if getattr(it, "id", None) == item_identifier or getattr(it, "name", None) == item_identifier:
                        target = it
                        break
            # 인덱스로 접근
            if target is None and isinstance(item_identifier, int):
                if 0 <= item_identifier < len(self.items):
                    target = self.items[item_identifier]

        if target is None:
            raise ValueError("Item to unequip not found")

        # 제거 전 아이템 역효과
        try:
            target.remove_on_unequip(self)
        except Exception:
            pass

        self.items = [it for it in self.items if it is not target]
        try:
            self.recalculate_stats()
        except Exception:
            pass

        return True

    def get_items(self):
        """현재 장착된 아이템 리스트 반환"""
        return list(self.items)