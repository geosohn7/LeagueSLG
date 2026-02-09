from typing import Optional, TYPE_CHECKING, List
if TYPE_CHECKING:
    from src.models.champion import Champion

class Army:
    """
    챔피언과 병력으로 구성된 부대 클래스.
    최대 3명의 챔피언을 보유할 수 있으며, 각 챔피언의 HP가 곧 병력(Troops)을 의미합니다.
    """
    def __init__(self, army_id: str, owner_id: str, champions: List['Champion'], unit_type: str = "cavalry"):
        self.id = army_id
        self.owner_id = owner_id
        self.champions = champions[:3]  # 최대 3명으로 제한
        self.unit_type = unit_type  # 병종: cavalry, spearman, archer, shieldman
        self.home_pos = (0, 0) # 귀환할 본진 좌표
        
        # 현재 위치 (x, y) - 행군 중이 아닐 때 유효
        self.pos_x: Optional[int] = None
        self.pos_y: Optional[int] = None
        
        self.status = "IDLE"  # IDLE, MARCHING, STATIONED
        
        # 진영 시너지 적용
        self.apply_faction_synergy()

    def apply_faction_synergy(self):
        """
        3명의 챔피언이 모두 같은 진영이면 모든 스탯에 10% 버프 적용
        """
        if len(self.champions) != 3:
            return
        
        # 모든 챔피언의 진영 확인
        factions = [c.faction for c in self.champions]
        
        # 모두 같은 진영인지 확인 (None 제외)
        if len(set(factions)) == 1 and factions[0] != 'None':
            faction_name = factions[0]
            print(f"🔥 [{faction_name}] 진영 시너지 발동! 모든 스탯 +10%")
            
            # 모든 챔피언에게 10% 스탯 버프 적용
            for champion in self.champions:
                champion.addBuff("faction_synergy", duration=999, value=0.1)

    @property
    def troop_count(self) -> int:
        """모든 챔피언의 현재 HP 합계를 병력 수로 반환"""
        return sum(int(c.current_hp) for c in self.champions if c.is_alive())

    @property
    def max_troop_count(self) -> int:
        """모든 챔피언의 최대 HP 합계를 최대 병력 수로 반환"""
        return sum(int(c.max_hp) for c in self.champions)

    def set_position(self, x: int, y: int):
        self.pos_x = x
        self.pos_y = y

    def is_alive(self) -> bool:
        """최소 1명의 챔피언이 살아있으면 부대 생존"""
        return any(c.is_alive() for c in self.champions)
    
    def get_alive_champions(self) -> List['Champion']:
        """살아있는 챔피언 목록 반환"""
        return [c for c in self.champions if c.is_alive()]

    def take_losses(self, amount: int):
        """병력 손실 처리 - 살아있는 챔피언들에게 균등 분배"""
        alive = self.get_alive_champions()
        if not alive:
            return
        
        damage_per_champion = amount / len(alive)
        for champion in alive:
            champion.take_damage(damage_per_champion)

    def recover_troops(self, amount: int):
        """병력 보충 - 모든 챔피언에게 균등 분배"""
        if not self.champions:
            return
        
        heal_per_champion = amount / len(self.champions)
        for champion in self.champions:
            champion.current_hp = min(champion.max_hp, champion.current_hp + heal_per_champion)

    def __repr__(self):
        alive_count = len(self.get_alive_champions())
        factions = [c.faction for c in self.champions]
        faction_str = f" [{factions[0]}]" if len(set(factions)) == 1 and factions[0] != 'None' else ""
        unit_type_emoji = {"cavalry": "🐴", "spearman": "🔱", "archer": "🏹", "shieldman": "🛡️"}.get(self.unit_type, "⚔️")
        return f"Army({alive_count}/{len(self.champions)} Champions{faction_str}, {unit_type_emoji}{self.unit_type}, Troops: {self.troop_count}/{self.max_troop_count}, Status: {self.status})"
