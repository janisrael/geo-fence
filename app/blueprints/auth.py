from flask import Blueprint, jsonify, request, current_app
from app.services import AuthService

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'phone', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'{field} is required'}), 400
        
        # Register user
        user = AuthService.register_user(
            name=data['name'],
            phone=data['phone'],
            email=data.get('email'),
            password=data['password'],
            role=data['role'],
            parent_id=data.get('parent_id')
        )
        
        # Generate token
        token = AuthService.generate_token(user)
        
        return jsonify({
            'status': 'ok',
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'token': token
        })
        
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error registering user: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.json
        
        # Validate required fields
        if 'phone' not in data or 'password' not in data:
            return jsonify({'status': 'error', 'message': 'Phone and password required'}), 400
        
        # Authenticate user
        success, user, token = AuthService.authenticate_user(data['phone'], data['password'])
        
        if not success:
            return jsonify({'status': 'error', 'message': 'Invalid phone or password'}), 401
        
        return jsonify({
            'status': 'ok',
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': token
        })
        
    except Exception as e:
        current_app.logger.error(f"Error logging in: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user info (requires authentication via header)"""
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'No authorization token'}), 401
        
        token = auth_header.split(' ')[1]
        user = AuthService.get_user_from_token(token)
        
        if not user:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        return jsonify({
            'status': 'ok',
            'user': user.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting current user: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

