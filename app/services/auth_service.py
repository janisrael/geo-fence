from app import db
from app.models import User
from datetime import datetime, timedelta
import jwt
from flask import current_app

class AuthService:
    """Service for authentication and authorization"""
    
    @staticmethod
    def register_user(name, phone, email, password, role='child', parent_id=None):
        """
        Register a new user
        
        Args:
            name: User name
            phone: Phone number
            email: Email address
            password: Plain password
            role: 'child' or 'parent'
            parent_id: Parent user ID (if role is 'child')
            
        Returns:
            User object
        """
        # Check if phone already exists
        if User.query.filter_by(phone=phone).first():
            raise ValueError(f"Phone number {phone} already registered")
        
        # Check if email already exists
        if email and User.query.filter_by(email=email).first():
            raise ValueError(f"Email {email} already registered")
        
        # Validate parent_id if provided
        if parent_id:
            parent = User.query.get(parent_id)
            if not parent or parent.role != 'parent':
                raise ValueError("Invalid parent user")
        
        # Create user
        user = User(
            name=name,
            phone=phone,
            email=email,
            role=role,
            parent_id=parent_id
        )
        
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def authenticate_user(phone, password):
        """
        Authenticate user with phone and password
        
        Args:
            phone: Phone number
            password: Plain password
            
        Returns:
            tuple: (success: bool, user: User or None, token: str or None)
        """
        user = User.query.filter_by(phone=phone).first()
        
        if not user:
            return (False, None, None)
        
        if not user.active:
            return (False, None, None)
        
        if not user.check_password(password):
            return (False, None, None)
        
        # Generate JWT token
        token = AuthService.generate_token(user)
        
        return (True, user, token)
    
    @staticmethod
    def generate_token(user):
        """
        Generate JWT token for user
        
        Args:
            user: User object
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user.id,
            'phone': user.phone,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        secret_key = current_app.config.get('JWT_SECRET_KEY')
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        return token
    
    @staticmethod
    def verify_token(token):
        """
        Verify JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            tuple: (valid: bool, user_data: dict or None)
        """
        try:
            secret_key = current_app.config.get('JWT_SECRET_KEY')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            return (True, payload)
        except jwt.ExpiredSignatureError:
            return (False, {'error': 'Token expired'})
        except jwt.InvalidTokenError:
            return (False, {'error': 'Invalid token'})
        except Exception as e:
            return (False, {'error': str(e)})
    
    @staticmethod
    def get_user_from_token(token):
        """
        Get user object from JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            User object or None
        """
        valid, payload = AuthService.verify_token(token)
        
        if not valid:
            return None
        
        user_id = payload.get('user_id')
        user = User.query.get(user_id)
        
        return user
    
    @staticmethod
    def update_user_profile(user_id, name=None, email=None, phone=None):
        """
        Update user profile
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            Updated User object
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        if name is not None:
            user.name = name
        if email is not None:
            # Check if email is taken by another user
            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != user_id:
                raise ValueError(f"Email {email} already in use")
            user.email = email
        if phone is not None:
            # Check if phone is taken by another user
            existing = User.query.filter_by(phone=phone).first()
            if existing and existing.id != user_id:
                raise ValueError(f"Phone {phone} already in use")
            user.phone = phone
        
        db.session.commit()
        
        return user
    
    @staticmethod
    def deactivate_user(user_id):
        """Deactivate a user account"""
        user = User.query.get(user_id)
        if user:
            user.active = False
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_user_children(parent_id):
        """Get all children for a parent"""
        return User.query.filter_by(parent_id=parent_id, role='child').all()
    
    @staticmethod
    def link_child_to_parent(child_id, parent_id):
        """Link a child user to a parent"""
        child = User.query.get(child_id)
        parent = User.query.get(parent_id)
        
        if not child or not parent:
            raise ValueError("Invalid child or parent")
        
        if parent.role != 'parent':
            raise ValueError("Parent user must have 'parent' role")
        
        child.parent_id = parent_id
        db.session.commit()
        
        return child



