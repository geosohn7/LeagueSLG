from sqlalchemy import Column, Integer, String, ForeignKey
from src.common.database import Base

class UserChampion(Base):
    __tablename__ = "user_champions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    champion_key = Column(String, nullable=False)
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)