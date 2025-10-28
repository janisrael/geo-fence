// Dashboard JavaScript

const API_BASE = '/api';
let token = localStorage.getItem('token');

// Check authentication
if (!token) {
    window.location.href = '/api/auth/register';
}

// Map variables
let dashboardMap = null;
let deviceMarkers = [];
let geofenceCircles = [];
let mapInitialized = false;
let alertEventSource = null;

// Load user info
async function loadDashboard() {
    try {
        // Load user name
        const user = JSON.parse(localStorage.getItem('user'));
        if (user) {
            const userNameElement = document.getElementById('userName');
            if (userNameElement) {
                userNameElement.textContent = user.name;
            }
        }
        
        // Load stats
        await loadStats();
        
        // Load recent alerts
        await loadRecentAlerts();
        
        // Initialize map
        initDashboardMap();
        
        // Load map data
        await loadMapData();
        
        // Start periodic updates - every 10 seconds for real-time tracking
        setInterval(() => {
            loadStats();
            loadMapData();
        }, 10000); // Update every 10 seconds for near real-time tracking
        
        // Start real-time alert notifications
        initRealtimeAlerts();
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Initialize real-time alerts via Server-Sent Events
function initRealtimeAlerts() {
    try {
        const user = JSON.parse(localStorage.getItem('user'));
        if (!user) return;
        
        // Create SSE connection
        const eventSource = new EventSource(`/api/realtime/events?user_id=${user.id}`);
        alertEventSource = eventSource;
        
        eventSource.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                
                console.log('SSE message received:', data.type, data);
                
                if (data.type === 'new_alert') {
                    // New alert received - show notification and reload recent alerts
                    console.log('New alert received:', data);
                    
                    // Get parent name
                    const parentName = user.name || 'Gabe';
                    const childName = data.child_name || 'child-01';
                    
                    // Show in-page notification
                    console.log('Showing notification for child:', childName);
                    showNotification('Your child has left the designated safe area', `Alert: ${childName} is outside safe zone`, '⚠️');
                    
                    // Show browser notification if permission granted
                    if (Notification.permission === 'granted') {
                        new Notification('Alert Triggered', {
                            body: `Hey ${parentName}, your child ${childName} is on the loose`,
                            icon: '/static/icon-192x192.png',
                            tag: 'geofence-alert'
                        });
                    }
                    
                    // Reload recent alerts immediately
                    loadRecentAlerts();
                    // Also reload stats to update alert count
                    loadStats();
                } else if (data.type === 'connected') {
                    console.log('Real-time alert stream connected');
                } else if (data.type === 'heartbeat') {
                    // Keep connection alive - only log occasionally to avoid spam
                    // console.log('SSE heartbeat');
                }
            } catch (error) {
                console.error('Error processing SSE message:', error);
            }
        };
        
        eventSource.onerror = function(error) {
            console.error('SSE error:', error);
            // Try to reconnect after 5 seconds
            setTimeout(() => {
                if (alertEventSource) {
                    alertEventSource.close();
                }
                initRealtimeAlerts();
            }, 5000);
        };
        
        // Request notification permission on first load
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }
    } catch (error) {
        console.error('Error initializing real-time alerts:', error);
    }
}

async function loadStats() {
    try {
        // Get devices
        const devicesRes = await fetch(`${API_BASE}/devices`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const devicesData = await devicesRes.json();
        
        if (devicesData.status === 'ok') {
            const devices = devicesData.devices;
            document.getElementById('deviceCount').textContent = devices.length;
            
            const onlineDevices = devices.filter(d => d.status === 'online').length;
            const statusIndicator = document.getElementById('deviceStatus');
            const statusText = document.getElementById('deviceStatusText');
            
            if (onlineDevices > 0) {
                statusIndicator.className = 'status-indicator online';
                statusText.textContent = `${onlineDevices} online`;
            } else {
                statusIndicator.className = 'status-indicator offline';
                statusText.textContent = 'All offline';
            }
        }
        
        // Get alerts
        const alertsRes = await fetch(`${API_BASE}/alerts`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const alertsData = await alertsRes.json();
        
        if (alertsData.status === 'ok') {
            const alerts = alertsData.alerts.filter(a => 
                new Date(a.timestamp) > new Date(Date.now() - 24*60*60*1000)
            );
            document.getElementById('alertCount').textContent = alerts.length;
        }
        
        // Get geofences
        const geofencesRes = await fetch(`/dashboard/api/geofences`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const geofencesData = await geofencesRes.json();
        
        if (geofencesData.status === 'ok') {
            document.getElementById('geofenceCount').textContent = geofencesData.geofences.length;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadRecentAlerts() {
    try {
        const response = await fetch(`${API_BASE}/alerts`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        
        if (data.status === 'ok') {
            const alerts = data.alerts.slice(0, 5); // Show recent 5
            const container = document.getElementById('recentAlerts');
            
            if (alerts.length === 0) {
                container.innerHTML = '<p style="text-align: center; padding: 40px;">No recent alerts</p>';
                return;
            }
            
            container.innerHTML = alerts.map(alert => `
                <div class="alert-card alert-warning" style="display: flex; justify-content: space-between; align-items: center; gap: 15px; padding: 15px;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; font-size: 1em;">${alert.child_name || 'Child'}</h4>
                        <p style="margin: 5px 0; font-size: 0.85em; color: var(--primary-color);">${formatDate(alert.timestamp)}</p>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <a href="https://maps.google.com/?q=${alert.latitude},${alert.longitude}" target="_blank" 
                           class="neu-button" style="padding: 8px 15px; font-size: 0.85em; min-width: 80px;">
                            Location
                        </a>
                        <button onclick="sendMessageToChild('${alert.child_name || 'Child'}')" 
                                class="neu-button neu-button-primary" 
                                style="padding: 8px 15px; font-size: 0.85em; min-width: 80px;">
                            Message
                        </button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading recent alerts:', error);
        document.getElementById('recentAlerts').innerHTML = 
            '<p style="text-align: center; padding: 40px; color: var(--danger-color);">Error loading alerts</p>';
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

// Initialize dashboard map
function initDashboardMap() {
    if (!dashboardMap) {
        // Default to a general location (you can make this dynamic)
        dashboardMap = L.map('dashboardMap').setView([34.0522, -118.2437], 12);
        
        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(dashboardMap);
    }
}

// Load map data (devices and geofences)
async function loadMapData() {
    try {
        // Clear existing geofence circles
        geofenceCircles.forEach(circle => dashboardMap.removeLayer(circle));
        geofenceCircles = [];
        
        // Get devices
        const devicesRes = await fetch(`${API_BASE}/devices`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const devicesData = await devicesRes.json();
        
        // Create a map of existing markers by device ID (before clearing)
        const existingMarkers = {};
        const oldMarkers = [...deviceMarkers]; // Copy before clearing
        oldMarkers.forEach((marker) => {
            if (marker.deviceId) {
                existingMarkers[marker.deviceId] = marker;
            }
        });
        
        // Get valid device IDs with locations
        const validDeviceIds = new Set();
        if (devicesData.status === 'ok' && devicesData.devices.length > 0) {
            devicesData.devices.forEach(device => {
                if (device.last_location) {
                    validDeviceIds.add(device.id);
                }
            });
        }
        
        // Remove markers for devices that no longer have valid locations
        oldMarkers.filter(m => m.deviceId && !validDeviceIds.has(m.deviceId))
            .forEach(m => dashboardMap.removeLayer(m));
        
        // Clear markers array - will rebuild with updates
        deviceMarkers = [];
        
        if (devicesData.status === 'ok' && devicesData.devices.length > 0) {
            devicesData.devices.forEach(device => {
                // Get last location for each device
                if (device.last_location) {
                    const lat = device.last_location.latitude;
                    const lng = device.last_location.longitude;
                    // Format child name - default to 'child-01' if not set
                    let childName = device.child_name || 'child-01';
                    if (childName.toLowerCase() === 'test' || childName.toLowerCase() === 'web-browser' || childName.toLowerCase() === 'web') {
                        childName = 'child-01';
                    }
                    
                    // Check if marker already exists for this device
                    let marker = existingMarkers[device.id];
                    
                    if (marker) {
                        // Update existing marker position smoothly with animation
                        marker.setLatLng([lat, lng], {
                            animate: true,
                            duration: 1.0
                        });
                    } else {
                        // Add new marker
                        marker = L.marker([lat, lng], {
                            icon: L.divIcon({
                                className: 'device-marker',
                                html: `<div style="background: ${device.status === 'online' ? '#00b894' : '#d63031'}; color: white; padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); display: flex; align-items: center; gap: 6px; white-space: nowrap;">
                                    <span style="font-size: 16px;">👤</span>
                                    <span>${childName}</span>
                                </div>`,
                                iconSize: [null, 35],
                                iconAnchor: [55, 25]
                            })
                        }).addTo(dashboardMap);
                        
                        marker.bindPopup(`<b>👤 ${childName}</b><br>Status: ${device.status}<br>Platform: ${device.platform}`);
                        marker.deviceId = device.id; // Store device ID
                    }
                    
                    deviceMarkers.push(marker);
                }
            });
            
            // Only auto-focus map on first load
            if (!mapInitialized && deviceMarkers.length > 0) {
                const bounds = L.latLngBounds(deviceMarkers.map(m => m.getLatLng()));
                if (deviceMarkers.length === 1) {
                    // Single device - center on it
                    dashboardMap.setView(deviceMarkers[0].getLatLng(), 15);
                } else {
                    // Multiple devices - fit all in view
                    dashboardMap.fitBounds(bounds, { padding: [50, 50] });
                }
                mapInitialized = true;
            }
        }
        
        // Get geofences
        const geofencesRes = await fetch(`/dashboard/api/geofences`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const geofencesData = await geofencesRes.json();
        
        if (geofencesData.status === 'ok') {
            geofencesData.geofences.forEach(geofence => {
                // Draw geofence circle
                const circle = L.circle([geofence.center_latitude, geofence.center_longitude], {
                    radius: geofence.radius_meters,
                    color: '#d63031',
                    fillColor: '#ffffff',
                    fillOpacity: 0.2,
                    weight: 2
                }).addTo(dashboardMap);
                
                // Add label
                L.marker([geofence.center_latitude, geofence.center_longitude], {
                    icon: L.divIcon({
                        className: 'geofence-label',
                        html: `<div style="background: rgba(255,255,255,0.9); padding: 5px 10px; border-radius: 5px; font-weight: 600; color: #d63031; border: 2px solid #d63031;">${geofence.name}</div>`,
                        iconSize: [null, 30],
                        iconAnchor: [0, 15]
                    })
                }).addTo(dashboardMap);
                
                geofenceCircles.push(circle);
            });
        }
    } catch (error) {
        console.error('Error loading map data:', error);
    }
}

// Toggle mobile navigation menu
function toggleNavMenu() {
    const navMenu = document.getElementById('navMenu');
    const burgerMenu = document.querySelector('.burger-menu');
    
    if (navMenu && burgerMenu) {
        navMenu.classList.toggle('active');
        burgerMenu.classList.toggle('active');
    }
}

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    const nav = document.querySelector('.nav-container');
    const burger = document.querySelector('.burger-menu');
    const navMenu = document.getElementById('navMenu');
    
    if (nav && navMenu && !nav.contains(event.target) && navMenu.classList.contains('active')) {
        navMenu.classList.remove('active');
        if (burger) burger.classList.remove('active');
    }
});

// Show in-page notification
function showNotification(message, title = null, icon = '⚠️') {
    const container = document.getElementById('notificationContainer');
    if (!container) return;
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.innerHTML = `
        <div class="notification-icon">${icon}</div>
        <div class="notification-content">
            ${title ? `<div class="notification-title">${title}</div>` : ''}
            <div class="notification-message">${message}</div>
        </div>
    `;
    
    // Add click handler to remove notification
    notification.addEventListener('click', () => {
        notification.style.animation = 'slideOut 0.5s ease-in';
        setTimeout(() => notification.remove(), 500);
    });
    
    // Add to container
    container.appendChild(notification);
    
    // Auto-remove after 8 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.5s ease-in';
            setTimeout(() => notification.remove(), 500);
        }
    }, 8000);
}

// Add slideOut animation to CSS via JavaScript
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Send message to child function
function sendMessageToChild(childName) {
    const messages = [
        `Hey ${childName}, please come back to the safe zone.`,
        `${childName}, where are you? Come back home please.`,
        `Hi ${childName}, stay safe and return to the designated area.`,
        `${childName}, mom/dad is worried. Please come back now.`
    ];
    
    const randomMessage = messages[Math.floor(Math.random() * messages.length)];
    
    // Show notification with message icon
    showNotification(`Message sent to ${childName}: "${randomMessage}"`, 'Message Sent', '✉️');
    
    console.log(`Message to ${childName}: ${randomMessage}`);
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', loadDashboard);

