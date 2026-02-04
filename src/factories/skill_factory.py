import json
import importlib
from pathlib import Path
from src.models.skill import Skill

# =========================
# 내부 캐시
# =========================
_SKILL_DATA = None


# =========================
# 프로젝트 루트 기준 JSON 로더
# =========================
def _load_skill_data():
    global _SKILL_DATA

    if _SKILL_DATA is not None:
        return _SKILL_DATA

    # skill_factory.py 위치 기준 → LeagueSLG 루트 계산
    # LeagueSLG/src/factories/skill_factory.py
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    SKILL_JSON_PATH = PROJECT_ROOT / "data" / "skills.json"

    try:
        with open(SKILL_JSON_PATH, "r", encoding="utf-8") as f:
            _SKILL_DATA = json.load(f)
    except FileNotFoundError:
        # 운영 중에도 죽지 않게 방어
        _SKILL_DATA = {}

    return _SKILL_DATA


# =========================
# 기존 공개 API (절대 변경 ❌)
# =========================
def create_skill(skill_id: str) -> Skill:
    data_map = _load_skill_data()
    skill_info = data_map.get(skill_id, {"name": skill_id})

    # ---------------------------------
    # 커스텀 스킬 로직 로딩 (기존 유지)
    # instance/skill/{skill_id}.py
    # ---------------------------------
    try:
        module_name = f"instance.skill.{skill_id}"
        module = importlib.import_module(module_name)

        if hasattr(module, skill_id):
            skill_class = getattr(module, skill_id)
            return skill_class(skill_id, skill_info)

    except (ImportError, AttributeError):
        # 커스텀 로직 없으면 기본 Skill 사용
        pass

    # ---------------------------------
    # 기본 Skill fallback (기존 유지)
    # ---------------------------------
    return Skill(skill_id, skill_info)
