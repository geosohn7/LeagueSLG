from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from src.common.database import Base

class ArmyDb(Base):
    """
    유저의 부대 구성을 저장하는 데이터베이스 모델.
    게임 로직의 'Army' 객체와 달리 영속성을 가집니다.
    """
    __tablename__ = "armies"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 0~4 (최대 5개 부대)
    slot_index = Column(Integer, nullable=False)
    
    # 병종 (cavalry, spearman, archer, shieldman)
    unit_type = Column(String, default="cavalry", nullable=False)
    
    # 부대 이름 (선택적)
    name = Column(String, nullable=True)

    # 유저 당 slot_index는 유니크해야 함
    __table_args__ = (
        UniqueConstraint('user_id', 'slot_index', name='uq_user_army_slot'),
    )

    # 관계 설정
    # UserChampion과 1:N 관계 (하나의 ArmyDb는 여러 UserChampion을 가짐)
    champions = relationship("UserChampion", back_populates="army", foreign_keys="UserChampion.army_db_id")

    def __repr__(self):
        return f"<ArmyDb(user={self.user_id}, slot={self.slot_index}, type={self.unit_type})>"
