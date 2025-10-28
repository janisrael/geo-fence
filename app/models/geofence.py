from app import db
from datetime import datetime

class Geofence(db.Model):
    """Geofence model for defining safe zones"""
    __tablename__ = 'geofences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    center_latitude = db.Column(db.Float, nullable=False)
    center_longitude = db.Column(db.Float, nullable=False)
    radius_meters = db.Column(db.Float, nullable=False)
    label = db.Column(db.String(50), nullable=True)  # 'home', 'school', 'custom', etc.
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    alerts = db.relationship('Alert', backref='geofence', lazy='dynamic', cascade='all, delete-orphan')
    rules = db.relationship('Rule', backref='geofence', lazy='dynamic', cascade='all, delete-orphan')
    
    def contains_point(self, latitude, longitude):
        """Check if a point is inside this geofence"""
        from geopy.distance import geodesic
        
        center = (self.center_latitude, self.center_longitude)
        point = (latitude, longitude)
        
        distance = geodesic(center, point).meters
        return distance <= self.radius_meters
    
    def get_distance(self, latitude, longitude):
        """Get distance from point to center of geofence"""
        from geopy.distance import geodesic
        
        center = (self.center_latitude, self.center_longitude)
        point = (latitude, longitude)
        
        return geodesic(center, point).meters
    
    def to_dict(self):
        """Convert geofence to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'center_latitude': self.center_latitude,
            'center_longitude': self.center_longitude,
            'radius_meters': self.radius_meters,
            'label': self.label,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Geofence {self.name} (radius: {self.radius_meters}m)>'



