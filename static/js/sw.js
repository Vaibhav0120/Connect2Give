// Service Worker for Push Notifications
self.addEventListener('push', function(event) {
    console.log('Push received:', event);
    
    let notificationData = {
        title: 'Connect2Give',
        body: 'You have a new notification',
        icon: '/static/images/logo.png',
        badge: '/static/images/logo.png',
        url: '/'
    };
    
    if (event.data) {
        try {
            const data = event.data.json();
            notificationData = {
                title: data.title || notificationData.title,
                body: data.body || notificationData.body,
                icon: data.icon || notificationData.icon,
                badge: data.badge || notificationData.badge,
                url: data.url || notificationData.url
            };
        } catch (e) {
            console.error('Error parsing notification data:', e);
        }
    }
    
    const promiseChain = self.registration.showNotification(notificationData.title, {
        body: notificationData.body,
        icon: notificationData.icon,
        badge: notificationData.badge,
        data: {
            url: notificationData.url
        }
    });
    
    event.waitUntil(promiseChain);
});

self.addEventListener('notificationclick', function(event) {
    console.log('Notification clicked:', event);
    event.notification.close();
    
    const url = event.notification.data.url || '/';
    
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(function(clientList) {
                // Check if there is already a window/tab open with the target URL
                for (let i = 0; i < clientList.length; i++) {
                    const client = clientList[i];
                    if (client.url === url && 'focus' in client) {
                        return client.focus();
                    }
                }
                // If no window/tab is already open, open a new one
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
    );
});

// Install event
self.addEventListener('install', function(event) {
    console.log('Service Worker installing.');
    self.skipWaiting();
});

// Activate event
self.addEventListener('activate', function(event) {
    console.log('Service Worker activating.');
    event.waitUntil(clients.claim());
});