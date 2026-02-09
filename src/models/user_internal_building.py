from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from src.common.database import Base
from datetime import datetime

class UserInternalBuilding(Base):
    __tablename__ = "user_internal_buildings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    building_type = Column(String, nullable=False)  # 'Barracks', 'Farm', 'Mine', 'Wall'
    level = Column(Integer, default=1, nullable=False)
    status = Column(String, default="IDLE")  # 'IDLE', 'UPGRADING'
    finish_time = Column(DateTime, nullable=True)  # 업그레이드 완료 예정 시간

    def is_upgrading(self) -> bool:
        return self.status == "UPGRADING" and self.finish_time and self.finish_time > datetime.now()
