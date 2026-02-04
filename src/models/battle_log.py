# src/models/battle_log.py

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from src.common.database import Base

class BattleLog(Base):
    __tablename__ = "battle_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)

    left_champion = Column(String, nullable=False)
    right_champion = Column(String, nullable=False)
    winner = Column(String, nullable=False)

    turn_count = Column(Integer, nullable=False)
    history_json = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
