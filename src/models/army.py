from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.champion import Champion

class Army:
    """
    챔피언과 병력으로 구성된 부대 클래스.
    본 프로젝트에서는 챔피언의 HP가 곧 병력(Troops)을 의미합니다.
    """
    def __init__(self, army_id: str, owner_id: str, champion: 'Champion'):
        self.id = army_id
        self.owner_id = owner_id
        self.champion = champion
        self.home_pos = (0, 0) # 귀환할 본진 좌표
        
        # 현재 위치 (x, y) - 행군 중이 아닐 때 유효
        self.pos_x: Optional[int] = None
        self.pos_y: Optional[int] = None
        
        self.status = "IDLE"  # IDLE, MARCHING, STATIONED

    @property
    def troop_count(self) -> int:
        """챔피언의 현재 HP를 병력 수로 반환"""
        return int(self.champion.current_hp)

    @property
    def max_troop_count(self) -> int:
        """챔피언의 최대 HP를 최대 병력 수로 반환"""
        return int(self.champion.max_hp)

    def set_position(self, x: int, y: int):
        self.pos_x = x
        self.pos_y = y

    def is_alive(self) -> bool:
        """챔피언의 생존 여부가 곧 부대의 생존 여부"""
        return self.champion.is_alive()

    def take_losses(self, amount: int):
        """병력 손실 처리 (HP 감소)"""
        self.champion.take_damage(amount)

    def recover_troops(self, amount: int):
        """병력 보충 (HP 회복)"""
        self.champion.current_hp = min(self.champion.max_hp, self.champion.current_hp + amount)

    def __repr__(self):
        return f"Army({self.champion.name}, Troops: {self.troop_count}/{self.max_troop_count}, Status: {self.status})"
