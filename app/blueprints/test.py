from flask import Blueprint, jsonify, request
from app.services import LocationService
from app.models import User, Device

bp = Blueprint('test', __name__)

@bp.route('/test-alert', methods=['POST'])
def test_alert():
    """
    Test endpoint to manually trigger an alert
    This simulates a child leaving the geofence
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id required'}), 400
        
        # Get or create test device
        device = Device.query.filter_by(user_id=user_id).first()
        if not device:
            device = Device(
                user_id=user_id,
                device_token='test-device',
                platform='test'
            )
            from app import db
            db.session.add(device)
            db.session.commit()
        
        # Get the geofence you created
        from app.models import Geofence
        geofence = Geofence.query.filter_by(user_id=user_id).first()
        
        if not geofence:
            return jsonify({
                'status': 'error', 
                'message': 'No geofence found. Create one first at /dashboard/geofence'
            }), 400
        
        # Simulate location OUTSIDE the geofence
        # Place it 1km away from center
        import math
        center_lat = geofence.center_latitude
        center_lon = geofence.center_longitude
        
        # Calculate a point 1km south of center
        test_lat = center_lat - (1000 / 111000)  # ~1km south
        test_lon = center_lon
        
        # Save this location
        location = LocationService.save_location(
            device_id=device.id,
            latitude=test_lat,
            longitude=test_lon,
            accuracy=10
        )
        
        # Check if should trigger alert
        should_alert, rule, message = LocationService.should_trigger_alert(device.id, location)
        
        if should_alert:
            # Create alert manually (skip time window check for testing)
            from app.models import Alert
            alert = Alert(
                device_id=device.id,
                geofence_id=geofence.id,
                alert_type='outside',
                latitude=test_lat,
                longitude=test_lon,
                message=message or 'Test alert: Child is outside safe zone'
            )
            from app import db
            db.session.add(alert)
            db.session.commit()
            
            # Try to send SMS
            from app.services import SMSService
            try:
                sms_service = SMSService()
                sms_service.send_alert_sms(alert.id)
            except Exception as e:
                return jsonify({
                    'status': 'ok',
                    'message': f'Alert created (SMS skipped: {str(e)})',
                    'alert_id': alert.id,
                    'location': {'lat': test_lat, 'lon': test_lon}
                })
            
            return jsonify({
                'status': 'ok',
                'message': 'Alert triggered and SMS sent!',
                'alert_id': alert.id,
                'location': {'lat': test_lat, 'lon': test_lon}
            })
        else:
            return jsonify({
                'status': 'info',
                'message': 'Location logged but no alert triggered (not in alert window or not outside long enough)',
                'location': location.to_dict()
            })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

