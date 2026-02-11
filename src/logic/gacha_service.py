import random
import json
import os
from typing import Dict, Any, Tuple
from src.db_manager import DatabaseManager
from src.models.user import User

class GachaService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.champion_data = self._load_champion_data()
        self.gacha_config = self._load_gacha_config()

    def _load_gacha_config(self) -> Dict[str, Any]:
        """gacha_config.json에서 가챠 설정을 로드합니다."""
        possible_paths = [
            "data/gacha_config.json",
            "../data/gacha_config.json",
            "../../data/gacha_config.json"
        ]
        
        # 절대 경로 기준 탐색 (프로젝트 루트 가정)
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__)) # src/logic
            project_root = os.path.dirname(os.path.dirname(current_dir)) # LeagueSLG
            abs_path = os.path.join(project_root, "data", "gacha_config.json")
            if os.path.exists(abs_path):
                possible_paths.insert(0, abs_path)
        except Exception:
            pass

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    print(f"Error loading {path}: {e}")
                    continue
        print("Warning: data/gacha_config.json not found.")
        return {}

    def _load_champion_data(self) -> Dict[str, Any]:
        """champions.json에서 챔피언 데이터를 로드합니다."""
        # 다양한 실행 환경(루트, src 내부 등)에서 파일 위치 찾기
        possible_paths = [
            "data/champions.json",
            "../data/champions.json",
            "../../data/champions.json"
        ]
        
        # 절대 경로 기준 탐색 (프로젝트 루트 가정)
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__)) # src/logic
            project_root = os.path.dirname(os.path.dirname(current_dir)) # LeagueSLG
            abs_path = os.path.join(project_root, "data", "champions.json")
            if os.path.exists(abs_path):
                possible_paths.insert(0, abs_path)
        except Exception:
            pass

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    print(f"Error loading {path}: {e}")
                    continue
        
        # 못 찾았을 경우 빈 딕셔너리 반환하거나 에러
        print("Warning: data/champions.json not found.")
        return {}

    def pull_champion(self, user_id: int, gacha_type: str = "gold_gacha") -> Tuple[bool, str, Dict[str, Any]]:
        """
        특정 타입의 가챠를 실행하여 챔피언을 뽑습니다.
        Args:
            user_id: 유저 ID
            gacha_type: 'silver_gacha', 'gold_gacha', 'pickup_gacha' 중 하나
        Returns: (Success, Message, ResultDetails)
        """
        # 1. Config Validation
        if gacha_type not in self.gacha_config:
            return False, f"Invalid gacha type: {gacha_type}", {}
        
        config = self.gacha_config[gacha_type]
        cost = config['cost']
        currency = config['currency']
        pool = config['pool'] # List of {"name": "Garen", "weight": 10}

        # 2. Check User Resource
        user_info = self.db.get_user_info(user_id)
        if not user_info:
            return False, "User not found", {}
        
        available_amount = user_info['resources'].get(currency, 0)
        
        if available_amount < cost:
            return False, f"Not enough {currency}. Need {cost}, Have {available_amount}", {}

        # 3. Weighted Random Selection
        total_weight = sum(item['weight'] for item in pool)
        pick_val = random.uniform(0, total_weight)
        current_weight = 0
        picked_key = None
        
        for item in pool:
            current_weight += item['weight']
            if pick_val <= current_weight:
                picked_key = item['name']
                break
        
        if not picked_key:
            picked_key = pool[-1]['name'] # Fallback
            
        # Get detailed data
        picked_data = self.champion_data.get(picked_key, {})

        # 4. Deduct Resource & Add Champion
        if not self.db.update_user_resource(user_id, currency, -cost):
             return False, f"Failed to deduct {currency}", {}
             
        self.db.add_champion_to_user(user_id, picked_key)

        remaining = available_amount - cost

        return True, f"축하합니다! {config.get('name', gacha_type)}에서 [{picked_key}] 영웅을 획득했습니다!", {
            "name": picked_key,
            "images": picked_data.get("images", {}),
            "remaining_currency": remaining,
            "currency_type": currency
        }
