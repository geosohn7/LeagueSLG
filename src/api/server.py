from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add the parent directory to sys.path to import existing classes
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.factories.champion_factory import create_champion, _load_champion_data
from src.logic.battle.battle import Battle
from src.models.champion import Champion

app = FastAPI()

# Mount Static Files
if not os.path.exists("static"):
    # Fallback or strict check, but for now assuming running from root
    pass
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class BattleRequest(BaseModel):
    left_id: str
    right_id: str

class BattleLog(BaseModel):
    turn: int
    actor: str
    target: str
    action: str
    damage: Optional[float] = 0
    left_hp: float
    right_hp: float
    message: str

class WebBattle(Battle):
    def __init__(self, left: Champion, right: Champion):
        super().__init__(left, right)
        self.logs = []

    def _log(self, msg: str):
        # We'll override this to capture logs instead of just printing
        # But for more structured data, we might need to hook into specific methods
        pass

    def _process_turn(self, actor: Champion, target: Champion):
        turn_data = {
            "turn": self.turn,
            "actor": actor.name,
            "target": target.name,
            "left_hp": self.left.current_hp,
            "right_hp": self.right.current_hp
        }
        
        # Capture turn start
        actor.on_turn_start()
        
        # Skill or basic attack
        skill = actor.roll_skills()
        if skill:
            action_name = skill.name
            # Skill effect logic usually calls take_damage or similar
            # For simplicity, we'll just track HP changes
            old_hp = target.current_hp
            skill.cast(self, actor, target)
            damage = old_hp - target.current_hp
        else:
            action_name = "일반 공격"
            atk = actor.getStat('ATK')
            df = target.getStat('DEF')
            damage = (atk * atk) / max(1, df)
            target.take_damage(damage)

        turn_data.update({
            "action": action_name,
            "damage": damage,
            "message": f"{actor.name}의 {action_name}! ({damage:.1f} 데미지)",
            "left_hp": self.left.current_hp,
            "right_hp": self.right.current_hp
        })
        
        self.logs.append(turn_data)
        actor.on_turn_end()

    def run_to_end(self):
        while self._both_alive() and self.turn < 100: # Safety cap
            first, second = self._get_turn_order()
            self._process_turn(first, second)
            if not second.is_alive():
                break
            self._process_turn(second, first)
            self.turn += 1
        
        winner = self.left.name if self.left.is_alive() else self.right.name
        return {
            "winner": winner, 
            "logs": self.logs,
            "left": {"name": self.left.name, "max_hp": self.left.max_hp},
            "right": {"name": self.right.name, "max_hp": self.right.max_hp}
        }

@app.get("/champions")
async def get_champions():
    data = _load_champion_data()
    return [{"id": k, "name": v["name"], "base_stat": v["base_stat"]} for k, v in data.items()]

@app.post("/simulate")
async def simulate_battle(request: BattleRequest):
    try:
        left = create_champion(request.left_id)
        right = create_champion(request.right_id)
        
        battle = WebBattle(left, right)
        result = battle.run_to_end()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
