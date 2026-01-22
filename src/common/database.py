import sqlite3
import os
from typing import List, Dict, Any

class DatabaseManager:
    """
    SQLite 데이터베이스 관리 클래스: 유저 정보 및 챔피언 상태 저장
    """
    def __init__(self, db_path: str = "db/game_data.db"):
        self.db_path = db_path
        # instance 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """테이블 초기화"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 유저 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL
                )
            ''')
            
            # 유저의 보유 챔피언 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_champions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    champion_key TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    exp INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.commit()

    def get_or_create_user(self, username: str) -> int:
        """유저 ID를 가져오거나 없으면 생성"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result:
                return result[0]
            
            cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
            conn.commit()
            return cursor.lastrowid

    def add_champion_to_user(self, user_id: int, champion_key: str):
        """유저에게 챔피언 추가"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_champions (user_id, champion_key) VALUES (?, ?)",
                (user_id, champion_key)
            )
            conn.commit()

    def get_user_champions(self, user_id: int) -> List[Dict[str, Any]]:
        """유저가 보유한 모든 챔피언 정보 조회"""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM user_champions WHERE user_id = ?",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_champion_data(self, champion_id: int, level: int, exp: int):
        """챔피언의 레벨과 경험치 업데이트"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE user_champions SET level = ?, exp = ? WHERE id = ?",
                (level, exp, champion_id)
            )
            conn.commit()
