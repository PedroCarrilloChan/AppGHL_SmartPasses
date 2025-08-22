from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """User model for future authentication features."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Ensure password hash field has length of at least 256
    password_hash = db.Column(db.String(256))
    
    def __repr__(self):
        return f'<User {self.username}>'
