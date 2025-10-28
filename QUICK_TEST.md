# Quick Test - How to Trigger an Alert

## You Just Created a Geofence! ✅

Now let's test the alert system:

---

## Step 1: Get Your User ID

The user you're logged in as - check the login you used earlier.

---

## Step 2: Trigger a Test Alert

I created a test endpoint for you. Run this command:

```bash
curl -X POST http://localhost:5000/test/test-alert \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

**What it does:**
1. Gets your geofence center
2. Simulates a location 1km AWAY from center
3. Creates an alert
4. Sends SMS (if Twilio configured)

---

## Step 3: View the Alert

Go to:
```
http://localhost:5000/dashboard/alerts
```

You should see the alert!

---

## How the Real Child App Works

### On the Child's Phone:

1. **Child opens:** http://localhost:5000/dashboard/child
2. **Browser asks:** "Allow location tracking?" → Child clicks Allow
3. **App starts tracking:**
   - Every 5 minutes: Sends current location
   - Every 60 seconds: Sends heartbeat
4. **Server checks:**
   - Is location outside geofence? ✓
   - Is it during alert hours (midnight-6am)? ✗ (not now)
   - Has it been 10 minutes? ✓
   
5. **Alert triggers** (only if ALL conditions met)

---

## Current Alert Settings

By default, alerts only trigger:
- Between midnight and 6am (to test now, you need to modify the code or wait)

To make it work RIGHT NOW for testing:

Edit `app/services/location_service.py` line ~90:

```python
# Change from:
def should_trigger_alert(device_id, location):
    ...
    if not location.is_inside_geofence and rule.should_trigger_alert(current_time, current_date):

# To (for testing):
def should_trigger_alert(device_id, location):
    ...
    if not location.is_inside_geofence:  # Always alert if outside
```

This will trigger alerts immediately when outside geofence, regardless of time.

---

## Visual Flow

```
┌─────────────────────────────────────────────────┐
│  YOU (Parent)                                   │
│  Created geofence with map ✅                  │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  CHILD APP                                      │
│  • Sends location every 5 minutes             │
│  • "I'm at 37.7749, -122.4194"                │
│  • Server checks: Inside or outside?           │
└──────────────┬──────────────────────────────────┘
               │
       ┌───────┴──────────┐
       │                  │
   INSIDE              OUTSIDE
       │                  │
   ✅ SAFE         ❌ CHECK TIME & DURATION
       │                  │
                       └─▶ After 10 min + midnight-6am
                           │
                           ▼
                      🚨 ALERT!
                           │
                    ┌──────┴──────┐
                    │             │
              SMS to Parent   Alert in Dashboard
```

---

## Test It NOW:

1. **View your geofences:**
   - Go to http://localhost:5000/dashboard/geofence
   - You should see the geofence you created

2. **Trigger test alert:**
   ```bash
   curl -X POST http://localhost:5000/test/test-alert \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1}'
   ```

3. **Check alerts:**
   - Go to http://localhost:5000/dashboard/alerts
   - Alert should appear!

4. **Open child app** (optional):
   - New tab: http://localhost:5000/dashboard/child
   - Grant location permission
   - Watch it track your location

---

## Next Steps

Choose one:
1. **Test the alert now** (run the curl command above)
2. **Modify alert time** (make it work during daytime for testing)
3. **View the child app** (see how tracking works)
4. **Set up SMS** (configure Twilio)

What would you like to do next?



