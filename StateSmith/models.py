from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationship to progress
    progress = db.relationship('UserProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_progress_summary(self):
        """Get summary of user's progress"""
        progress_dict = {}
        for p in self.progress:
            progress_dict[p.level_id] = {
                'completed': p.completed,
                'stars': p.stars,
                'unlocked': p.unlocked,
                'attempts': p.attempts,
                'best_states': p.best_states
            }
        
        completed_levels = sum(1 for p in self.progress if p.completed)
        total_stars = sum(p.stars for p in self.progress)
        
        return {
            'completed_levels': completed_levels,
            'total_stars': total_stars,
            'levels': progress_dict
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class UserProgress(db.Model):
    """Track user progress for each level"""
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    level_id = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    stars = db.Column(db.Integer, default=0)
    unlocked = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)
    best_states = db.Column(db.Integer)
    completed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Store the best DFA solution
    best_solution = db.Column(db.Text)
    
    # Unique constraint: one progress record per user per level
    __table_args__ = (db.UniqueConstraint('user_id', 'level_id', name='unique_user_level'),)
    
    def set_solution(self, dfa_data):
        """Store DFA solution as JSON"""
        self.best_solution = json.dumps(dfa_data)
    
    def get_solution(self):
        """Retrieve DFA solution"""
        if self.best_solution:
            return json.loads(self.best_solution)
        return None
    
    def __repr__(self):
        return f'<UserProgress user={self.user_id} level={self.level_id} stars={self.stars}>'


class UserAchievement(db.Model):
    """Track unlocked achievements for users"""
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.String(50), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: one achievement per user
    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),)
    
    def __repr__(self):
        return f'<UserAchievement user={self.user_id} achievement={self.achievement_id}>'
