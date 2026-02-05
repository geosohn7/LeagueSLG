# LeagueSLG/data/champion_loader.py

import json
from pathlib import Path

# 현재 파일 위치
CURRENT_FILE = Path(__file__).resolve()

# LeagueSLG 루트 찾기 (data 폴더를 포함하는 디렉토리)
if CURRENT_FILE.parent.name == "data":
    PROJECT_ROOT = CURRENT_FILE.parent.parent
else:
    raise RuntimeError("champion_loader.py must be inside a data/ directory")

CHAMPION_JSON_PATH = PROJECT_ROOT / "data" / "champions.json"

_CHAMPION_CACHE = None


def load_champions():
    global _CHAMPION_CACHE

    if _CHAMPION_CACHE is None:
        if not CHAMPION_JSON_PATH.exists():
            raise FileNotFoundError(
                f"champions.json not found at: {CHAMPION_JSON_PATH}"
            )

        with open(CHAMPION_JSON_PATH, "r", encoding="utf-8") as f:
            _CHAMPION_CACHE = json.load(f)

    return _CHAMPION_CACHE
