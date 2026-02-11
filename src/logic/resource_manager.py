from src.db_manager import DatabaseManager
from src.models.user_internal_building import UserInternalBuilding

class ResourceManager:
    """
    자원 생산 및 수집 로직을 담당합니다.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
        # Base production rates per hour
        self.BASE_SILVER_RATE = 100
        
        # Building multipliers (e.g., Level 1 Mine = +10%)
        self.MINE_MULTIPLIER_PER_LEVEL = 0.1

    def collect_silver(self, user_id: int) -> int:
        """
        Calculates and collects accrued silver for the user.
        Returns the amount of silver collected.
        """
        # 1. Get User's Silver Mine Level
        mine = self.db.get_or_create_internal_building(user_id, "silver_mine")
        mine_level = mine.level if mine else 0
        
        # 2. Calculate Hourly Rate
        # Formula: Base + (Base * Level * Multiplier)
        hourly_rate = int(self.BASE_SILVER_RATE * (1 + mine_level * self.MINE_MULTIPLIER_PER_LEVEL))
        
        # 3. Update User Resource via DB Manager
        # We need to see how much was actually added (db_manager logic handles time diff)
        # However, db_manager.update_user_silver_generation doesn't return the amount added directly.
        # So we'll fetch silver before and after.
        
        user_info_before = self.db.get_user_info(user_id)
        if not user_info_before:
            return 0
        silver_before = user_info_before['resources']['silver']
        
        self.db.update_user_silver_generation(user_id, hourly_rate)
        
        user_info_after = self.db.get_user_info(user_id)
        silver_after = user_info_after['resources']['silver']
        
        return silver_after - silver_before
