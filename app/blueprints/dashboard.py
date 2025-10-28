from flask import Blueprint, render_template, jsonify, request
from app.utils.auth_decorator import jwt_required, get_jwt_identity
from app.services import GeofenceService
from app.models import Geofence, Rule, Device, User

bp = Blueprint('dashboard', __name__)

@bp.route('/')
def index():
    """Dashboard home"""
    return render_template('dashboard.html')

@bp.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@bp.route('/child')
def child_app():
    """Child tracking app"""
    return render_template('child_app.html')

@bp.route('/geofence')
def geofence_config():
    """Geofence configuration"""
    return render_template('geofence.html')

@bp.route('/alerts')
def alerts():
    """View alerts"""
    return render_template('alerts.html')

@bp.route('/api/geofences', methods=['GET'])
@jwt_required
def get_geofences(**kwargs):
    """Get user's geofences"""
    try:
        user_id = kwargs.get('user_id')
        geofences = Geofence.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'status': 'ok',
            'geofences': [geofence.to_dict() for geofence in geofences]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/geofences', methods=['POST'])
@jwt_required
def create_geofence(**kwargs):
    """Create new geofence"""
    try:
        data = request.json
        user_id = kwargs.get('user_id')
        
        required = ['name', 'center_latitude', 'center_longitude', 'radius_meters']
        for field in required:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'{field} is required'}), 400
        
        geofence = GeofenceService.create_geofence(
            user_id=user_id,
            name=data['name'],
            center_latitude=data['center_latitude'],
            center_longitude=data['center_longitude'],
            radius_meters=data['radius_meters'],
            label=data.get('label')
        )
        
        return jsonify({
            'status': 'ok',
            'geofence': geofence.to_dict()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/geofences/<int:geofence_id>', methods=['PUT'])
@jwt_required
def update_geofence(geofence_id, **kwargs):
    """Update existing geofence"""
    try:
        data = request.json
        geofence = GeofenceService.update_geofence(geofence_id, **data)
        
        return jsonify({
            'status': 'ok',
            'geofence': geofence.to_dict()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/geofences/<int:geofence_id>', methods=['DELETE'])
@jwt_required
def delete_geofence(geofence_id, **kwargs):
    """Delete geofence"""
    try:
        deleted = GeofenceService.delete_geofence(geofence_id)
        
        if deleted:
            return jsonify({'status': 'ok', 'message': 'Geofence deleted'})
        else:
            return jsonify({'status': 'error', 'message': 'Geofence not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/rules', methods=['GET'])
@jwt_required
def get_rules(**kwargs):
    """Get user's rules"""
    try:
        user_id = kwargs.get('user_id')
        rules = Rule.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'status': 'ok',
            'rules': [rule.to_dict() for rule in rules]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

