from datetime import datetime, timedelta
from enum import Enum
from typing import Tuple, List, Optional
from src.models.army import Army
import math

class MarchStatus(Enum):
    GOING = "행군 중"
    STATIONED = "주둔 중"
    RETURNING = "귀환 중"
    COMPLETED = "의무 완료"

class March:
    """
    부대의 이동 및 임무(행군)를 관리하는 클래스
    """
    def __init__(
        self, 
        user_id: str, 
        army: Army,  # 챔피언 ID 리스트 대신 Army 객체 수용
        start_pos: Tuple[int, int], 
        target_pos: Tuple[int, int],
        move_speed: float = 1.0  # 초당 이동 거리 (타일 수)
    ):
        self.user_id = user_id
        self.army = army
        self.start_pos = start_pos
        self.target_pos = target_pos
        self.status = MarchStatus.GOING
        
        # 행군 시작 시 부대 상태 변경
        self.army.status = "MARCHING"
        
        # 거리 계산 (유클리드 거리)
        self.distance = math.sqrt((target_pos[0] - start_pos[0])**2 + (target_pos[1] - start_pos[1])**2)
        
        # 소요 시간 계산 (초 단위)
        self.travel_time_seconds = self.distance / move_speed * 60 # 1타일당 1분 기본 (예시)
        
        self.start_time = datetime.now()
        self.arrival_time = self.start_time + timedelta(seconds=self.travel_time_seconds)

    def is_arrived(self) -> bool:
        """현재 시간이 도착 예정 시간보다 지났는지 확인"""
        if self.status != MarchStatus.GOING:
            return False
        return datetime.now() >= self.arrival_time

    def get_remaining_time(self) -> float:
        """남은 시간 (초)"""
        remaining = (self.arrival_time - datetime.now()).total_seconds()
        return max(0, remaining)

    def __repr__(self):
        return f"March({self.user_id}: {self.army.champion.name} {self.start_pos} -> {self.target_pos}, Status: {self.status.value})"
