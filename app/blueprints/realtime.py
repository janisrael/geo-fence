from flask import Blueprint, Response, request, current_app
from app.models import Alert, User
from app import db
import json
import threading
from datetime import datetime, timedelta

bp = Blueprint('realtime', __name__)

# Store active SSE connections by user_id
active_connections = {}
connections_lock = threading.Lock()

def broadcast_alert(alert):
    """Broadcast new alert to all connected clients"""
    # The SSE stream will pick up new alerts on the next poll
    # This function is kept for future webhook/push notifications
    pass

@bp.route('/events', methods=['GET'])
def stream_alerts():
    """Server-Sent Events endpoint for real-time alerts"""
    user_id = request.args.get('user_id')
    if not user_id:
        return Response(
            f"data: {json.dumps({'error': 'user_id required'})}\n\n",
            mimetype='text/event-stream'
        )
    
    # Get the Flask app instance
    app = current_app._get_current_object()
    
    def generate():
        """Generator function for SSE stream"""
        # Track this connection
        connection_id = f"{user_id}_{id(generate)}"
        
        try:
            last_alert_id = None
            
            # Send initial connection confirmation
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Real-time alert stream active'})}\n\n"
            
            import time
            while True:
                try:
                    # Use app context for database queries
                    with app.app_context():
                        from app.models import Device
                        devices = Device.query.filter_by(user_id=user_id).all()
                        device_ids = [d.id for d in devices]
                        
                        if device_ids:
                            alerts = Alert.query.filter(
                                Alert.device_id.in_(device_ids)
                            ).order_by(
                                Alert.timestamp.desc()
                            ).limit(5).all()
                        else:
                            alerts = []
                        
                        # Send new alerts
                        for alert in alerts:
                            if last_alert_id is None or alert.id > last_alert_id:
                                alert_dict = alert.to_dict()
                                alert_dict['type'] = 'new_alert'
                                yield f"data: {json.dumps(alert_dict)}\n\n"
                                last_alert_id = alert.id
                    
                    # Send heartbeat every 30 seconds to keep connection alive
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
                    
                    # Sleep for 1 second before checking again (faster polling)
                    time.sleep(1)
                    
                except Exception as e:
                    # Log error but keep connection alive
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                    time.sleep(5)
                
        except GeneratorExit:
            # Client disconnected
            pass
        except Exception as e:
            print(f"SSE connection error: {e}")
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

