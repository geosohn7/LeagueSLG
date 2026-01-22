import json
import importlib
from src.models.skill import Skill

_SKILL_DATA = None

def _load_skill_data():
    global _SKILL_DATA
    if _SKILL_DATA is None:
        try:
            with open("data/skills.json", "r", encoding="utf-8") as f:
                _SKILL_DATA = json.load(f)
        except FileNotFoundError:
            _SKILL_DATA = {}
    return _SKILL_DATA

def create_skill(skill_id: str) -> Skill:
    data_map = _load_skill_data()
    skill_info = data_map.get(skill_id, {"name": skill_id})
    
    # Try to load custom logic from instance/skill/{skill_id}.py
    try:
        # Import the module
        module_name = f"instance.skill.{skill_id}"
        module = importlib.import_module(module_name)
        
        # Look for the class (usually same as skill_id)
        if hasattr(module, skill_id):
            skill_class = getattr(module, skill_id)
            return skill_class(skill_id, skill_info)
    except (ImportError, AttributeError):
        # Specific logic file doesn't exist or doesn't have the class, use generic Skill
        pass
        
    return Skill(skill_id, skill_info)
