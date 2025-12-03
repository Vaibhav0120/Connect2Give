/**
 * Volunteer Pickups & Delivery Management
 * Handles donation acceptance, delivery routing, and map display
 */

let deliveryMapInstance = null;

/**
 * Initialize the page when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function () {
    // Get the current view from the page (passed from Django template)
    const currentView = document.body.dataset.currentView || '';
    
    // If the page loads in delivery mode, initialize the map
    if (currentView === "delivery_route") {
        initializeDeliveryRouteMap();
    }

    // If the page loads with a specific view, ensure the correct tab is shown
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('view') === 'history') {
        const mainContent = document.getElementById('main-content');
        const historyContent = document.getElementById('history');
        
        if (mainContent) mainContent.classList.remove('active');
        if (historyContent) historyContent.classList.add('active');
    }
});

/**
 * Initialize the delivery route map with Leaflet and routing
 */
function initializeDeliveryRouteMap() {
    const volunteerDataElement = document.getElementById('volunteer-location-data');
    const campDataElement = document.getElementById('nearest-camp-data');
    const mapContainer = document.getElementById('delivery-map');

    // Validate required elements exist
    if (!volunteerDataElement || !mapContainer || !campDataElement) {
        if (mapContainer) {
            mapContainer.innerHTML = '<p class="empty-state">Cannot display route due to missing location data. Please set your location in your profile or check for active camps.</p>';
        }
        return;
    }

    // Validate Leaflet and routing libraries are loaded
    if (typeof L === 'undefined' || typeof L.Routing === 'undefined') {
        mapContainer.innerHTML = '<p class="empty-state">Error: Mapping library failed to load. Please refresh the page.</p>';
        return;
    }

    // Parse location data
    const volunteerData = JSON.parse(volunteerDataElement.textContent);
    const campData = JSON.parse(campDataElement.textContent);

    // Create map instance
    deliveryMapInstance = L.map('delivery-map', {
        zoomControl: false,
        attributionControl: false
    }).setView([volunteerData.lat, volunteerData.lon], 13);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(deliveryMapInstance);
    
    // Get CSRF token for form submission
    const csrftoken = getCookie('csrftoken');
    const deliveryFormAction = `/donation/deliver/to/${campData.pk}/`;

    // Add routing control
    L.Routing.control({
        waypoints: [
            L.latLng(volunteerData.lat, volunteerData.lon),
            L.latLng(campData.latitude, campData.longitude)
        ],
        routeWhileDragging: false,
        createMarker: (i, waypoint) => {
            const markerContent = i === 0 
                ? "<strong>Your Location</strong>" 
                : `<strong>Nearest Camp:</strong><br>${campData.name}`;
            
            return L.marker(waypoint.latLng, { draggable: false })
                .bindPopup(markerContent);
        }
    })
    .on('routesfound', function(e) {
        // Display route summary with distance and time
        const summary = e.routes[0].summary;
        const deliveryInfo = document.getElementById('delivery-info');
        const distance = (summary.totalDistance / 1000).toFixed(2);
        const time = Math.round(summary.totalTime / 60);
        
        deliveryInfo.innerHTML = `
            <div class="route-summary">
                <p><strong>Distance:</strong> ${distance} km</p>
                <p><strong>Estimated Time:</strong> ${time} minutes</p>
                <form action="${deliveryFormAction}" method="POST" style="margin-top: 1rem;">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                    <button type="submit" class="btn" data-testid="confirm-delivery-btn">
                        Confirm & Mark All as Delivered
                    </button>
                </form>
            </div>
        `;
    })
    .addTo(deliveryMapInstance);
}

/**
 * Switch between pickup and history tabs with URL update
 * @param {Event} event - Click event
 * @param {string} tabId - ID of tab to switch to
 */
function switchPickupTab(event, tabId) {
    const url = new URL(window.location);
    if (tabId === 'history') {
        url.searchParams.set('view', 'history');
    } else {
        url.searchParams.delete('view');
    }
    window.location.href = url.toString();
}

/**
 * Accept a donation via AJAX
 * @param {number} donationId - ID of the donation to accept
 */
function acceptDonation(donationId) {
    const csrftoken = getCookie('csrftoken');
    const acceptBtn = document.getElementById(`accept-btn-${donationId}`);
    
    if (!acceptBtn) {
        console.error('Accept button not found for donation:', donationId);
        return;
    }
    
    // Show loading state
    acceptBtn.disabled = true;
    acceptBtn.textContent = 'Accepting...';
    acceptBtn.style.cursor = 'wait';
    
    // Make AJAX request
    fetch(`/donation/accept/${donationId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update button to show success state
            acceptBtn.textContent = 'Accepted!';
            acceptBtn.classList.remove('action-button');
            acceptBtn.style.backgroundColor = '#10b981';
            acceptBtn.style.color = 'white';
            acceptBtn.style.cursor = 'default';
            
            // Animate and remove the row
            setTimeout(() => {
                const row = document.getElementById(`donation-row-${donationId}`);
                if (row) {
                    row.style.transition = 'opacity 0.3s ease-out';
                    row.style.opacity = '0';
                    setTimeout(() => row.remove(), 300);
                }
            }, 1000);
            
            // Show success message
            showToast(data.message || 'Donation accepted! Please pick it up within 30 minutes.', 'success');
            
            // Reload page after 2 seconds to update active pickups count
            setTimeout(() => location.reload(), 2000);
        } else {
            // Reset button on failure
            acceptBtn.disabled = false;
            acceptBtn.textContent = 'Accept';
            acceptBtn.style.cursor = 'pointer';
            showToast(data.message || 'Failed to accept donation', 'error');
        }
    })
    .catch(error => {
        console.error('Error accepting donation:', error);
        // Reset button on error
        acceptBtn.disabled = false;
        acceptBtn.textContent = 'Accept';
        acceptBtn.style.cursor = 'pointer';
        showToast('An error occurred. Please try again.', 'error');
    });
}

/**
 * Mark a donation as collected via AJAX
 * @param {number} donationId - ID of the donation to mark as collected
 */
function markAsCollected(donationId) {
    const csrftoken = getCookie('csrftoken');
    const collectBtn = document.getElementById(`collect-btn-${donationId}`);

    if (!collectBtn) return;

    // Show loading state
    collectBtn.disabled = true;
    collectBtn.textContent = 'Updating...';

    fetch(`/donation/collected/${donationId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            // Reload page to reflect changes (button should disappear or change to "Picked Up" badge)
            setTimeout(() => location.reload(), 1000);
        } else {
            collectBtn.disabled = false;
            collectBtn.textContent = 'Mark as Picked Up';
            showToast(data.message || 'Failed to update status', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        collectBtn.disabled = false;
        collectBtn.textContent = 'Mark as Picked Up';
        showToast('An error occurred. Please try again.', 'error');
    });
}

/**
 * Register with an NGO via AJAX
 * @param {number} ngoId - ID of the NGO to register with
 */
function registerWithNGO(ngoId) {
    const csrftoken = getCookie('csrftoken');
    const registerBtn = document.getElementById(`register-btn-${ngoId}`);
    
    if (!registerBtn) return;
    
    // Show loading state
    registerBtn.disabled = true;
    registerBtn.textContent = 'Registering...';
    
    fetch(`/volunteer/register/ngo/${ngoId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            registerBtn.disabled = false;
            registerBtn.textContent = 'Register';
            showToast(data.message || 'Failed to register', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        registerBtn.disabled = false;
        registerBtn.textContent = 'Register';
        showToast('An error occurred. Please try again.', 'error');
    });
}

/**
 * Unregister from an NGO via AJAX
 * @param {number} ngoId - ID of the NGO to unregister from
 */
function unregisterFromNGO(ngoId) {
    if (!confirm('Are you sure you want to unregister from this NGO?')) {
        return;
    }
    
    const csrftoken = getCookie('csrftoken');
    const unregisterBtn = document.getElementById(`unregister-btn-${ngoId}`);
    
    if (unregisterBtn) {
        unregisterBtn.disabled = true;
        unregisterBtn.textContent = 'Unregistering...';
    }
    
    fetch(`/volunteer/unregister/ngo/${ngoId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            if (unregisterBtn) {
                unregisterBtn.disabled = false;
                unregisterBtn.textContent = 'Unregister';
            }
            showToast(data.message || 'Failed to unregister', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (unregisterBtn) {
            unregisterBtn.disabled = false;
            unregisterBtn.textContent = 'Unregister';
        }
        showToast('An error occurred. Please try again.', 'error');
    });
}
