from app import db
from datetime import datetime

class Alert(db.Model):
    """Alert model for tracking safety alerts"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    geofence_id = db.Column(db.Integer, db.ForeignKey('geofences.id'), nullable=True)
    alert_type = db.Column(db.String(50), nullable=False)  # 'outside', 'tamper', 'heartbeat_lost', 'device_offline'
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'sent', 'acknowledged', 'dismissed'
    message_sent = db.Column(db.Boolean, default=False)
    message_sent_at = db.Column(db.DateTime, nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    acknowledged_by_user = db.relationship('User', foreign_keys=[acknowledged_by], lazy='select', backref='acknowledged_alerts')
    
    def acknowledge(self, user_id):
        """Mark alert as acknowledged"""
        self.status = 'acknowledged'
        self.acknowledged_at = datetime.utcnow()
        self.acknowledged_by = user_id
    
    def mark_sent(self):
        """Mark alert as sent"""
        self.message_sent = True
        self.message_sent_at = datetime.utcnow()
        self.status = 'sent'
    
    def to_dict(self):
        """Convert alert to dictionary"""
        # Get child name from device
        child_name = 'child-01'
        try:
            if self.device_obj:
                # Get child_name from device
                child_name = self.device_obj.child_name or self.device_obj.device_token
                # Clean up the name
                if child_name.lower() in ['test', 'web-browser', 'web']:
                    child_name = 'child-01'
        except:
            pass
        
        return {
            'id': self.id,
            'device_id': self.device_id,
            'geofence_id': self.geofence_id,
            'alert_type': self.alert_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'status': self.status,
            'message_sent': self.message_sent,
            'message_sent_at': self.message_sent_at.isoformat() if self.message_sent_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'acknowledged_by': self.acknowledged_by,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'child_name': child_name
        }
    
    def __repr__(self):
        return f'<Alert {self.alert_type} - {self.status}>'

