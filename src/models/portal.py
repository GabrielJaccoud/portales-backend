from src.models.user import db
from datetime import datetime

class Portal(db.Model):
    __tablename__ = 'portals'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    creator_id = db.Column(db.String(128), db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    is_public = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Campos JSON para dados complexos
    ai_analysis = db.Column(db.JSON, nullable=True)
    ar_effects = db.Column(db.JSON, nullable=True)
    
    # Relacionamentos
    reviews = db.relationship('Review', backref='portal', lazy=True, cascade='all, delete-orphan')
    explorations = db.relationship('Exploration', backref='portal', lazy=True)
    tags = db.relationship('Tag', secondary='portal_tags', backref='portals')

    def __repr__(self):
        return f'<Portal {self.title}>'

    def to_dict(self, include_creator=True, include_category=True, include_tags=True, include_stats=True):
        portal_dict = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'thumbnail_url': self.thumbnail_url,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
            'ai_analysis': self.ai_analysis,
            'ar_effects': self.ar_effects
        }
        
        if include_creator and self.creator:
            portal_dict['creator'] = {
                'id': self.creator.id,
                'name': self.creator.name,
                'avatar_url': self.creator.avatar_url,
                'is_verified': self.creator.is_verified
            }
        
        if include_category and self.category:
            portal_dict['category'] = self.category.to_dict()
        
        if include_tags:
            portal_dict['tags'] = [tag.to_dict() for tag in self.tags]
        
        if include_stats:
            portal_dict['stats'] = {
                'views_count': 0,  # TODO: Implementar contagem de visualizações
                'likes_count': len(self.liked_by),
                'favorites_count': len(self.favorited_by),
                'rating_average': self.get_average_rating(),
                'rating_count': len(self.reviews)
            }
        
        return portal_dict
    
    def get_average_rating(self):
        if not self.reviews:
            return 0.0
        total = sum(review.rating for review in self.reviews)
        return round(total / len(self.reviews), 1)

# Tabela de associação para tags
portal_tags = db.Table('portal_tags',
    db.Column('portal_id', db.Integer, db.ForeignKey('portals.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

