# Geofence Tracking System

A child safety geofence tracking system built with Flask backend and web frontend.

## Features

- Real-time location tracking
- Geofence monitoring with configurable zones
- SMS alerts via Twilio
- Parent dashboard for configuration and monitoring
- Background operation (web-based)
- Device heartbeat and anti-tamper detection
- Time-based alert rules

## Project Structure

```
geofence/
├── app/               # Flask application
│   ├── models/        # Database models
│   ├── services/      # Business logic
│   ├── blueprints/    # API routes
│   └── utils/         # Helper functions
├── assets/            # Frontend resources
│   ├── css/
│   └── js/
├── templates/         # HTML templates
├── config.py          # Configuration
├── requirements.txt   # Python dependencies
└── run.py            # Application entry point
```

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

4. Configure Twilio credentials in `.env`:
```env
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_NUMBER=+1234567890
```

5. Run the application:
```bash
python run.py
```

6. Access the application:
- API: http://localhost:5000
- Dashboard: http://localhost:5000/dashboard

## Development

### Backend Structure
- `/app/models/` - Database models (User, Device, Geofence, Alert, Rule)
- `/app/services/` - Business logic (Location, Geofence, SMS, Auth)
- `/app/blueprints/` - API routes (API, Auth, Dashboard)
- `/app/utils/` - Helper functions

### Frontend Structure
- `/templates/` - HTML templates
- `/assets/css/` - Stylesheets
- `/assets/js/` - JavaScript modules

## API Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/location` - Receive location data
- `POST /api/heartbeat` - Device heartbeat
- `GET /api/status` - API status

## Phase 2: AI Features (Future)

- Behavioral pattern learning
- Smart alert filtering
- Predictive geofencing
- Voice interaction

## Security

- JWT-based authentication
- Encrypted location data in transit
- Rate limiting on API endpoints
- Input validation and sanitization
- Secure SMS credentials storage

## License

Private project for personal use.

---

**Project**: Geofence Tracking System  
**Version**: 1.0.0  
**Author**: Swordfish Development  
**Architect**: Agimat - Super Debugger AI v1.5



