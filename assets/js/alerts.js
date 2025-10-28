// Alerts View JavaScript

const API_BASE = '/api';
let token = localStorage.getItem('token');

async function loadAlerts() {
    try {
        const response = await fetch(`${API_BASE}/alerts`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        
        if (data.status === 'ok') {
            displayAlerts(data.alerts);
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

function displayAlerts(alerts) {
    const container = document.getElementById('alertsContainer');
    
    if (alerts.length === 0) {
        container.innerHTML = '<div class="neu-container"><p style="text-align: center; padding: 40px;">No alerts yet</p></div>';
        return;
    }
    
    container.innerHTML = alerts.map(alert => {
        const alertClass = alert.alert_type === 'outside' ? 'alert-warning' : 'alert-danger';
        const status = alert.status.charAt(0).toUpperCase() + alert.status.slice(1);
        
        return `
            <div class="alert-card ${alertClass}">
                <h3>${alert.child_name || 'Child'}: ${alert.alert_type.charAt(0).toUpperCase() + alert.alert_type.slice(1).replace('_', ' ')} Alert</h3>
                <p><strong>Time:</strong> ${formatDate(alert.timestamp)}</p>
                <p><strong>Status:</strong> ${status}</p>
                <p><strong>Location:</strong> ${alert.latitude.toFixed(6)}, ${alert.longitude.toFixed(6)}</p>
                ${alert.message ? `<p style="margin: 10px 0; color: var(--danger-color);"><strong>Message:</strong> ${alert.message}</p>` : ''}
                <div style="margin-top: 15px; display: flex; gap: 10px;">
                    <a href="https://maps.google.com/?q=${alert.latitude},${alert.longitude}" target="_blank" 
                       class="neu-button neu-button-primary" style="flex: 1; text-align: center; text-decoration: none;">
                        View on Map
                    </a>
                    ${alert.status === 'sent' ? `
                        <button class="neu-button neu-button-success" onclick="acknowledgeAlert(${alert.id})" style="flex: 1;">
                            Acknowledge
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

async function acknowledgeAlert(alertId) {
    try {
        const response = await fetch(`${API_BASE}/alerts/${alertId}/acknowledge`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'ok') {
            alert('Alert acknowledged');
            loadAlerts();
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error acknowledging alert:', error);
        alert('Failed to acknowledge alert');
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
document.addEventListener('DOMContentLoaded', loadAlerts);

