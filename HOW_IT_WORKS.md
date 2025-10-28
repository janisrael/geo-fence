# How the Geofence Tracking System Works

## Overview
This system allows parents to monitor when their children leave designated safe zones (geofences) during restricted time periods and receive SMS alerts.

---

## System Flow

### 1. **Initial Setup (One-Time)**

```
┌─────────────┐
│   Parent    │
│  Registers  │
└──────┬──────┘
       │ Creates account
       ▼
┌─────────────────┐
│  Authentication │
│  (JWT Token)    │
└──────┬──────────┘
       │
       ▼
┌──────────────────┐
│  Create          │
│  Geofences       │ ← Define safe zones (home, school, etc.)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Create Rules    │ ← Set time windows (e.g., no alerts 6am-11pm)
└──────────────────┘
```

**Parent actions:**
1. Register at http://localhost:5000
2. Login to dashboard
3. Create geofences (pin location + radius)
4. Configure alert rules (time windows)

---

### 2. **Daily Operation**

#### A. **Child Device (Background Tracking)**

```
┌─────────────────────────────────────┐
│   Child Opens App (Background)     │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│  Browser Requests Location      │ ← HTML5 Geolocation API
│  (every 5 minutes)             │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│  POST /api/location             │
│  {                              │
│    latitude: 37.7749           │
│    longitude: -122.4194         │
│    accuracy: 10 meters          │
│  }                              │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│  Backend Processes Location     │
│  1. Save to database            │
│  2. Check geofence containment  │
│  3. Check time windows          │
│  4. Trigger alert if needed     │
└─────────────┬───────────────────┘
              │
              ▼
        ┌─────────────┐
        │   Alert?    │
        └──────┬──────┘
               │
        ┌──────┴─────────────┐
        │                    │
      YES                    NO
        │                    │
        ▼                    ▼
┌──────────────┐    ┌───────────────┐
│ Create Alert │    │   Continue    │
│ Send SMS     │    │   Tracking    │
└──────┬───────┘    └───────────────┘
       │
       ▼
┌─────────────────┐
│  Parent Receives│
│  SMS Alert      │
│  "Your child is │
│  outside safe   │
│  zone"          │
└─────────────────┘
```

---

### 3. **Real Example Scenario**

**Setup:**
- Geofence: Home (37.7749, -122.4194, radius 100m)
- Rule: Alert if outside between 12:00 AM - 6:00 AM
- Child device: Running background app

**Timeline:**
```
10:00 PM - Child inside geofence ✅
           No alert (before curfew)
           
11:59 PM - Child outside geofence ❌
           Timer starts (10-minute threshold)
           
12:09 AM - Still outside after 10 minutes
           → ALERT TRIGGERED
           → SMS sent to parent
           → Parent sees alert on dashboard
           
12:15 AM - Child returns inside geofence ✅
           Alert status: Resolved
```

---

## Key Components

### 1. **Frontend (Web UI)**

**Login Page** (`/`)
- User registration
- User login
- JWT token storage in localStorage

**Dashboard** (`/dashboard/`)
- Real-time stats (devices, alerts, geofences)
- Recent alerts view
- Quick navigation

**Geofence Configuration** (`/dashboard/geofence`)
- Create/edit/delete safe zones
- Set center coordinates
- Adjust radius (meters)

**Alerts Page** (`/dashboard/alerts`)
- View all alerts history
- Acknowledge alerts
- View on map

**Child App** (`/dashboard/child`)
- Minimal UI
- Background location tracking
- Silent operation

---

### 2. **Backend API**

#### Authentication
```python
POST /api/auth/register
  → Creates user account
  → Returns JWT token
  
POST /api/auth/login
  → Validates credentials
  → Returns JWT token
```

#### Location Tracking
```python
POST /api/location
  → Saves location to database
  → Checks geofence containment
  → Evaluates alert rules
  → Sends SMS if threshold exceeded
  
POST /api/heartbeat
  → Updates device online status
  → Marks device as "seen"
```

#### Geofence Management
```python
GET  /dashboard/api/geofences
POST /dashboard/api/geofences
PUT  /dashboard/api/geofences/<id>
DELETE /dashboard/api/geofences/<id>
```

---

### 3. **Geofence Detection Logic**

```python
# Pseudocode

def should_trigger_alert(location, time_now, rules):
    # 1. Check if outside any geofence
    if is_inside_geofence(location):
        return False  # Safe
    
    # 2. Check time window
    if not is_in_alert_window(time_now, rules):
        return False  # Outside alert hours
    
    # 3. Check duration outside
    duration_outside = get_duration_outside(device)
    if duration_outside < rule.threshold_minutes:
        return False  # Not outside long enough
    
    # 4. All conditions met - trigger alert
    return True
```

**Geofence Calculation:**
- Uses Geopy library
- Calculates distance from point to geofence center
- If distance ≤ radius: Inside ✅
- If distance > radius: Outside ❌

---

### 4. **Alert System**

#### Trigger Conditions
1. **Location**: Outside any configured geofence
2. **Time**: Within alert time window (e.g., midnight-6am)
3. **Duration**: Outside for threshold minutes (e.g., 10 minutes)

#### Alert Types
- `outside`: Left safe zone
- `tamper`: Device disabled/suspicious activity
- `heartbeat_lost`: No location updates for 30+ minutes
- `device_offline`: Device marked offline

#### SMS Integration (Twilio)
```python
def send_alert(alert):
    message = f"🚨 Alert: {child_name} is outside safe zone"
    map_url = f"https://maps.google.com/?q={lat},{lon}"
    
    send_sms(parent_phone, message + map_url)
```

---

## Database Schema

```
┌─────────┐       ┌─────────┐       ┌──────────┐
│  Users  │◄──────│ Devices │──────►│ Locations│
│         │       │         │       │          │
└────┬────┘       └────┬────┘       └──────────┘
     │                 │
     │                 │
     ▼                 ▼
┌──────────┐    ┌──────────┐
│ Geofences│    │  Alerts  │
│          │    │          │
└─────┬────┘    └──────────┘
      │
      │
      ▼
  ┌───────┐
  │ Rules │
  └───────┘
```

**Relationships:**
- User → Devices (1-to-many)
- Device → Locations (1-to-many)
- Device → Alerts (1-to-many)
- User → Geofences (1-to-many)
- Geofence → Locations (1-to-many)
- User → Rules (1-to-many)

---

## User Roles

### **Parent**
- Create/configure geofences
- View dashboard with stats
- Receive SMS alerts
- View alert history
- Monitor device status

### **Child**
- App runs in background
- Sends location updates every 5 minutes
- Sends heartbeat every minute
- No interaction required (stealth mode)

---

## Security Features

### Authentication
- JWT tokens (24-hour expiry)
- Bcrypt password hashing
- Protected API routes
- Session management

### Data Protection
- Encrypted location data in transit (HTTPS)
- User isolation (can only see own data)
- Device token validation
- Rate limiting (future)

### Privacy
- Location data retention: 30 days (configurable)
- Parent-child linkage for safety
- Consent-based tracking

---

## Installation & Usage

### Start Server
```bash
cd /home/swordfish/development/geofence
source venv/bin/activate
python run.py
```

### Access URLs
- **Login**: http://localhost:5000
- **Dashboard**: http://localhost:5000/dashboard/
- **Geofences**: http://localhost:5000/dashboard/geofence
- **Alerts**: http://localhost:5000/dashboard/alerts
- **Child App**: http://localhost:5000/dashboard/child

### First Time Setup
1. Register parent account
2. Login to dashboard
3. Create geofence (set home location)
4. Configure alert rules
5. Open child app on child's device
6. Enter credentials (same as parent)
7. Grant location permissions
8. System starts tracking

---

## Next Steps (Phase 2)

### Mobile App (Capacitor)
- Native Android/iOS app
- Background location tracking
- Push notifications
- Better battery optimization

### AI Features
- Pattern recognition (learn normal routes)
- Smart filtering (reduce false positives)
- Predictive alerts
- Voice interaction

---

## Technical Stack

**Backend:**
- Python 3.13
- Flask 3.0.0
- SQLAlchemy (ORM)
- Geopy (distance calculations)
- Twilio (SMS)
- PyJWT (authentication)

**Frontend:**
- HTML5
- CSS3 (Neumorphism design)
- Vanilla JavaScript
- Material Icons
- Roboto Slab font

**Database:**
- SQLite (development)
- PostgreSQL (production-ready)

---

**Created by**: Swordfish Development  
**Architect**: Agimat - Super Debugger AI v1.5  
**Status**: ✅ **Fully Operational**

