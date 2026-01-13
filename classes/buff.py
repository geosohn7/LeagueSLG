import time
from utils.buffType import BuffType

class Buff:
    def __init__(
        self,
        buff_type: BuffType,
        duration: float,
        value: float | None = None
    ):
        self.buff_type = buff_type
        self.value = value
        self.expire_time = time.time() + duration

    def is_expired(self) -> bool:
        return time.time() >= self.expire_time
