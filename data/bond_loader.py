
# data/bond_loader.py

import json
from pathlib import Path

# 현재 파일 위치
CURRENT_FILE = Path(__file__).resolve()

# Project Root 찾기 (data 폴더 상위)
if CURRENT_FILE.parent.name == "data":
    PROJECT_ROOT = CURRENT_FILE.parent.parent
else:
    raise RuntimeError("bond_loader.py must be inside a data/ directory")

BOND_JSON_PATH = PROJECT_ROOT / "data" / "bonds.json"

_BOND_CACHE = None

def load_bonds():
    global _BOND_CACHE

    if _BOND_CACHE is None:
        if not BOND_JSON_PATH.exists():
            # 파일이 없으면 빈 딕셔너리 반환 (혹은 에러 처리)
            return {}

        with open(BOND_JSON_PATH, "r", encoding="utf-8") as f:
            _BOND_CACHE = json.load(f)

    return _BOND_CACHE
