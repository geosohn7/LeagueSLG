from src.factories.champion_factory import create_champion
from sqlalchemy import Column, Integer, String
from src.common.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)