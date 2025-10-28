from flask import Blueprint, jsonify, request, current_app
from app.utils.auth_decorator import jwt_required, get_jwt_identity
from app.models import Device
from app.services import LocationService, SMSService, GeofenceService
from datetime import datetime

bp = Blueprint('api', __name__)

@bp.route('/status')
def status():
    """API status endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Geofence Tracking API',
        'version': '1.0.0'
    })

@bp.route('/location', methods=['POST'])
@jwt_required
def receive_location(**kwargs):
    """Receive location data from child device"""
    try:
        data = request.json
        user_id = kwargs.get('user_id')
        
        # Get or create device
        device = Device.query.filter_by(user_id=user_id, device_token=data.get('device_token')).first()
        
        if not device:
            # Create new device
            device = Device(
                user_id=user_id,
                device_token=data.get('device_token', 'web'),
                platform=data.get('platform', 'web')
            )
            from app import db
            db.session.add(device)
            db.session.commit()
        
        # Validate required fields
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude is None or longitude is None:
            return jsonify({'status': 'error', 'message': 'Latitude and longitude required'}), 400
        
        # Save location
        location = LocationService.save_location(
            device_id=device.id,
            latitude=latitude,
            longitude=longitude,
            accuracy=data.get('accuracy'),
            altitude=data.get('altitude'),
            speed=data.get('speed'),
            heading=data.get('heading')
        )
        
        # Check if alert should be triggered
        should_alert, rule, message = LocationService.should_trigger_alert(device.id, location)
        
        if should_alert:
            # Create alert
            from app.models import Alert
            alert = Alert(
                device_id=device.id,
                geofence_id=location.nearest_geofence_id,
                alert_type='outside',
                latitude=location.latitude,
                longitude=location.longitude,
                message=message
            )
            from app import db
            db.session.add(alert)
            db.session.commit()
            
            # Broadcast real-time alert
            try:
                from app.blueprints.realtime import broadcast_alert
                broadcast_alert(alert.to_dict())
            except Exception as e:
                current_app.logger.error(f"Failed to broadcast alert: {str(e)}")
            
            # Send SMS
            try:
                sms_service = SMSService()
                sms_service.send_alert_sms(alert.id)
            except Exception as e:
                current_app.logger.error(f"Failed to send SMS: {str(e)}")
        
        return jsonify({
            'status': 'ok',
            'message': 'Location received',
            'location': location.to_dict(),
            'alert_triggered': should_alert
        })
        
    except Exception as e:
        current_app.logger.error(f"Error processing location: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/heartbeat', methods=['POST'])
@jwt_required
def heartbeat(**kwargs):
    """Device heartbeat endpoint"""
    try:
        data = request.json
        user_id = kwargs.get('user_id')
        
        device_token = data.get('device_token', 'web')
        device = Device.query.filter_by(user_id=user_id, device_token=device_token).first()
        
        if device:
            LocationService.check_device_heartbeat(device.id)
        
        # Check for offline devices
        offline_devices = LocationService.find_offline_devices()
        
        return jsonify({
            'status': 'ok',
            'message': 'Heartbeat received',
            'device_online': device and device.status == 'online'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error processing heartbeat: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/devices', methods=['GET'])
@jwt_required
def get_devices(**kwargs):
    """Get user's devices"""
    try:
        user_id = kwargs.get('user_id')
        devices = Device.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'status': 'ok',
            'devices': [device.to_dict() for device in devices]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting devices: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/alerts', methods=['GET'])
@jwt_required
def get_alerts(**kwargs):
    """Get user's alerts"""
    try:
        user_id = kwargs.get('user_id')
        from app.models import Alert
        
        # Get device IDs for this user
        user_devices = Device.query.filter_by(user_id=user_id).all()
        device_ids = [device.id for device in user_devices]
        
        alerts = Alert.query.filter(Alert.device_id.in_(device_ids)).order_by(Alert.timestamp.desc()).limit(50).all()
        
        return jsonify({
            'status': 'ok',
            'alerts': [alert.to_dict() for alert in alerts]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting alerts: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@jwt_required
def acknowledge_alert(alert_id, **kwargs):
    """Acknowledge an alert"""
    try:
        from app.models import Alert
        alert = Alert.query.get(alert_id)
        
        if not alert:
            return jsonify({'status': 'error', 'message': 'Alert not found'}), 404
        
        user_id = kwargs.get('user_id')
        alert.acknowledge(user_id)
        
        from app import db
        db.session.commit()
        
        return jsonify({'status': 'ok', 'message': 'Alert acknowledged'})
        
    except Exception as e:
        current_app.logger.error(f"Error acknowledging alert: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

