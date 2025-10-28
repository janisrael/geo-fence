// Geofence Management JavaScript

const API_BASE = '/api';
let token = localStorage.getItem('token');
let map = null;
let geofenceMarker = null;
let geofenceCircle = null;
let currentCenter = null;
let currentRadius = 100; // meters

async function loadGeofences() {
    try {
        const response = await fetch(`/dashboard/api/geofences`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        
        if (data.status === 'ok') {
            displayGeofences(data.geofences);
        }
    } catch (error) {
        console.error('Error loading geofences:', error);
    }
}

function displayGeofences(geofences) {
    const container = document.getElementById('geofencesList');
    
    if (geofences.length === 0) {
        container.innerHTML = '<div class="neu-container"><p style="text-align: center; padding: 40px;">No geofences configured. Create one to get started.</p></div>';
        return;
    }
    
    container.innerHTML = geofences.map(gf => `
        <div class="neu-card">
            <h3>${gf.name}</h3>
            <p><strong>Type:</strong> ${gf.label || 'Custom'}</p>
            <p><strong>Radius:</strong> ${gf.radius_meters} meters</p>
            <p><strong>Status:</strong> ${gf.active ? '<span style="color: var(--success-color);">Active</span>' : 'Inactive'}</p>
            <button class="neu-button neu-button-danger" onclick="deleteGeofence(${gf.id})" style="margin-top: 15px;">
                Delete
            </button>
        </div>
    `).join('');
}

async function createGeofence(event) {
    event.preventDefault();
    
    // Get values from map
    const lat = parseFloat(document.getElementById('gfLatitude').value);
    const lng = parseFloat(document.getElementById('gfLongitude').value);
    
    if (!lat || !lng || isNaN(lat) || isNaN(lng)) {
        alert('Please click on the map to set a location');
        return;
    }
    
    const formData = {
        name: document.getElementById('gfName').value,
        center_latitude: lat,
        center_longitude: lng,
        radius_meters: parseInt(document.getElementById('gfRadius').value),
        label: document.getElementById('gfLabel').value
    };
    
    try {
        const response = await fetch(`/dashboard/api/geofences`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.status === 'ok') {
            alert('Geofence created successfully!');
            
            // Close modal and reset
            document.getElementById('addGeofenceModal').classList.remove('active');
            if (map) {
                map.remove();
                map = null;
                geofenceMarker = null;
                geofenceCircle = null;
                currentCenter = null;
            }
            document.getElementById('geofenceForm').reset();
            document.getElementById('radiusDisplay').textContent = '100';
            currentRadius = 100;
            
            loadGeofences();
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error creating geofence:', error);
        alert('Failed to create geofence');
    }
}

async function deleteGeofence(id) {
    if (!confirm('Are you sure you want to delete this geofence?')) {
        return;
    }
    
    try {
        const response = await fetch(`/dashboard/api/geofences/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await response.json();
        
        if (data.status === 'ok') {
            alert('Geofence deleted');
            loadGeofences();
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error deleting geofence:', error);
        alert('Failed to delete geofence');
    }
}

function showAddGeofence() {
    document.getElementById('addGeofenceModal').classList.add('active');
    
    // Initialize map after modal is shown
    setTimeout(() => {
        initMapPicker();
    }, 100);
}

function initMapPicker() {
    // Default center (San Francisco) - will try to use user's location
    const defaultCenter = [37.7749, -122.4194];
    
    // Create map
    if (!map) {
        map = L.map('geofenceMap').setView(defaultCenter, 13);
        
        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        // Try to get user's current location
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    map.setView([lat, lng], 14);
                    updateCoordinates(lat, lng);
                },
                (error) => {
                    console.log('Could not get location:', error);
                }
            );
        }
        
        // Map click handler
        map.on('click', (e) => {
            const { lat, lng } = e.latlng;
            updateCoordinates(lat, lng);
        });
    }
    
    // Update coordinates on first load
    if (!currentCenter) {
        const center = map.getCenter();
        updateCoordinates(center.lat, center.lng);
    }
}

function updateCoordinates(lat, lng) {
    currentCenter = [lat, lng];
    
    // Update input fields
    document.getElementById('gfLatitude').value = lat.toFixed(6);
    document.getElementById('gfLongitude').value = lng.toFixed(6);
    
    // Update marker
    if (geofenceMarker) {
        map.removeLayer(geofenceMarker);
    }
    geofenceMarker = L.marker([lat, lng]).addTo(map);
    geofenceMarker.bindPopup('<b>Geofence Center</b><br>Click to set different location').openPopup();
    
    // Update circle
    updateCircle();
}

function updateCircle() {
    // Remove existing circle
    if (geofenceCircle) {
        map.removeLayer(geofenceCircle);
    }
    
    if (currentCenter && currentRadius) {
        // Create circle
        geofenceCircle = L.circle(currentCenter, {
            color: '#007bff',
            fillColor: '#007bff',
            fillOpacity: 0.2,
            radius: currentRadius
        }).addTo(map);
    }
}

function updateRadiusDisplay(value) {
    currentRadius = parseInt(value);
    document.getElementById('radiusDisplay').textContent = currentRadius;
    updateCircle();
}

function closeAddGeofence() {
    document.getElementById('addGeofenceModal').classList.remove('active');
    
    // Clean up map
    if (map) {
        map.remove();
        map = null;
        geofenceMarker = null;
        geofenceCircle = null;
        currentCenter = null;
    }
    
    // Reset form
    document.getElementById('geofenceForm').reset();
    document.getElementById('radiusDisplay').textContent = '100';
    currentRadius = 100;
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', loadGeofences);
document.getElementById('geofenceForm').addEventListener('submit', createGeofence);

