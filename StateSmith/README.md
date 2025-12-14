# StateSmith - Automata Escape Room Game

An interactive web-based game that teaches Deterministic Finite Automata (DFA) through progressive puzzle challenges. Players build state machines on a canvas to escape from dungeon rooms!

## 🎮 Game Features

- **12 Progressive Levels**: From Tutorial to Master difficulty
- **Interactive Canvas**: Drag-and-drop state machine builder
- **Visual Feedback**: Real-time testing with step-by-step execution
- **Star Rating System**: Earn 1-3 stars based on solution efficiency
- **Modern UI**: Dungeon-themed interface with smooth animations
- **Hints System**: Get help when stuck on challenging levels
- **Progress Tracking**: Save your progress across sessions

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Navigate to the StateSmith directory:
```powershell


2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Run the game server:
```powershell
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5001
```

## 🎯 How to Play

### Goal
Build a DFA (Deterministic Finite Automaton) that accepts the "good keys" and rejects the "bad keys" to escape each room!

### Controls

**Canvas Interaction:**
- **Left Click**: Add new state or select existing state
- **Right Click**: Add transitions from selected state
- **Click + Drag**: Move states around

**Toolbar Buttons:**
- **Add State**: Create a new state in the center
- **Set Start**: Mark selected state as the start state (green arrow)
- **Set Accept**: Toggle selected state as accept state (double circle)
- **Delete State**: Remove selected state
- **Clear All**: Reset the entire canvas

### Building Your DFA

1. **Create States**: Click on the canvas to add states
2. **Set Start State**: Select a state and click "Set Start" (there can only be one)
3. **Set Accept States**: Select states and click "Set Accept" (can have multiple)
4. **Add Transitions**: Right-click a state to define where it goes on each symbol
5. **Test Solution**: Click "Test My DFA" to see if your solution works!

### Level Progression

| Difficulty | Levels | Description |
|-----------|---------|-------------|
| Tutorial | 1-3 | Basic patterns (ends with, starts with) |
| Easy | 4-6 | Simple counting (even/odd, parity) |
| Medium | 7-9 | Pattern recognition (forbidden patterns) |
| Hard | 10-11 | Complex logic (divisibility, multiples) |
| Master | 12 | Grand finale challenge |

## 📋 Game Levels

1. **The First Door** - Accept strings ending with "1"
2. **The Parity Chamber** - Even number of 1's
3. **The Binary Gate** - Even binary numbers
4. **The Alternating Path** - No consecutive 1's
5. **The Double Guard** - Divisibility by 3
6. **The Triple Lock** - Contains "11"
7. **The Forbidden Zone** - No "00" substring
8. **The Pattern Maze** - Starts and ends with same symbol
9. **The Modulo Gate** - Divisibility by 5
10. **The Complex Lock** - Even 0's OR odd 1's
11. **The Perfect Balance** - Equal 0's and 1's (length ≤ 6)
12. **The Grand Finale** - Ultimate challenge!

## 🎨 Game Architecture

### Backend (Python Flask)
- `app.py` - Main Flask server with API routes
- `dfa_engine.py` - DFA validation and testing logic
- `levels.py` - Level definitions and requirements

### Frontend (HTML/CSS/JS)
- `templates/index.html` - Main game interface
- `static/css/style.css` - Dungeon-themed styling
- `static/js/main.js` - Game state management
- `static/js/canvas.js` - Interactive state machine builder

## 🔧 API Endpoints

- `GET /api/levels` - Get all level information
- `GET /api/level/<id>` - Get specific level details
- `POST /api/test_solution` - Test DFA against level requirements
- `GET /api/hint` - Get hint for current level
- `POST /api/progress` - Save player progress

## 🎓 Learning Objectives

By playing StateSmith, you'll learn:

- **DFA Fundamentals**: States, transitions, start/accept states
- **Pattern Recognition**: How to design automatons for specific patterns
- **Formal Languages**: Regular languages and their representations
- **Problem Solving**: Breaking down complex patterns into state logic
- **Optimization**: Creating minimal state machines

## 🌟 Star Rating System

- ⭐ **1 Star**: Solution works but uses maximum allowed states
- ⭐⭐ **2 Stars**: Good solution with reasonable number of states
- ⭐⭐⭐ **3 Stars**: Optimal solution using minimal states!

## 🐛 Troubleshooting

### Port Already in Use
If port 5001 is already in use, edit `app.py` and change:
```python
app.run(debug=True, port=5002)  # Use a different port
```

### Canvas Not Working
Make sure JavaScript is enabled in your browser and clear your cache if needed.

## 📝 Tips for Success

1. **Start Simple**: Begin with the minimum number of states needed
2. **Test Early**: Use the test button frequently to check your progress
3. **Use Hints**: Don't be afraid to ask for help on difficult levels
4. **Think About States**: Each state represents "remembering" something about the input
5. **Draw on Paper**: Sometimes sketching the DFA first helps!

## 🎉 Credits

Created as an educational game for Theory of Computation course.

**Technologies Used:**
- Flask 3.0.0
- HTML5 Canvas API
- Modern JavaScript (ES6+)
- CSS3 Animations
- Font Awesome Icons
- Google Fonts (Orbitron & Inter)

---

Have fun escaping the dungeon with the power of automata! 🏰✨
