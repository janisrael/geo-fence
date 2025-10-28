from app import db
from datetime import datetime

class Device(db.Model):
    """Device model for tracking child devices"""
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_token = db.Column(db.String(255), nullable=False, unique=True)
    platform = db.Column(db.String(50), nullable=False)  # 'web', 'android', 'ios'
    child_name = db.Column(db.String(100), nullable=True)  # Name of the child being tracked
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='online')  # 'online' or 'offline'
    battery_level = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    locations = db.relationship('Location', foreign_keys='Location.device_id', backref=db.backref('device', lazy='select'), lazy='dynamic', cascade='all, delete-orphan', order_by='Location.timestamp.desc()')
    alerts = db.relationship('Alert', foreign_keys='Alert.device_id', lazy='dynamic', cascade='all, delete-orphan', backref='device_obj')
    
    def is_online(self):
        """Check if device is online based on last_seen"""
        if not self.last_seen:
            return False
        
        # Consider offline if no heartbeat for 30 minutes
        from datetime import timedelta
        timeout = datetime.utcnow() - timedelta(minutes=30)
        return self.last_seen > timeout
    
    def get_last_location(self):
        """Get the most recent location for this device"""
        if self.locations.count() > 0:
            return self.locations.first()
        return None
    
    def to_dict(self):
        """Convert device to dictionary"""
        last_location = self.get_last_location()
        last_location_dict = None
        if last_location:
            last_location_dict = {
                'latitude': last_location.latitude,
                'longitude': last_location.longitude,
                'timestamp': last_location.timestamp.isoformat() if last_location.timestamp else None
            }
        
        # Get child name (use child_name field or fall back to device_token)
        child_name = self.child_name or self.device_token
        # Replace "test" with "Child-1" for display
        if child_name.lower() == 'test':
            child_name = 'Child-1'
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_token': self.device_token,
            'platform': self.platform,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'status': 'online' if self.is_online() else 'offline',
            'battery_level': self.battery_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_location': last_location_dict,
            'child_name': child_name
        }
    
    def __repr__(self):
        return f'<Device {self.device_token} ({self.platform})>'

