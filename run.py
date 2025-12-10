from app import create_app, db
from config import Config

app = create_app(Config)

if __name__ == '__main__':
    # Create database tables on startup
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            # Handle case where tables already exist (common in production)
            error_str = str(e).lower()
            if 'already exists' in error_str or 'table' in error_str:
                # Tables already exist, verify they're accessible
                try:
                    from app.models.user import User
                    # Try to query to verify tables exist and are accessible
                    User.query.limit(1).all()
                except Exception:
                    # If tables don't exist or aren't accessible, log and continue
                    print(f"Warning: Database tables may already exist: {e}")
            else:
                # Re-raise unexpected errors
                print(f"Error: Database initialization failed: {e}")
                raise e
    
    app.run(
        host='0.0.0.0',
        port=app.config['APP_PORT'],
        debug=app.config['APP_DEBUG']
    )



