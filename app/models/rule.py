from app import db
from datetime import datetime, time

class Rule(db.Model):
    """Rules for alert triggering based on time windows"""
    __tablename__ = 'rules'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    geofence_id = db.Column(db.Integer, db.ForeignKey('geofences.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.Time, nullable=False)  # e.g., '00:00:00'
    end_time = db.Column(db.Time, nullable=False)    # e.g., '06:00:00'
    threshold_minutes = db.Column(db.Integer, default=10)
    enabled = db.Column(db.Boolean, default=True)
    message_template = db.Column(db.Text, nullable=True)
    alert_immediately_on_exit = db.Column(db.Boolean, default=False)
    days_of_week = db.Column(db.String(20), default='all')  # 'all', 'weekdays', 'weekends', or specific days
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_time_window_active(self, current_time=None):
        """Check if current time is within the rule's time window"""
        if not current_time:
            current_time = datetime.now().time()
        
        # Handle time windows that span midnight (e.g., 22:00 - 06:00)
        if self.start_time > self.end_time:
            # Time window spans midnight
            return current_time >= self.start_time or current_time <= self.end_time
        else:
            # Normal time window
            return self.start_time <= current_time <= self.end_time
    
    def is_day_allowed(self, current_date=None):
        """Check if current day is allowed based on days_of_week setting"""
        if not current_date:
            current_date = datetime.now()
        
        if self.days_of_week == 'all':
            return True
        elif self.days_of_week == 'weekdays':
            return current_date.weekday() < 5  # Monday-Friday
        elif self.days_of_week == 'weekends':
            return current_date.weekday() >= 5  # Saturday-Sunday
        else:
            # Specific days: e.g., "0,1,2" for Mon, Tue, Wed
            days = [int(d) for d in self.days_of_week.split(',')]
            return current_date.weekday() in days
    
    def should_trigger_alert(self, current_time=None, current_date=None):
        """Determine if alert should be triggered based on rule"""
        if not self.enabled:
            return False
        
        if not self.is_day_allowed(current_date):
            return False
        
        if not self.is_time_window_active(current_time):
            return False
        
        return True
    
    def to_dict(self):
        """Convert rule to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'geofence_id': self.geofence_id,
            'name': self.name,
            'start_time': self.start_time.strftime('%H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M:%S') if self.end_time else None,
            'threshold_minutes': self.threshold_minutes,
            'enabled': self.enabled,
            'message_template': self.message_template,
            'alert_immediately_on_exit': self.alert_immediately_on_exit,
            'days_of_week': self.days_of_week,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Rule {self.name} ({self.start_time}-{self.end_time})>'



