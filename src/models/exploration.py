from src.models.user import db
from datetime import datetime

class Exploration(db.Model):
    __tablename__ = 'explorations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(128), db.ForeignKey('users.id'), nullable=False)
    portal_id = db.Column(db.Integer, db.ForeignKey('portals.id'), nullable=True)
    scan_image_url = db.Column(db.String(500), nullable=True)
    detection_confidence = db.Column(db.Float, nullable=True)
    ar_activated = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Exploration {self.id} by User {self.user_id}>'

    def to_dict(self, include_portal=True):
        exploration_dict = {
            'id': self.id,
            'scan_image_url': self.scan_image_url,
            'detection_confidence': self.detection_confidence,
            'ar_activated': self.ar_activated,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None
        }
        
        if include_portal and self.portal:
            exploration_dict['portal'] = {
                'id': self.portal.id,
                'title': self.portal.title,
                'image_url': self.portal.image_url,
                'thumbnail_url': self.portal.thumbnail_url
            }
        
        return exploration_dict

