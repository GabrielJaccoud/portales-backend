from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(128), primary_key=True)  # Firebase UID
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatar_url = db.Column(db.String(500), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(200), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    portals = db.relationship('Portal', backref='creator', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')
    explorations = db.relationship('Exploration', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # Relacionamentos many-to-many
    liked_portals = db.relationship('Portal', secondary='user_portal_likes', backref='liked_by')
    favorite_portals = db.relationship('Portal', secondary='user_portal_favorites', backref='favorited_by')
    
    # Seguindo/Seguidores
    following = db.relationship(
        'User', 
        secondary='user_follows',
        primaryjoin='User.id == user_follows.c.follower_id',
        secondaryjoin='User.id == user_follows.c.followed_id',
        backref='followers'
    )

    def __repr__(self):
        return f'<User {self.name}>'

    def to_dict(self, include_stats=True):
        user_dict = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'location': self.location,
            'website': self.website,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None
        }
        
        if include_stats:
            user_dict['stats'] = {
                'portals_count': len(self.portals),
                'followers_count': len(self.followers),
                'following_count': len(self.following)
            }
        
        return user_dict

# Tabelas de associação para relacionamentos many-to-many
user_portal_likes = db.Table('user_portal_likes',
    db.Column('user_id', db.String(128), db.ForeignKey('users.id'), primary_key=True),
    db.Column('portal_id', db.Integer, db.ForeignKey('portals.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

user_portal_favorites = db.Table('user_portal_favorites',
    db.Column('user_id', db.String(128), db.ForeignKey('users.id'), primary_key=True),
    db.Column('portal_id', db.Integer, db.ForeignKey('portals.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

user_follows = db.Table('user_follows',
    db.Column('follower_id', db.String(128), db.ForeignKey('users.id'), primary_key=True),
    db.Column('followed_id', db.String(128), db.ForeignKey('users.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

