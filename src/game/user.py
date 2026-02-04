from typing import List
from src.db_manager import DatabaseManager
from src.models.champion import Champion
from src.logic.champion_mapper import orm_to_champion, champion_to_orm
from src.logic.champion_mapper import orm_dict_to_champion


class User:
    """
    게임 로직용 User
    - main.py가 기대하는 인터페이스 제공
    - 내부적으로 DatabaseManager 사용
    """

    def __init__(self, username: str, db_manager: DatabaseManager):
        self.username = username
        self.db = db_manager

        # DB에서 유저 및 챔피언 로드
        self.user_id = self.db.get_or_create_user(username)
        self.champions: List[Champion] = []
        self._load_champions()


    def _load_champions(self):
        champ_rows = self.db.get_user_champions(self.user_id)

        self.champions = [
            orm_dict_to_champion(row)
            for row in champ_rows
    ]


    def add_champion(self, champion_key: str):
        self.db.add_champion_to_user(self.user_id, champion_key)
        self._load_champions()

    def save_data(self):
        """
        현재 챔피언 상태를 DB에 저장
        """
        for champ in self.champions:
            self.db.update_champion_data_by_key(
                self.user_id,
                champ.name,
                champ.level,
                champ.exp,
            )
