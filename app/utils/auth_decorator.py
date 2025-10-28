from functools import wraps
from flask import request, jsonify
from app.services import AuthService

def jwt_required(f=None):
    """Custom JWT decorator to replace Flask-JWT-Extended"""
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # Get token from header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'status': 'error', 'message': 'No authorization token'}), 401
            
            token = auth_header.split(' ')[1]
            
            # Verify token
            valid, payload = AuthService.verify_token(token)
            if not valid:
                return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
            
            # Add user_id to kwargs
            kwargs['user_id'] = payload.get('user_id')
            
            return func(*args, **kwargs)
        return decorated_function
    
    if f is None:
        return decorator
    else:
        return decorator(f)

def get_jwt_identity():
    """Get current user ID from token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    valid, payload = AuthService.verify_token(token)
    
    if valid:
        return payload.get('user_id')
    return None

