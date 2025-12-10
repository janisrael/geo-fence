from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initialize extensions
db = SQLAlchemy()

def create_app(config_class=Config):
    """Application factory pattern for Flask"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../assets',
                static_url_path='/static')
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from app.blueprints.api import bp as api_bp
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.dashboard import bp as dashboard_bp
    from app.blueprints.test import bp as test_bp
    from app.blueprints.realtime import bp as realtime_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(test_bp, url_prefix='/test')
    app.register_blueprint(realtime_bp, url_prefix='/api/realtime')
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            # Tables may already exist, verify they're accessible
            try:
                from app.models.user import User
                # Try to query to verify tables exist and are accessible
                User.query.limit(1).all()
            except Exception:
                # If tables don't exist or aren't accessible, re-raise the original error
                raise e
    
    @app.route('/')
    def index():
        return render_template('login.html')
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    return app

