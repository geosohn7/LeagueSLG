import json
import importlib
from src.models.champion import Champion
from src.factories.skill_factory import create_skill

_CHAMPION_DATA = None


def _load_champion_data():
    global _CHAMPION_DATA
    if _CHAMPION_DATA is None:
        try:
            with open("data/champions.json", "r", encoding="utf-8") as f:
                _CHAMPION_DATA = json.load(f)
        except FileNotFoundError:
            # Fallback for different execution contexts
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            rel_path = os.path.join(current_dir, "../../data/champions.json")
            with open(rel_path, "r", encoding="utf-8") as f:
                _CHAMPION_DATA = json.load(f)
    return _CHAMPION_DATA


def create_champion(champion_id: str) -> Champion:
    data = _load_champion_data()

    # [Patch] Handle Legacy Keys directly in Factory
    legacy_map = {
        "Garen": "주몽", "Ashe": "소서노", "Lux": "선덕여왕",
        "Darius": "광개토대왕", "Ahri": "평강공주", "Katarina": "연개소문",
        "Jhin": "양만춘", "Lee Sin": "계백", "Yasuo": "김유신",
        "Teemo": "이차돈", "Ezreal": "김춘추", "Caitlyn": "낙랑공주",
        "Jinx": "호동왕자", "Leona": "세오녀", "LeBlanc": "도림",
        "Guan Yu": "관창", "Zhu Ge Liang": "을지문덕", "Cao Cao": "연개소문",
        "Sejong the Great": "광개토대왕", "Khazix": "비형랑",
        "Kai'Sa": "설총", "Akali": "최치원", "Jax": "온달", "Irelia": "평강공주"
    }

    if champion_id not in data:
        if champion_id in legacy_map:
            # print(f"[Factory] Redirecting '{champion_id}' -> '{legacy_map[champion_id]}'")
            champion_id = legacy_map[champion_id]
        else:
            # Fallback if specific mapping missing but needed to proceed
            # print(f"[Factory] Unknown ID '{champion_id}', falling back to '주몽'")
            champion_id = "주몽"
            
    if champion_id not in data:
         raise ValueError(f"Champion '{champion_id}' not found after mapping")

    c = data[champion_id]
    skills = [create_skill(sid) for sid in c.get("skills", [])]

    # Try to load custom logic from instance/champion/{champion_id}.py
    try:
        module_name = f"instance.champion.{champion_id}"
        module = importlib.import_module(module_name)
        
        if hasattr(module, champion_id):
            champion_class = getattr(module, champion_id)
            return champion_class(
                name=c["name"],
                base_stat=c["base_stat"],
                stat_growth=c["stat_growth"],
                skills=skills,
                minions=tuple(c["minions"]) if c.get("minions") else None,
                image=c.get("images", {}),
                faction=c.get("faction", "None")
            )
    except (ImportError, AttributeError):
        pass

    return Champion(
        name=c["name"],
        base_stat=c["base_stat"],
        stat_growth=c["stat_growth"],
        skills=skills,
        minions=tuple(c["minions"]) if c.get("minions") else None,
        image=c.get("images", {}),
        faction=c.get("faction", "None")
    )
