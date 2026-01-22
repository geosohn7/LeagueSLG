import json
import importlib

"""
심플 아이템 팩토리
- items.json에서 아이템 데이터를 읽어 Item 객체를 생성
- instance/item/<item_id>.py 가 존재하면 그 모듈의 클래스를 사용하여 생성 시도
"""

_ITEM_DATA = None

def _load_item_data():
    global _ITEM_DATA
    if _ITEM_DATA is None:
        try:
            with open("data/items.json", "r", encoding="utf-8") as f:
                _ITEM_DATA = json.load(f)
        except FileNotFoundError:
            _ITEM_DATA = {}
    return _ITEM_DATA

class Item:
    """
    간단한 아이템 데이터 컨테이너.
    실제 게임에서 장착 시 효과를 적용하려면 `apply_on_equip` / `remove_on_unequip` 를 오버라이드하세요.
    """
    def __init__(self, item_id: str, info: dict):
        self.id = item_id
        self.name = info.get("name", item_id)
        self.stat_bonuses = info.get("stat_bonuses", [])
        self.on_hit = info.get("on_hit")
        self.description = info.get("description", "")

    def apply_on_equip(self, champion):
        """
        챔피언에게 장착(영구 적용)할 때 호출할 기본 동작.
        - stat_bonuses를 읽어 `champion.base_stat`을 직접 수정하고 `recalculate_stats()`를 호출합니다.
        """
        idx_map = {"HP":0, "ATK":1, "DEF":2, "SPATK":3, "SPDEF":4, "SPD":5}
        for bonus in self.stat_bonuses:
            stat = bonus.get("stat", "").upper()
            value = bonus.get("value", 0)
            is_percent = bonus.get("is_percent", False)
            idx = idx_map.get(stat)
            if idx is None:
                continue
            if is_percent:
                champion.base_stat[idx] = int(champion.base_stat[idx] * (1 + value/100))
            else:
                champion.base_stat[idx] = int(champion.base_stat[idx] + value)
        # 능력치 재계산
        try:
            champion.recalculate_stats()
        except Exception:
            # 챔피언이 해당 메서드를 가지지 않으면 무시
            pass

    def remove_on_unequip(self, champion):
        """
        현재는 구현되어 있지 않음(필요 시 역적용 로직 추가).
        """
        pass

def create_item(item_id: str) -> Item:
    data_map = _load_item_data()
    item_info = data_map.get(item_id, {"name": item_id})

    # Try to load custom logic from instance/item/<item_id>.py
    try:
        module_name = f"instance.item.{item_id}"
        module = importlib.import_module(module_name)
        if hasattr(module, item_id):
            item_class = getattr(module, item_id)
            return item_class(item_id, item_info)
    except (ImportError, AttributeError):
        pass

    return Item(item_id, item_info)

