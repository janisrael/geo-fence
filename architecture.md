# Geofence Tracking System — Architecture

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         SYSTEM OVERVIEW                          │
└─────────────────────────────────────────────────────────────────┘

    ┌────────────────┐
    │  Child Device  │
    │   (Browser/    │
    │   Capacitor)   │
    └───────┬────────┘
            │
            │ 1. Location Updates (every 5 min)
            │    POST /api/location
            │
            ▼
    ┌──────────────────────────────────────────────┐
    │         Flask Backend Server                 │
    │  ┌────────────────────────────────────────┐  │
    │  │  Location Service                      │  │
    │  │  - Receives location data              │  │
    │  │  - Validates coordinates               │  │
    │  │  - Stores in database                  │  │
    │  └──────────┬─────────────────────────────┘  │
    │             │                                 │
    │  ┌──────────▼─────────────────────────────┐  │
    │  │  Geofence Validator                     │  │
    │  │  - Checks if outside geofence          │  │
    │  │  - Validates time window                │  │
    │  │  - Calculates duration                  │  │
    │  └──────────┬─────────────────────────────┘  │
    │             │                                 │
    │  ┌──────────▼─────────────────────────────┐  │
    │  │  Alert Service                         │  │
    │  │  - Creates alert record                │  │
    │  │  - Sends SMS to parents                │  │
    │  │  - Updates dashboard                   │  │
    │  └──────────┬─────────────────────────────┘  │
    └─────────────┼─────────────────────────────────┘
                  │
                  │ 2. SMS Alert
                  │
                  ▼
        ┌─────────────────┐
        │  Twilio SMS API │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  Parent Phone   │
        │  (SMS Received) │
        └─────────────────┘

    ┌─────────────────────────────┐
    │   Parent Dashboard (Web)    │
    │  ┌────────────────────────┐ │
    │  │ - View alerts          │ │
    │  │ - Configure geofence   │ │
    │  │ - Set time windows     │ │
    │  │ - Live location map    │ │
    │  └────────────────────────┘ │
    └─────────────────────────────┘
```

---

## Component Architecture

### Backend Layer (Flask)

```
┌─────────────────────────────────────────────┐
│            Application Layer                │
│  ┌─────────────────────────────────────────┐│
│  │  Blueprints:                            ││
│  │  - /api/auth   (login, register)        ││
│  │  - /api/location (track, heartbeat)     ││
│  │  - /api/geofence (CRUD operations)     ││
│  │  - /api/alerts (list, acknowledge)     ││
│  └─────────────────────────────────────────┘│
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│            Service Layer                    │
│  ┌─────────────────────────────────────────┐│
│  │  LocationService                        ││
│  │  - Validate coordinates                 ││
│  │  - Store location data                  ││
│  └─────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────┐│
│  │  GeofenceService                        ││
│  │  - Calculate distance                   ││
│  │  - Check inside/outside                 ││
│  │  - Time window validation               ││
│  └─────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────┐│
│  │  SMSService (Twilio)                    ││
│  │  - Send alerts                          ││
│  │  - Rate limiting                        ││
│  │  - Message templates                    ││
│  └─────────────────────────────────────────┘│
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Database Layer (SQLAlchemy)        │
│  ┌─────────────────────────────────────────┐│
│  │  Models:                                ││
│  │  - User, Device, Geofence, Alert       ││
│  │  - Rules, Session                       ││
│  └─────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

### Frontend Layer (Web App)

```
┌─────────────────────────────────────────────┐
│         Child App Interface                 │
│  ┌─────────────────────────────────────────┐│
│  │  HTML: Minimal UI                        ││
│  │  - Background service worker            ││
│  │  - Silent location tracking             ││
│  │  - Heartbeat indicator (optional)       ││
│  └─────────────────────────────────────────┘│
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│       Parent Dashboard (Vue-like SPA)       │
│  ┌─────────────────────────────────────────┐│
│  │  Views:                                  ││
│  │  - Login / Register                     ││
│  │  - Dashboard (alerts overview)          ││
│  │  - Geofence Configuration               ││
│  │  - Settings (time windows, rules)      ││
│  │  - Live Map View                        ││
│  └─────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

---

## Data Flow: Alert Triggering

### Sequence Diagram

```
Child Device        Backend         Geofence         SMS Service
    │                 │                │                 │
    │─Send Location──>│                │                 │
    │                 │───Check───────>│                 │
    │                 │                │                 │
    │                 │<──Outside +    │                 │
    │                 │   TimeWindow   │                 │
    │                 │   Violation    │                 │
    │                 │                │                 │
    │                 │──Start Timer───>│                 │
    │                 │                │                 │
    │                 │  (10 min wait) │                 │
    │                 │                │                 │
    │─Still Outside──>│─Check Again───>│                 │
    │                 │                │                 │
    │                 │  (Timer Expired)                 │
    │                 │                │                 │
    │                 │───Create Alert─>│                │
    │                 │                │                 │
    │                 │───Send SMS─────>│──>Twilio────>Parent
    │                 │<───Confirm─────│                │
    │                 │                │                 │
    │<─Alert Sent─────│                │                 │
```

---

## Database Schema

```
┌──────────────────────────────────────────┐
│            DATABASE SCHEMA               │
└──────────────────────────────────────────┘

Users Table
├── id (PK)
├── name
├── role (child|parent)
├── phone
├── email
├── created_at
└── active

Devices Table
├── id (PK)
├── user_id (FK)
├── device_token
├── platform (web|android|ios)
├── last_location_id (FK)
├── last_seen
└── status (online|offline)

Locations Table
├── id (PK)
├── device_id (FK)
├── latitude
├── longitude
├── accuracy
├── timestamp
└── is_inside_geofence

Geofences Table
├── id (PK)
├── user_id (FK)
├── name
├── center_latitude
├── center_longitude
├── radius_meters
├── active
└── label

Alerts Table
├── id (PK)
├── device_id (FK)
├── geofence_id (FK)
├── alert_type (outside|tamper|heartbeat_lost)
├── latitude
├── longitude
├── timestamp
├── status (pending|sent|acknowledged)
└── message_sent

Rules Table
├── id (PK)
├── user_id (FK)
├── start_time (HH:MM)
├── end_time (HH:MM)
├── threshold_minutes
├── enabled
└── message_template
```

---

## Security Architecture

```
┌─────────────────────────────────────────────┐
│           Security Layers                    │
└─────────────────────────────────────────────┘

Layer 1: Transport Security
├── HTTPS/TLS for all communications
├── Certificate validation
└── Secure WebSocket for real-time updates

Layer 2: Authentication
├── JWT token-based auth
├── Device token validation
├── Session management
└── Refresh token rotation

Layer 3: Authorization
├── Role-based access (parent vs child)
├── Device ownership validation
├── API endpoint protection
└── Resource-level permissions

Layer 4: Data Protection
├── Encrypted location data
├── Secure SMS credentials
├── Input validation & sanitization
├── SQL injection prevention
└── XSS protection

Layer 5: Rate Limiting
├── API endpoint throttling
├── SMS sending limits
├── Location update frequency
└── DDoS protection
```

---

## Deployment Architecture

```
┌──────────────────────────────────────────────┐
│          PRODUCTION DEPLOYMENT               │
└──────────────────────────────────────────────┘

Internet
    │
    ▼
┌─────────────────────┐
│   Web Server (Nginx)│
│   - HTTPS/SSL       │
│   - Static files     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Flask App (Gunicorn) │
│   - Process Manager │
│   - Multi-worker    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   PostgreSQL DB      │
│   - Main database    │
│   - Replication      │
└─────────────────────┘

External Services:
├── Twilio (SMS)
├── Google Maps API (optional)
└── Capacitor Build Service
```

---

## Phase 2: AI Integration Points

```
┌─────────────────────────────────────────────┐
│            AI-Enhanced Features            │
└─────────────────────────────────────────────┘

1. Behavioral Pattern Learning
   └── Analyze historical location data
       └── Learn normal routes
       └── Detect anomalies

2. Smart Alert Filtering
   └── ML model for false positive reduction
   └── Context-aware alerting
   └── Adaptive thresholds

3. Predictive Geofencing
   └── Auto-adjust geofence based on patterns
   └── Predictive route monitoring
   └── Time-based pattern recognition

4. Natural Language Interface
   └── Voice commands for quick actions
   └── Chatbot for support
   └── Emergency voice activation
```

---

**Created**: $(date)  
**Architect**: Agimat  
**Project**: Geofence Tracking System



