from src.models.user import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    portal_id = db.Column(db.Integer, db.ForeignKey('portals.id'), nullable=False)
    user_id = db.Column(db.String(128), db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    title = db.Column(db.String(200), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Constraint para garantir que um usuário só pode avaliar um portal uma vez
    __table_args__ = (db.UniqueConstraint('portal_id', 'user_id', name='unique_user_portal_review'),)

    def __repr__(self):
        return f'<Review {self.id} - Portal {self.portal_id} by User {self.user_id}>'

    def to_dict(self, include_user=True):
        review_dict = {
            'id': self.id,
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'is_verified': self.is_verified,
            'helpful_count': self.helpful_count,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None
        }
        
        if include_user and self.user:
            review_dict['user'] = {
                'id': self.user.id,
                'name': self.user.name,
                'avatar_url': self.user.avatar_url
            }
        
        return review_dict

