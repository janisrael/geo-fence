from app import create_app, db
from config import Config

app = create_app(Config)

if __name__ == '__main__':
    # Create database tables on startup
    with app.app_context():
        db.create_all()
    
    app.run(
        host='0.0.0.0',
        port=app.config['APP_PORT'],
        debug=app.config['APP_DEBUG']
    )



