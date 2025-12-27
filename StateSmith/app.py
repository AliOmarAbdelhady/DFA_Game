from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import secrets
import os
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dfa_engine import DFA, validate_dfa, test_dfa_against_level
from levels import LEVELS
from achievements import check_achievements, get_new_achievements, ACHIEVEMENTS
from models import db, User, UserProgress, UserAchievement

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'statesmith.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

# Authentication Routes
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Register a new user"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or len(username) < 3:
            return jsonify({'success': False, 'error': 'Username must be at least 3 characters'}), 400
        
        if not email or '@' not in email:
            return jsonify({'success': False, 'error': 'Valid email is required'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'error': 'Email already registered'}), 400
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Flush to get the user.id before commit
        
        # Initialize first level as unlocked
        first_level = UserProgress(user_id=user.id, level_id=1, unlocked=True)
        db.session.add(first_level)
        
        db.session.commit()
        
        # Log in the user
        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Log in an existing user"""
    try:
        data = request.json
        username_or_email = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return jsonify({'success': False, 'error': 'Username/email and password required'}), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'success': False, 'error': 'Invalid username/email or password'}), 401
        
        # Log in user
        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Logged in successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Log out current user"""
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/auth/current_user')
def get_current_user():
    """Get currently logged in user"""
    if current_user.is_authenticated:
        return jsonify({
            'success': True,
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'created_at': current_user.created_at.isoformat() if current_user.created_at else None
            }
        })
    return jsonify({'success': True, 'authenticated': False})

@app.route('/api/auth/delete_account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account and all associated data"""
    try:
        user_id = current_user.id
        username = current_user.username
        
        # Delete all user progress
        UserProgress.query.filter_by(user_id=user_id).delete()
        
        # Delete all user achievements
        UserAchievement.query.filter_by(user_id=user_id).delete()
        
        # Logout user
        logout_user()
        
        # Delete user account
        User.query.filter_by(id=user_id).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Account {username} has been deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/levels')
@login_required
def get_levels():
    """Get all available levels"""
    # Get user's progress from database
    user_progress = {p.level_id: p for p in current_user.progress}
    
    return jsonify({
        'success': True,
        'levels': [
            {
                'id': level['id'],
                'title': level['title'],
                'difficulty': level['difficulty'],
                'unlocked': user_progress.get(level['id']).unlocked if level['id'] in user_progress else (level['id'] == 1),
                'completed': user_progress.get(level['id']).completed if level['id'] in user_progress else False,
                'stars': user_progress.get(level['id']).stars if level['id'] in user_progress else 0
            }
            for level in LEVELS
        ]
    })

@app.route('/api/level/<int:level_id>')
@login_required
def get_level(level_id):
    """Get specific level details"""
    level = next((l for l in LEVELS if l['id'] == level_id), None)
    if not level:
        return jsonify({'success': False, 'error': 'Level not found'}), 404
    
    # Check if unlocked
    progress = UserProgress.query.filter_by(user_id=current_user.id, level_id=level_id).first()
    if level_id > 1 and (not progress or not progress.unlocked):
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
@login_required
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
        
        # Get or create progress record
        progress = UserProgress.query.filter_by(user_id=current_user.id, level_id=level_id).first()
        if not progress:
            progress = UserProgress(user_id=current_user.id, level_id=level_id, unlocked=True)
            db.session.add(progress)
        
        # Increment attempts
        progress.attempts += 1
        
        if result['passed']:
            # Get old progress for achievement comparison
            old_progress = current_user.get_progress_summary()
            
            # Update progress
            old_stars = progress.stars
            progress.completed = True
            progress.stars = max(progress.stars, result['stars'])
            progress.completed_at = datetime.utcnow()
            
            # Store solution if it's better
            num_states = len(dfa_data['states'])
            if progress.best_states is None or num_states < progress.best_states:
                progress.best_states = num_states
                progress.set_solution(dfa_data)
            
            # Unlock next level
            next_level_id = level_id + 1
            if next_level_id <= len(LEVELS):
                next_progress = UserProgress.query.filter_by(
                    user_id=current_user.id, level_id=next_level_id
                ).first()
                if not next_progress:
                    next_progress = UserProgress(
                        user_id=current_user.id,
                        level_id=next_level_id,
                        unlocked=True
                    )
                    db.session.add(next_progress)
                else:
                    next_progress.unlocked = True
            
            db.session.commit()
            
            # Get new progress and check for new achievements
            new_progress = current_user.get_progress_summary()
            new_achievements = get_new_achievements(old_progress, new_progress)
            
            # Save new achievements
            for achievement in new_achievements:
                user_achievement = UserAchievement(
                    user_id=current_user.id,
                    achievement_id=achievement['id']
                )
                db.session.add(user_achievement)
            
            db.session.commit()
            
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
            db.session.commit()
            return jsonify({
                'success': True,
                'passed': False,
                'message': result['message'],
                'test_results': result['test_results'],
                'failed_key': result.get('failed_key')
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/hint/<int:level_id>')
@login_required
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
@login_required
def get_progress():
    """Get player's progress"""
    progress = current_user.get_progress_summary()
    return jsonify({'success': True, 'progress': progress})

@app.route('/api/achievements')
@login_required
def get_achievements():
    """Get player's achievements"""
    # Get user's unlocked achievements
    user_achievements = {a.achievement_id: a for a in current_user.achievements}
    
    achievements_list = []
    for achievement in ACHIEVEMENTS:
        achievement_data = {
            'id': achievement['id'],
            'title': achievement['title'],
            'description': achievement['description'],
            'icon': achievement['icon'],
            'unlocked': achievement['id'] in user_achievements
        }
        if achievement['id'] in user_achievements:
            achievement_data['unlocked_at'] = user_achievements[achievement['id']].unlocked_at.isoformat()
        achievements_list.append(achievement_data)
    
    return jsonify({
        'success': True,
        'achievements': achievements_list,
        'total': len(user_achievements)
    })

@app.route('/api/reset_progress', methods=['POST'])
@login_required
def reset_progress():
    """Reset all progress"""
    # Delete all progress and achievements
    UserProgress.query.filter_by(user_id=current_user.id).delete()
    UserAchievement.query.filter_by(user_id=current_user.id).delete()
    
    # Re-initialize first level
    first_level = UserProgress(user_id=current_user.id, level_id=1, unlocked=True)
    db.session.add(first_level)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Progress reset'})

@app.route('/api/leaderboard')
@login_required
def get_leaderboard():
    """Get top players leaderboard"""
    users = User.query.all()
    leaderboard = []
    
    for user in users:
        summary = user.get_progress_summary()
        leaderboard.append({
            'username': user.username,
            'completed_levels': summary['completed_levels'],
            'total_stars': summary['total_stars'],
            'achievements': len(user.achievements)
        })
    
    # Sort by total stars, then by completed levels
    leaderboard.sort(key=lambda x: (x['total_stars'], x['completed_levels']), reverse=True)
    
    return jsonify({
        'success': True,
        'leaderboard': leaderboard[:10]  # Top 10 players
    })

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
