from typing import List
from src.models.champion import Champion
from src.common.database import DatabaseManager
from src.factories.champion_factory import create_champion

class User:
    """
    유저 클래스: 유저 정보 및 보유 챔피언 관리
    """
    def __init__(self, username: str, db_manager: DatabaseManager):
        self.username = username
        self.db_manager = db_manager
        self.user_id = self.db_manager.get_or_create_user(username)
        self.champions: List[Champion] = []
        self._load_champions()

    def _load_champions(self):
        """데이터베이스에서 유저의 챔피언 정보를 불러옴"""
        champion_data = self.db_manager.get_user_champions(self.user_id)
        self.champions = []
        for data in champion_data:
            key = data['champion_key']
            champ = create_champion(key)
            champ.db_id = data['id']
            champ.level = data['level']
            champ.exp = data['exp']
            champ.recalculate_stats()
            self.champions.append(champ)

    def add_champion(self, champion_key: str):
        """유저에게 새로운 챔피언을 지급"""
        self.db_manager.add_champion_to_user(self.user_id, champion_key)
        self._load_champions()

    def save_data(self):
        """모든 챔피언의 현재 상태를 데이터베이스에 저장"""
        for champ in self.champions:
            if hasattr(champ, 'db_id'):
                self.db_manager.update_champion_data(champ.db_id, champ.level, champ.exp)

    def get_champion(self, index: int) -> Champion:
        if 0 <= index < len(self.champions):
            return self.champions[index]
        return None
