# 📂 LeagueSLG Project Handover Document

> **To the New AI Assistant:**
> Please read this document carefully. It contains the entire context, architectural decisions, recent bug fixes, and future plans for the LeagueSLG project.
> Your goal is to continue acting as the **Lead Developer (Antigravity)** for this project, maintaining the same context and helpfulness as before.

---

## 1. 🏗️ Project Overview
**LeagueSLG** is a strategy simulation game featuring League of Legends champions.
- **Backend**: Python (FastAPI, SQLAlchemy, SQLite)
- **Frontend**: Flutter (Mobile & Web)
- **Core Mechanics**: 20x20 Grid Map, Turn-based Battle System, Gacha (Champion Summoning), City Management.

## 2. 🛠️ Tech Stack & Architecture
- **Database**: SQLite (`db/game_data.db`).
  - **ORM**: SQLAlchemy (`src/models/`).
  - **Schema Management**: `src/api/server.py` now auto-creates tables on startup.
- **API Server**: FastAPI (`src/api/server.py`).
  - Runs on `http://localhost:8000`.
  - Handles game logic, map data, battles, and user state.
- **Frontend**: Flutter (`flutter_app/`).
  - Uses `http` package to communicate with the backend.
  - **Web Version**: Renders via Canvas (HTML/JS), does not use standard HTML DOM elements for game objects.

## 3. 🚨 Recent Critical Fixes (Must Know)
These fixes were applied to resolve issues on other environments (e.g., a friend's PC).

### A. Missing Database Tables
- **Issue**: `db/game_data.db` is git-ignored, so new clones crashed with "no such table".
- **Fix**: Added `@app.on_event("startup")` in `src/api/server.py` to auto-run `Base.metadata.create_all(bind=engine)`.
- **Instruction**: Just run `py src/api/server.py`, and the DB is created automatically.

### B. Army Creation Bug
- **Issue**: `create_army` expected a `List[Champion]`, but a single object was passed, causing a 500 Error.
- **Fix**: Changed `map_manager.create_army(request.user_id, champion)` to `map_manager.create_army(request.user_id, [champion])` in `src/api/server.py`.

### C. Old DB Schema Issue
- **Issue**: `OperationalError: no such column: users.silver` might occur if an old DB file exists.
- **Fix**: Delete `db/game_data.db` manually. The server will recreate it with the correct schema (including `silver`, `gold` columns).

## 4. 🗺️ Key Implementation Details

### Map System
- **Logic**: `src/logic/map_manager.py` handles movement, occupation, and battle triggering.
- **Visuals**: `flutter_app/lib/main.dart` -> `TileWidget`.
  - No assets are used; visuals are drawn using `Container` colors and Emojis/Text.

### Battle System
- **Simulation**: Python backend (`src/logic/battle/`) runs the math.
- **Reporting**:
  - **Dev Mode**: Generates `reports/battle_report.html` and opens it in the browser via Python.
  - **User Mode**: Frontend queries `/battle/results` and displays a Flutter UI (`BattleScreen`).

### User & Resources
- **Models**: `src/models/user.py` defines the DB schema (has `gold`, `silver`, `food`, etc.).
- **Game Logic**: `src/game/user.py` is currently a lightweight wrapper.
  - **TODO**: Move resource management logic (add/spend) into `src/game/user.py` to reduce direct DB calls and enable caching.

## 5. 🚀 How to Run

### Backend
```bash
# Initialize DB (Optional, server does it too)
py src/init_db.py

# Start Server
py src/api/server.py
```

### Frontend
```bash
cd flutter_app
# Run on Web (Recommended for Dev)
flutter run -d chrome

# Run on Android Emulator
# IMPORTANT: Change API URL in main.dart to 'http://10.0.2.2:8000'
```

## 6. 📝 Future Roadmap (Things to do next)
1.  **Refactor Resource Logic**: Implement `add_resource`/`spend_resource` in `src/game/user.py`.
2.  **Asset Integration**: Replace placeholder colors/emojis with actual images (when assets are ready).
3.  **Building Upgrades**: Implement logic for upgrading buildings and unlocking new features.

---
**End of Handover Document**
