from src.common.database import Base, engine
from src.models import user, user_champion
from src.models.user import User
from src.models.user_champion import UserChampion
from src.models.battle_log import BattleLog
from src.models.user_internal_building import UserInternalBuilding
from src.models.army_model import ArmyDb

def init():
    Base.metadata.create_all(bind=engine)
    print("✅ DB tables created")

if __name__ == "__main__":
    init()