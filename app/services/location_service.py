from app import db
from app.models import Device, Location, Geofence, Alert, Rule
from datetime import datetime, timedelta
from flask import current_app

class LocationService:
    """Service for handling location tracking and geofence detection"""
    
    @staticmethod
    def save_location(device_id, latitude, longitude, accuracy=None, 
                     altitude=None, speed=None, heading=None):
        """
        Save location data from device
        
        Args:
            device_id: Device ID
            latitude: Latitude
            longitude: Longitude
            accuracy: GPS accuracy in meters
            altitude: Altitude in meters
            speed: Speed in m/s
            heading: Heading in degrees
            
        Returns:
            Location object
        """
        # Validate device exists
        device = Device.query.get(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        
        # Create new location
        location = Location(
            device_id=device_id,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
            altitude=altitude,
            speed=speed,
            heading=heading,
            timestamp=datetime.utcnow()
        )
        
        # Check geofence status
        is_inside, geofence = LocationService._check_geofences(
            device.user_id, latitude, longitude
        )
        
        location.is_inside_geofence = is_inside
        location.nearest_geofence_id = geofence.id if geofence else None
        
        # Update device
        device.last_seen = datetime.utcnow()
        device.status = 'online'
        
        db.session.add(location)
        db.session.commit()
        
        return location
    
    @staticmethod
    def _check_geofences(user_id, latitude, longitude):
        """
        Check if location is inside any geofence
        
        Returns:
            tuple: (is_inside, nearest_geofence)
        """
        geofences = Geofence.query.filter_by(
            user_id=user_id, 
            active=True
        ).all()
        
        nearest_geofence = None
        min_distance = float('inf')
        
        for geofence in geofences:
            is_inside = geofence.contains_point(latitude, longitude)
            distance = geofence.get_distance(latitude, longitude)
            
            if is_inside:
                return (True, geofence)
            
            if distance < min_distance:
                min_distance = distance
                nearest_geofence = geofence
        
        return (False, nearest_geofence)
    
    @staticmethod
    def should_trigger_alert(device_id, location):
        """
        Determine if alert should be triggered based on location and rules
        
        Args:
            device_id: Device ID
            location: Location object
            
        Returns:
            tuple: (should_alert, rule, message)
        """
        device = Device.query.get(device_id)
        if not device:
            return (False, None, None)
        
        # TESTING MODE: Always alert if outside geofence (time restrictions disabled)
        if not location.is_inside_geofence:
            # Check for recent alerts to implement cooldown (10 seconds)
            recent_alerts = Alert.query.filter(
                Alert.device_id == device_id,
                Alert.alert_type == 'outside',
                Alert.timestamp >= datetime.utcnow() - timedelta(seconds=10)
            ).order_by(Alert.timestamp.desc()).first()
            
            # If there's a recent alert, don't trigger another one (cooldown)
            if recent_alerts:
                return (False, None, None)
            
            # Check duration outside geofence (still apply threshold to avoid spam)
            recent_locations = Location.query.filter(
                Location.device_id == device_id,
                Location.timestamp >= datetime.utcnow() - timedelta(minutes=10)
            ).order_by(Location.timestamp.desc()).all()
            
            # Count how long device has been outside
            outside_duration = 0
            for loc in reversed(recent_locations):
                if not loc.is_inside_geofence:
                    outside_duration += 1
            
            # Alert if been outside for at least 2 location updates (avoid immediate spam)
            if outside_duration >= 2:
                message = LocationService._generate_alert_message(location, device, None)
                return (True, None, message)
        
        return (False, None, None)
    
    @staticmethod
    def _generate_alert_message(location, device, rule):
        """Generate alert message based on rule template"""
        if rule and rule.message_template:
            return rule.message_template.format(
                user_name=device.user.name,
                location=f"{location.latitude}, {location.longitude}",
                time=location.timestamp.strftime('%I:%M %p'),
                map_url=f"https://maps.google.com/?q={location.latitude},{location.longitude}"
            )
        
        # Default message for testing mode
        map_url = f"https://maps.google.com/?q={location.latitude},{location.longitude}"
        
        # Get child name
        child_name = device.child_name or device.device_token
        if child_name.lower() in ['test', 'web-browser', 'web']:
            child_name = 'child-01'
        
        return (
            f"Alert: {child_name} is outside safe zone at "
            f"{location.timestamp.strftime('%I:%M %p')}. "
            f"Location: {map_url}"
        )
    
    @staticmethod
    def check_device_heartbeat(device_id):
        """Update device heartbeat"""
        device = Device.query.get(device_id)
        if device:
            device.last_seen = datetime.utcnow()
            device.status = 'online'
            db.session.commit()
    
    @staticmethod
    def find_offline_devices():
        """Find devices that are offline (no heartbeat for 30+ minutes)"""
        timeout = datetime.utcnow() - timedelta(minutes=30)
        devices = Device.query.filter(
            Device.last_seen < timeout,
            Device.status == 'online'
        ).all()
        
        for device in devices:
            device.status = 'offline'
        
        db.session.commit()
        return devices

