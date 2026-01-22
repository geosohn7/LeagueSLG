import json
from src.models.buff import Buff

# 버프 데이터 캐싱용 변수
_BUFF_DATA = None

def _load_buff_data():
    """
    buffs.json 에서 버프의 기본 정의(베이스 수치, 대상 스탯 등)를 로드
    """
    global _BUFF_DATA
    if _BUFF_DATA is None:
        try:
            with open("data/buffs.json", "r", encoding="utf-8") as f:
                _BUFF_DATA = json.load(f)
        except FileNotFoundError:
            _BUFF_DATA = {}
    return _BUFF_DATA

def create_buff(buff_id: str, duration: int, caster=None, skill_coeff: float = 1.0, scaling_stat: str = "SPATK") -> Buff:
    """
    시전자의 능력치와 스킬 계수를 조합하여 최종 위력이 계산된 Buff 객체를 생성
    
    공식: [스킬 계수] * [시전자 참조 스탯] * [버프 베이스 수치]
    예: 0.3(계수) * 20(시전자 주문력) * 1.0(베이스) = 6.0 (%)
    """
    data = _load_buff_data()
    # buffs.json에 정의된 기본 정보를 가져옴
    b_info = data.get(buff_id, {"base_value": 1.0})
    
    applied_value = 0.0
    
    # 베이스 수치가 있는 버프(능력치 변화 등)만 위력을 계산
    if caster and b_info.get("base_value", 0) > 0:
        caster_stat = caster.getStat(scaling_stat)
        applied_value = skill_coeff * caster_stat * b_info.get("base_value", 1.0)
    elif b_info.get("base_value", 0) > 0:
        # 시전자가 없을 경우 기본 계수만 반영
        applied_value = skill_coeff * b_info.get("base_value", 1.0)
    
    # ID 기반으로 Buff 객체를 생성하여 반환
    return Buff(buff_id, duration, value=applied_value)
