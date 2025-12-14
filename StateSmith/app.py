from flask import Flask, render_template, request, jsonify, session
import json
import secrets
from dfa_engine import DFA, validate_dfa, test_dfa_against_level
from levels import LEVELS
from achievements import check_achievements, get_new_achievements

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/levels')
def get_levels():
    """Get all available levels"""
    return jsonify({
        'success': True,
        'levels': [
            {
                'id': level['id'],
                'title': level['title'],
                'difficulty': level['difficulty'],
                'unlocked': session.get(f'level_{level["id"]}_unlocked', level['id'] == 1)
            }
            for level in LEVELS
        ]
    })

@app.route('/api/level/<int:level_id>')
def get_level(level_id):
    """Get specific level details"""
    level = next((l for l in LEVELS if l['id'] == level_id), None)
    if not level:
        return jsonify({'success': False, 'error': 'Level not found'}), 404
    
    # Check if unlocked
    if level_id > 1 and not session.get(f'level_{level_id}_unlocked', False):
        return jsonify({'success': False, 'error': 'Level locked'}), 403
    
    return jsonify({
        'success': True,
        'level': {
            'id': level['id'],
            'title': level['title'],
            'description': level['description'],
            'alphabet': level['alphabet'],
            'rule': level['rule'],
            'good_keys': level['good_keys'],
            'bad_keys': level['bad_keys'],
            'hint': level.get('hint', ''),
            'difficulty': level['difficulty'],
            'min_states': level.get('min_states', 2),
            'max_states': level.get('max_states', 10)
        }
    })

@app.route('/api/test_solution', methods=['POST'])
def test_solution():
    """Test player's DFA solution"""
    try:
        data = request.json
        level_id = data['level_id']
        dfa_data = data['dfa']
        
        # Get level
        level = next((l for l in LEVELS if l['id'] == level_id), None)
        if not level:
            return jsonify({'success': False, 'error': 'Level not found'}), 404
        
        # Validate DFA structure
        validation = validate_dfa(dfa_data, level['alphabet'])
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': validation['error'],
                'hint': 'Check your state machine structure'
            })
        
        # Create DFA object
        dfa = DFA(
            states=set(dfa_data['states']),
            alphabet=set(level['alphabet']),
            transitions=dfa_data['transitions'],
            start_state=dfa_data['start_state'],
            accept_states=set(dfa_data['accept_states'])
        )
        
        # Test against level requirements
        result = test_dfa_against_level(dfa, level)
        
        if result['passed']:
            # Get old progress for achievement comparison
            old_progress = {
                'completed_levels': sum(1 for l in LEVELS if session.get(f'level_{l["id"]}_completed', False)),
                'total_stars': sum(session.get(f'level_{l["id"]}_stars', 0) for l in LEVELS),
                'levels': {
                    l['id']: {
                        'completed': session.get(f'level_{l["id"]}_completed', False),
                        'stars': session.get(f'level_{l["id"]}_stars', 0),
                        'unlocked': session.get(f'level_{l["id"]}_unlocked', l['id'] == 1)
                    }
                    for l in LEVELS
                }
            }
            
            # Unlock next level
            next_level_id = level_id + 1
            session[f'level_{next_level_id}_unlocked'] = True
            
            # Save score
            current_stars = session.get(f'level_{level_id}_stars', 0)
            session[f'level_{level_id}_stars'] = max(current_stars, result['stars'])
            session[f'level_{level_id}_completed'] = True
            
            # Get new progress and check for new achievements
            new_progress = {
                'completed_levels': sum(1 for l in LEVELS if session.get(f'level_{l["id"]}_completed', False)),
                'total_stars': sum(session.get(f'level_{l["id"]}_stars', 0) for l in LEVELS),
                'levels': {
                    l['id']: {
                        'completed': session.get(f'level_{l["id"]}_completed', False),
                        'stars': session.get(f'level_{l["id"]}_stars', 0),
                        'unlocked': session.get(f'level_{l["id"]}_unlocked', l['id'] == 1)
                    }
                    for l in LEVELS
                }
            }
            
            new_achievements = get_new_achievements(old_progress, new_progress)
            
            return jsonify({
                'success': True,
                'passed': True,
                'stars': result['stars'],
                'message': result['message'],
                'test_results': result['test_results'],
                'next_level_unlocked': next_level_id <= len(LEVELS),
                'new_achievements': [{
                    'id': a['id'],
                    'title': a['title'],
                    'description': a['description'],
                    'icon': a['icon']
                } for a in new_achievements]
            })
        else:
            return jsonify({
                'success': True,
                'passed': False,
                'message': result['message'],
                'test_results': result['test_results'],
                'failed_key': result.get('failed_key')
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/hint/<int:level_id>')
def get_hint(level_id):
    """Get hint for a level (costs a star)"""
    level = next((l for l in LEVELS if l['id'] == level_id), None)
    if not level:
        return jsonify({'success': False, 'error': 'Level not found'}), 404
    
    return jsonify({
        'success': True,
        'hint': level.get('detailed_hint', level.get('hint', 'Try testing with the example keys!'))
    })

@app.route('/api/progress')
def get_progress():
    """Get player's progress"""
    progress = {
        'completed_levels': sum(1 for level in LEVELS if session.get(f'level_{level["id"]}_completed', False)),
        'total_stars': sum(session.get(f'level_{level["id"]}_stars', 0) for level in LEVELS),
        'levels': {
            level['id']: {
                'completed': session.get(f'level_{level["id"]}_completed', False),
                'stars': session.get(f'level_{level["id"]}_stars', 0),
                'unlocked': session.get(f'level_{level["id"]}_unlocked', level['id'] == 1)
            }
            for level in LEVELS
        }
    }
    return jsonify({'success': True, 'progress': progress})

@app.route('/api/achievements')
def get_achievements():
    """Get player's achievements"""
    progress = {
        'completed_levels': sum(1 for level in LEVELS if session.get(f'level_{level["id"]}_completed', False)),
        'total_stars': sum(session.get(f'level_{level["id"]}_stars', 0) for level in LEVELS),
        'levels': {
            level['id']: {
                'completed': session.get(f'level_{level["id"]}_completed', False),
                'stars': session.get(f'level_{level["id"]}_stars', 0),
                'unlocked': session.get(f'level_{level["id"]}_unlocked', level['id'] == 1)
            }
            for level in LEVELS
        }
    }
    
    unlocked_achievements = check_achievements(progress)
    
    return jsonify({
        'success': True,
        'achievements': unlocked_achievements,
        'total': len(unlocked_achievements)
    })

@app.route('/api/reset_progress', methods=['POST'])
def reset_progress():
    """Reset all progress"""
    session.clear()
    return jsonify({'success': True, 'message': 'Progress reset'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
