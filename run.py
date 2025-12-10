from app import create_app, db
from config import Config

app = create_app(Config)

if __name__ == '__main__':
    # Create database tables on startup
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
    
    app.run(
        host='0.0.0.0',
        port=app.config['APP_PORT'],
        debug=app.config['APP_DEBUG']
    )



