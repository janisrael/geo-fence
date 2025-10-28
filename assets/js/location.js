// Location Tracking for Child App

const API_BASE = '/api';
let token = localStorage.getItem('token');
let watchId = null;

// Check authentication
if (!token) {
    window.location.href = '/';
}

function startTracking() {
    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser');
        return;
    }
    
    const options = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
    };
    
    // Start tracking
    watchId = navigator.geolocation.watchPosition(
        handlePositionSuccess,
        handlePositionError,
        options
    );
    
    // Also send heartbeat
    setInterval(sendHeartbeat, 60000); // Every minute
}

function handlePositionSuccess(position) {
    const { latitude, longitude, accuracy } = position.coords;
    
    updateStatus('Active', 'online');
    updateLastUpdate();
    
    // Send location to server
    sendLocation(latitude, longitude, accuracy);
}

function handlePositionError(error) {
    updateStatus('Error: ' + error.message, 'offline');
    console.error('Geolocation error:', error);
}

async function sendLocation(latitude, longitude, accuracy) {
    try {
        const response = await fetch(`${API_BASE}/location`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                latitude,
                longitude,
                accuracy,
                platform: 'web',
                device_token: 'web-browser'
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'ok' && data.alert_triggered) {
            console.log('Alert triggered!');
        }
    } catch (error) {
        console.error('Error sending location:', error);
    }
}

async function sendHeartbeat() {
    try {
        const response = await fetch(`${API_BASE}/heartbeat`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                device_token: 'web-browser'
            })
        });
        
        if (response.ok) {
            console.log('Heartbeat sent');
        }
    } catch (error) {
        console.error('Error sending heartbeat:', error);
    }
}

function updateStatus(status, indicatorClass) {
    const statusElement = document.getElementById('status');
    const indicatorElement = document.querySelector('.status-indicator-large');
    
    if (statusElement) {
        statusElement.textContent = status;
    }
    
    if (indicatorElement) {
        indicatorElement.className = `status-indicator-large ${indicatorClass}`;
    }
}

function updateLastUpdate() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    
    const lastUpdateElement = document.getElementById('lastUpdate');
    if (lastUpdateElement) {
        lastUpdateElement.textContent = timeString;
    }
}

// Initialize tracking when page loads
document.addEventListener('DOMContentLoaded', () => {
    updateStatus('Starting...', 'online');
    startTracking();
    updateLastUpdate();
});

// Keep page alive
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        updateLastUpdate();
    }
});



