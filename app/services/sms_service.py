from app import db
from app.models import Device, User, Alert
from twilio.rest import Client
from datetime import datetime
from flask import current_app

class SMSService:
    """Service for sending SMS alerts via Twilio"""
    
    def __init__(self):
        """Initialize Twilio client"""
        self.account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        self.auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        self.from_number = current_app.config.get('TWILIO_FROM_NUMBER')
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
    
    def send_alert_sms(self, alert_id, parent_user_ids=None):
        """
        Send SMS alert to parents
        
        Args:
            alert_id: Alert ID
            parent_user_ids: List of parent user IDs (optional, will auto-detect if not provided)
            
        Returns:
            list: List of sent message SIDs
        """
        if not self.client:
            current_app.logger.warning("Twilio not configured, skipping SMS")
            return []
        
        alert = Alert.query.get(alert_id)
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")
        
        if alert.message_sent:
            current_app.logger.info(f"Alert {alert_id} already sent")
            return []
        
        device = alert.device
        child_user = device.user
        
        # Get parent users
        if parent_user_ids is None:
            # Get parents of this child
            if child_user.role == 'child' and child_user.parent_id:
                parent_user_ids = [child_user.parent_id]
                # Also get any other parent linked to this child
                parents = User.query.filter_by(id=child_user.parent_id).all()
            else:
                # If this is a parent alert, send to themselves
                parent_user_ids = [child_user.id]
                parents = [child_user]
        else:
            parents = User.query.filter(User.id.in_(parent_user_ids)).all()
        
        sent_messages = []
        
        for parent in parents:
            if not parent.phone:
                current_app.logger.warning(f"Parent {parent.id} has no phone number")
                continue
            
            try:
                # Send SMS
                message = self.client.messages.create(
                    body=alert.message or self._format_default_message(alert, child_user),
                    from_=self.from_number,
                    to=parent.phone
                )
                
                sent_messages.append(message.sid)
                current_app.logger.info(f"Sent SMS to {parent.phone}: {message.sid}")
                
            except Exception as e:
                current_app.logger.error(f"Failed to send SMS to {parent.phone}: {str(e)}")
        
        # Mark alert as sent
        if sent_messages:
            alert.mark_sent()
            db.session.commit()
        
        return sent_messages
    
    def _format_default_message(self, alert, user):
        """Format default alert message"""
        map_url = f"https://maps.google.com/?q={alert.latitude},{alert.longitude}"
        timestamp = alert.timestamp.strftime('%I:%M %p on %B %d') if alert.timestamp else 'now'
        
        alert_type_messages = {
            'outside': f"{user.name} is outside the safe zone",
            'tamper': f"⚠️ Possible tampering detected on {user.name}'s device",
            'heartbeat_lost': f"No contact with {user.name}'s device",
            'device_offline': f"{user.name}'s device is offline"
        }
        
        main_message = alert_type_messages.get(alert.alert_type, "Alert triggered")
        
        return (
            f"🚨 {main_message} at {timestamp}. "
            f"Location: {map_url}"
        )
    
    def send_custom_sms(self, to_phone, message):
        """
        Send custom SMS
        
        Args:
            to_phone: Phone number to send to
            message: Message content
            
        Returns:
            message SID
        """
        if not self.client:
            raise RuntimeError("Twilio not configured")
        
        message_obj = self.client.messages.create(
            body=message,
            from_=self.from_number,
            to=to_phone
        )
        
        return message_obj.sid
    
    def send_verification_code(self, phone, code):
        """
        Send verification code SMS
        
        Args:
            phone: Phone number
            code: Verification code
            
        Returns:
            message SID
        """
        message = f"Your verification code is: {code}"
        return self.send_custom_sms(phone, message)



