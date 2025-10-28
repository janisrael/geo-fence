from app import db
from datetime import datetime

class Location(db.Model):
    """Location tracking model"""
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, nullable=True)  # in meters
    altitude = db.Column(db.Float, nullable=True)
    speed = db.Column(db.Float, nullable=True)  # in m/s
    heading = db.Column(db.Float, nullable=True)  # in degrees
    is_inside_geofence = db.Column(db.Boolean, default=False)
    nearest_geofence_id = db.Column(db.Integer, db.ForeignKey('geofences.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    nearest_geofence = db.relationship('Geofence', foreign_keys=[nearest_geofence_id], lazy='select')
    
    def to_dict(self):
        """Convert location to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'altitude': self.altitude,
            'speed': self.speed,
            'heading': self.heading,
            'is_inside_geofence': self.is_inside_geofence,
            'nearest_geofence_id': self.nearest_geofence_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Location ({self.latitude}, {self.longitude}) at {self.timestamp}>'

