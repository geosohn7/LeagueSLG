from sqlalchemy import Column, Integer, String, DateTime
from src.common.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    
    # 자원 시스템
    gold = Column(Integer, default=10000, nullable=False)   # Premium Currency (Cash Only)
    silver = Column(Integer, default=100000, nullable=False) # Common Currency (Mined)
    food = Column(Integer, default=500, nullable=False)
    wood = Column(Integer, default=500, nullable=False)
    iron = Column(Integer, default=100, nullable=False)
    stone = Column(Integer, default=100, nullable=False)
    
    reserve_troops = Column(Integer, default=100, nullable=False)
    
    # 은(Silver) 자동 생산용 (기존 Gold 대체)
    last_silver_collected = Column(DateTime, nullable=True)