# Gabay - Location Safety & Geofence Tracking System

A professional geofence tracking and location safety system built with Flask backend and modern web frontend. Designed for real-time location monitoring, geofence alerts, and device tracking with SMS notifications via Twilio.

## Features

- **Real-Time Location Tracking**: Continuous GPS monitoring with device heartbeat detection
- **Geofence Monitoring**: Configurable safety zones with entry/exit alerts
- **SMS Alerts**: Instant notifications via Twilio integration
- **Parent Dashboard**: Comprehensive web interface for configuration and monitoring
- **Background Operation**: Web-based tracking that works in the background
- **Device Management**: Multi-device support with anti-tamper detection
- **Time-Based Rules**: Configurable alert rules based on time windows
- **User Authentication**: Secure JWT-based authentication system

## Tech Stack

- **Backend**: Python Flask, SQLAlchemy
- **Frontend**: JavaScript, HTML/CSS
- **Database**: SQLite (with PostgreSQL support)
- **SMS Service**: Twilio API
- **Geolocation**: Geopy for distance calculations
- **Deployment**: Docker, Kubernetes (k3s), Hetzner Cloud

## Quick Start

### Prerequisites

- Python 3.11+
- SQLite (or PostgreSQL for production)
- Twilio account (for SMS alerts)
- Docker (for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/janisrael/geo-fence.git
   cd geo-fence
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database**
   ```bash
   python run.py
   # Database tables will be created automatically
   ```

5. **Run the application**
   ```bash
   python run.py
   # Or with gunicorn for production:
   gunicorn --bind 0.0.0.0:6003 --workers 2 --threads 2 --timeout 120 run:app
   ```

## Environment Variables

See `.env.example` for required environment variables:

- `TWILIO_ACCOUNT_SID`: Twilio account SID
- `TWILIO_AUTH_TOKEN`: Twilio authentication token
- `TWILIO_FROM_NUMBER`: Twilio phone number for sending SMS
- `SECRET_KEY`: Flask session secret key (generate with `openssl rand -hex 32`)
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)

## Deployment

### Kubernetes (Hetzner)

The main branch automatically deploys to Hetzner Kubernetes via GitHub Actions.

**Manual deployment:**
```bash
# Build Docker image
docker build -t gabay:latest .

# Deploy to Kubernetes
kubectl apply -f k8s/
kubectl rollout restart deployment/gabay-app -n gabay
```

### Docker

```bash
# Build image
docker build -t gabay:latest .

# Run container
docker run -d \
  -p 6003:6003 \
  -e TWILIO_ACCOUNT_SID=your-sid \
  -e TWILIO_AUTH_TOKEN=your-token \
  -e TWILIO_FROM_NUMBER=+1234567890 \
  -e SECRET_KEY=your-secret-key \
  gabay:latest
```

## Project Structure

```
geofence/
├── app/                    # Flask application
│   ├── __init__.py        # Application factory
│   ├── models/            # Database models (User, Device, Geofence, Alert, Rule, Location)
│   ├── services/          # Business logic (Location, Geofence, SMS, Auth)
│   ├── blueprints/        # API routes (API, Auth, Dashboard, Realtime, Test)
│   └── utils/             # Helper functions (Auth decorator)
├── assets/                # Frontend resources
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript modules
├── templates/             # HTML templates
├── instance/              # SQLite database (created at runtime)
├── config.py              # Configuration settings
├── run.py                 # Application entry point
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker container definition
└── k8s/                   # Kubernetes manifests
```

## API Documentation

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Location Tracking
- `POST /api/location` - Receive location data from device
- `POST /api/heartbeat` - Device heartbeat check
- `GET /api/location/history` - Get location history

### Geofence Management
- `POST /api/geofence` - Create geofence zone
- `GET /api/geofence` - List all geofences
- `PUT /api/geofence/<id>` - Update geofence
- `DELETE /api/geofence/<id>` - Delete geofence

### Device Management
- `POST /api/device` - Register device
- `GET /api/device` - List devices
- `PUT /api/device/<id>` - Update device
- `DELETE /api/device/<id>` - Delete device

### Alerts
- `GET /api/alerts` - Get alert history
- `POST /api/alerts/clear` - Clear alerts

### Dashboard
- `GET /dashboard` - Parent dashboard (requires authentication)
- `GET /api/dashboard/stats` - Dashboard statistics

### System
- `GET /api/status` - API health check

## Development

### Running Tests
```bash
# Run application in development mode
python run.py
```

### Database Migrations
Database tables are created automatically on first run via SQLAlchemy's `db.create_all()`.

### Code Style
- Follow PEP 8
- Use descriptive variable names
- Document complex functions

## CI/CD

This project uses GitHub Actions for continuous integration and deployment:

- **Main branch** → Deploys to **Hetzner Kubernetes** (k3s)

The CI/CD workflow:
1. Runs tests and syntax checks
2. Builds Docker image on Hetzner server
3. Imports image to k3s
4. Applies Kubernetes manifests
5. Restarts deployment

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for password security
- **Rate Limiting**: API endpoint protection
- **Input Validation**: Sanitization of user inputs
- **Secure Credentials**: Environment variable management
- **HTTPS Support**: SSL/TLS encryption via Cloudflare

## Phase 2: AI Features (Planned)

- Behavioral pattern learning
- Smart alert filtering using ML
- Predictive geofencing
- Voice interaction capabilities
- Anomaly detection

## Troubleshooting

### Common Issues

**503 Service Temporarily Unavailable**
- Check if pods are running: `kubectl get pods -n gabay`
- Check pod logs: `kubectl logs -n gabay <pod-name>`
- Verify service and ingress: `kubectl get svc,ingress -n gabay`

**SMS Not Sending**
- Verify Twilio credentials in environment variables
- Check Twilio account balance
- Review SMS service logs

**Database Issues**
- Ensure instance directory has write permissions
- Check database file exists: `ls -la instance/`
- Verify SQLite is accessible

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary and confidential.

## Support

For issues and questions, please contact the development team.

---

**Live URL**: https://gabay.janisrael.com

**Project**: Gabay - Location Safety System  
**Version**: 1.0.0  
**Created By**: Jan Francis Israel  
**Website**: https://janisrael.com  
**GitHub**: https://github.com/janisrael/geo-fence
