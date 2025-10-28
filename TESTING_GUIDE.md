# Testing the Geofence Alert System

## Current Status ✅
- Geofence created successfully (you just did it!)
- Server running on http://localhost:5000
- Database working
- Map picker working

---

## How the Alert System Works

### Step-by-Step Flow:

```
1. PARENT SIDE (You just did this!)
   ├─ Create geofence with map picker ✅
   ├─ Set center location (click on map)
   ├─ Set radius (100m, 200m, etc.)
   └─ Save geofence

2. CHILD DEVICE SIDE (Need to test)
   ├─ Child opens app at /dashboard/child
   ├─ App requests location permission
   ├─ Every 5 minutes: Sends location to server
   ├─ Server checks: Is child inside geofence?
   └─ If NO + after curfew time → TRIGGER ALERT

3. ALERT SYSTEM
   ├─ Backend creates Alert record
   ├─ Sends SMS to parent (if Twilio configured)
   └─ Parent sees alert in dashboard
```

---

## Testing Flow (Right Now)

### Option 1: Test with Same Browser (Quick Test)

1. **Open Child App** in the SAME browser:
   ```
   http://localhost:5000/dashboard/child
   ```

2. **Grant Location Permission** when asked

3. **Watch the App** - It will:
   - Request your current location
   - Send location to server every 5 minutes
   - Show "Tracking Active" status

4. **Force an Alert** (for testing):
   - You're probably INSIDE the geofence right now
   - To test alert: Manually trigger it via API (see below)

### Option 2: Simulate Alert (Recommended for Quick Testing)

**Create a test alert manually via API:**

```bash
# First, get your JWT token from browser localStorage
# Or register a child account

# Then send a test location OUTSIDE the geofence:
curl -X POST http://localhost:5000/api/location \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 100.0000,
    "longitude": -200.0000,
    "accuracy": 10,
    "platform": "web",
    "device_token": "test-device"
  }'
```

---

## Detailed Alert Logic

### When Does Alert Trigger?

An alert triggers when ALL these conditions are met:

1. ✅ **Location**: Child is OUTSIDE any geofence
2. ⏰ **Time**: Current time is in alert window (midnight-6am by default)
3. ⏱️ **Duration**: Child has been outside for threshold minutes (10 minutes default)

### Example Scenario:

```
Geofence: Your Home (let's say at 37.7749, -122.4194)
Radius: 100 meters
Alert Rule: Between 00:00 - 06:00 (midnight to 6am)

Timeline:
─────────────────────────────────────────────────
10:00 PM - Child at home (inside geofence)
            ✅ No alert (before curfew)

11:59 PM - Child leaves home
            ⏳ Timer starts (10-minute threshold)

12:09 AM - Still outside after 10 minutes
            → 🚨 ALERT TRIGGERED!
            → SMS sent to parent
            → Dashboard shows alert

12:15 AM - Child returns home
            ✅ Alert resolved
```

---

## How to Test Child Tracking

### Method 1: Open Child App in Browser

1. **In a new tab/window, go to:**
   ```
   http://localhost:5000/dashboard/child
   ```

2. **Login as a child user:**
   - If you don't have one, register:
   - Go to http://localhost:5000
   - Register with role: "Child"
   - Login

3. **Grant location permission** when browser asks

4. **The app will:**
   - Show "Location Tracking Active"
   - Send location every 5 minutes
   - Update "Last update" timestamp

### Method 2: Test Alert Logic Manually

Create a test alert via the API:

```bash
# Using the curl command above
# Or use the test script below
```

---

## Testing Alert Trigger

### Quick Test: Mock Location Outside Geofence

I'll create a test endpoint for you. But first, let's check if you created the geofence correctly:

**Check your geofences:**
```bash
curl -s http://localhost:5000/dashboard/api/geofences \
  -H "Authorization: Bearer YOUR_TOKEN" | jq
```

**See your geofence center:** The latitude/longitude where you clicked

### To Test Alert:

1. **Get your current location**
   - Open browser console
   - Run: `navigator.geolocation.getCurrentPosition(console.log)`

2. **Check if you're inside geofence**
   - Your geofence center: (from geofence creation)
   - Your current location: (from step 1)
   - If distance > radius: You're OUTSIDE

3. **Wait during alert hours** (midnight-6am)
   - Or modify the rule to test now

---

## How Alert Rules Work

By default, the system will create automatic alerts when:
- Child leaves geofence
- After threshold time (10 minutes)
- During restricted hours

### Configure Alert Time Windows:

Currently hardcoded, but you can customize:

**Edit the logic in:** `app/services/location_service.py`

Find the `should_trigger_alert` function around line 59.

---

## Real-Time Testing Steps

### 1. Check Your Geofence Was Created

```bash
# In browser console or via API:
GET /dashboard/api/geofences
# Should show your created geofence
```

### 2. Open Child App

```
http://localhost:5000/dashboard/child
```

### 3. Monitor Dashboard

```
http://localhost:5000/dashboard/
```

Watch for:
- Device status changing
- Alerts appearing
- Location updates

### 4. Force Location Update

The child app sends location every 5 minutes. To test faster:
- Check browser console
- Look for location API calls
- Or manually trigger via API

---

## Expected Behavior

### Child App:
- Shows "Location Tracking Active"
- Updates every 5 minutes
- Minimal UI (background operation focus)
- Heartbeat every 60 seconds

### Parent Dashboard:
- Shows device count
- Shows recent alerts
- Shows geofence count
- Updates every 30 seconds

### When Alert Triggers:
1. Alert created in database
2. SMS sent (if Twilio configured)
3. Parent dashboard updates
4. Alert appears in /dashboard/alerts

---

## Configuration Needed

### For SMS to Work:
1. Sign up for Twilio at https://www.twilio.com
2. Get Account SID, Auth Token
3. Add to `.env` file:
   ```
   TWILIO_ACCOUNT_SID=your-sid
   TWILIO_AUTH_TOKEN=your-token
   TWILIO_FROM_NUMBER=+1234567890
   ```
4. Restart server

### For Alerts During Daytime:
Currently alerts only trigger midnight-6am. To test now:
- Modify the time check in `app/services/location_service.py`
- Or wait until midnight 😉

---

## Next Steps to Test NOW

1. ✅ Geofence created (you did this!)
2. ⏭️ Open child app: http://localhost:5000/dashboard/child
3. ⏭️ Grant location permission
4. ⏭️ Check dashboard for device registered
5. ⏭️ Wait 5 minutes OR manually trigger location update

---

**Would you like me to:**
- Create a test endpoint to manually trigger alerts?
- Set up Twilio for SMS testing?
- Modify alert time windows to work during daytime?
- Show you the actual code that checks geofence containment?



