# StateSmith — DFA Automata Escape Room

StateSmith is a browser-based learning game for **Deterministic Finite Automata (DFA)**. Players build DFAs to “unlock doors” by accepting valid keys and rejecting invalid ones.

It’s built as a small Flask web app with a lightweight SQLite database for **user accounts**, **progress saving**, **achievements**, and a **leaderboard**.

## Features

- **Interactive DFA builder** in the browser (states, transitions, start/accept states)
- **12 progressively harder levels** (tutorial → master)
- **Automatic solution testing** against per-level good/bad keys
- **Star rating** based on correctness + efficiency (fewer states)
- **User authentication** (signup/login/logout)
- **Progress persistence** (unlocks, completions, attempts, best solutions)
- **Achievements & leaderboard**

## Tech Stack

- Backend: **Python + Flask**
- Auth: **Flask-Login**
- Database: **SQLite** via **Flask-SQLAlchemy**
- Frontend: **Vanilla JavaScript**, HTML templates, CSS, Canvas drawing

## Requirements

- Python **3.x** (recommended: 3.9+)
- Windows / macOS / Linux (instructions below are Windows-first)

Python dependencies are listed in [requirements.txt](requirements.txt).

## Quickstart (Windows / PowerShell)

From the project folder:

```powershell
cd .\StateSmith
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open your browser:

- http://localhost:5001

### Optional: use the setup script

A small helper script is included at [setup.ps1](setup.ps1).

```powershell
cd .\StateSmith
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup.ps1
python app.py
```

## How to Play

1. Start the server (`python app.py`) and open http://localhost:5001
2. Create an account (Sign Up) or log in
3. Select a level
4. Build a DFA that matches the level rule
5. Test your solution; if it passes all tests, the next level unlocks

Progress is saved automatically per account.

## Resetting Progress / Database

StateSmith stores data in a local SQLite file:

- `statesmith.db`

To start fresh, stop the server and delete `statesmith.db`. The database will be recreated automatically on next start.

## Project Structure

- [app.py](app.py) — Flask server + API routes
- [dfa_engine.py](dfa_engine.py) — DFA validation + execution + level testing
- [levels.py](levels.py) — Level definitions (rules, alphabets, test keys)
- [models.py](models.py) — SQLAlchemy models (users, progress, achievements)
- [achievements.py](achievements.py) — Achievement rules
- [templates/index.html](templates/index.html) — Main UI
- [static/js/main.js](static/js/main.js) — Frontend logic
- [static/js/canvas.js](static/js/canvas.js) — DFA canvas rendering
- [static/css/style.css](static/css/style.css) — Styling

## API (High Level)

The UI talks to a JSON API under `/api/*`, including:

- Auth: `/api/auth/signup`, `/api/auth/login`, `/api/auth/logout`, `/api/auth/current_user`
- Levels: `/api/levels`, `/api/level/<id>`, `/api/test_solution`, `/api/hint/<id>`
- Progress: `/api/progress`, `/api/reset_progress`
- Social: `/api/achievements`, `/api/leaderboard`

## Notes

- This project runs with Flask’s development server (`debug=True`) and is intended for learning/demo use.
- The Flask `secret_key` is generated on startup; restarting the server may invalidate existing sessions.

## License

No license file is currently included. If you plan to publish or share this project publicly, consider adding a `LICENSE`.
