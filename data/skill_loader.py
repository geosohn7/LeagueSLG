# data/skill_loader.py

import json
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
SKILL_JSON_PATH = PROJECT_ROOT / "data" / "skills.json"

_SKILL_CACHE = None


def load_skills():
    global _SKILL_CACHE

    if _SKILL_CACHE is None:
        if not SKILL_JSON_PATH.exists():
            raise FileNotFoundError(f"skills.json not found at: {SKILL_JSON_PATH}")

        with open(SKILL_JSON_PATH, "r", encoding="utf-8") as f:
            _SKILL_CACHE = json.load(f)

    return _SKILL_CACHE
