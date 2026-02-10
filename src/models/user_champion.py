from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.common.database import Base

class UserChampion(Base):
    __tablename__ = "user_champions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    champion_key = Column(String, nullable=False)
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)

    # 챔피언이 소속된 부대 ID
    army_db_id = Column(Integer, ForeignKey("armies.id"), nullable=True, default=None)
    
    # 현재 병력 (HP) - 전투 후 저장됨
    current_hp = Column(Integer, default=100, nullable=False) # 기본값 100 (실제로는 Max HP여야 함)

    # 관계 설정 (ArmyDb.champions와 양방향)
    # lazy import를 위해 문자열 참조 사용
    army = relationship("ArmyDb", back_populates="champions", foreign_keys=[army_db_id])