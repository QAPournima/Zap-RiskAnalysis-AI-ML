// 📱 Bug Risk Analysis Dashboard - Service Worker
// Provides offline support, caching, and push notifications

const CACHE_NAME = 'bugdash-v1.2.0';
const OFFLINE_URL = '/static/offline.html';

// Assets to cache for offline functionality
const CACHE_ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/offline.html',
    '/help',
    // Add any other critical assets
];

// API endpoints to cache responses
const API_CACHE_PATTERNS = [
    '/api/health',
    '/api/analyze/',
    '/api/trends/',
    '/api/alerts/check'
];

// 🚀 Install Event - Cache essential assets
self.addEventListener('install', event => {
    console.log('📦 Service Worker: Installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('📋 Service Worker: Caching essential assets');
                return cache.addAll(CACHE_ASSETS);
            })
            .then(() => {
                console.log('✅ Service Worker: Installation complete');
                return self.skipWaiting(); // Activate immediately
            })
            .catch(error => {
                console.error('❌ Service Worker: Installation failed', error);
            })
    );
});

// 🔄 Activate Event - Clean up old caches
self.addEventListener('activate', event => {
    console.log('🔄 Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== CACHE_NAME) {
                            console.log('🗑️ Service Worker: Deleting old cache', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('✅ Service Worker: Activation complete');
                return self.clients.claim(); // Take control immediately
            })
    );
});

// 🌐 Fetch Event - Handle requests with caching strategies
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip cross-origin requests
    if (!url.origin.includes(self.location.origin)) {
        return;
    }
    
    // Handle different types of requests
    if (request.method === 'GET') {
        if (url.pathname.startsWith('/api/')) {
            // API requests - Network first, then cache
            event.respondWith(handleApiRequest(request));
        } else if (url.pathname === '/' || url.pathname.startsWith('/help')) {
            // HTML pages - Stale while revalidate
            event.respondWith(handlePageRequest(request));
        } else if (url.pathname.startsWith('/static/')) {
            // Static assets - Cache first
            event.respondWith(handleStaticRequest(request));
        } else {
            // Other requests - Network first with offline fallback
            event.respondWith(handleGenericRequest(request));
        }
    }
});

// 🔌 API Request Handler - Network first with offline data
async function handleApiRequest(request) {
    const cache = await caches.open(CACHE_NAME);
    
    try {
        // Try network first
        const response = await fetch(request);
        
        if (response.ok) {
            // Cache successful API responses
            cache.put(request, response.clone());
            
            // Add offline indicator to response
            const modifiedResponse = addOfflineIndicator(response.clone(), false);
            return modifiedResponse;
        }
        
        throw new Error(`HTTP ${response.status}`);
        
    } catch (error) {
        console.log(`📡 Service Worker: Network failed for ${request.url}, trying cache`);
        
        // Try cache as fallback
        const cachedResponse = await cache.match(request);
        if (cachedResponse) {
            // Add offline indicator to cached response
            return addOfflineIndicator(cachedResponse, true);
        }
        
        // Return offline error response
        return createOfflineApiResponse(request);
    }
}

// 📄 Page Request Handler - Stale while revalidate
async function handlePageRequest(request) {
    const cache = await caches.open(CACHE_NAME);
    
    try {
        const response = await fetch(request);
        if (response.ok) {
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        const cachedResponse = await cache.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page
        return cache.match(OFFLINE_URL) || new Response(
            createOfflineHTML(),
            { headers: { 'Content-Type': 'text/html' } }
        );
    }
}

// 🖼️ Static Request Handler - Cache first
async function handleStaticRequest(request) {
    const cache = await caches.open(CACHE_NAME);
    
    // Try cache first
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }
    
    // Fetch and cache if not found
    try {
        const response = await fetch(request);
        if (response.ok) {
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        // Return a placeholder or error response
        return new Response('Asset not available offline', { status: 503 });
    }
}

// 🌍 Generic Request Handler - Network first with offline fallback
async function handleGenericRequest(request) {
    try {
        return await fetch(request);
    } catch (error) {
        const cache = await caches.open(CACHE_NAME);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            return cache.match(OFFLINE_URL) || new Response(
                createOfflineHTML(),
                { headers: { 'Content-Type': 'text/html' } }
            );
        }
        
        return new Response('Network error and no cache available', { status: 503 });
    }
}

// 🔄 Add offline indicator to API responses
function addOfflineIndicator(response, isOffline) {
    return response.json().then(data => {
        const modifiedData = {
            ...data,
            offline_mode: isOffline,
            cached_at: isOffline ? new Date().toISOString() : undefined
        };
        
        return new Response(JSON.stringify(modifiedData), {
            status: response.status,
            statusText: response.statusText,
            headers: response.headers
        });
    }).catch(() => response); // Return original if not JSON
}

// 📱 Create offline API response
function createOfflineApiResponse(request) {
    const url = new URL(request.url);
    const endpoint = url.pathname;
    
    let offlineData = {
        success: false,
        message: 'Offline mode - Liproprietary commercialed functionality available',
        offline_mode: true,
        endpoint: endpoint
    };
    
    // Provide basic offline responses for different endpoints
    if (endpoint.includes('/api/health')) {
        offlineData = {
            status: 'offline',
            jira_connected: false,
            offline_mode: true,
            message: 'Health check not available offline'
        };
    } else if (endpoint.includes('/api/analyze/')) {
        offlineData = {
            success: false,
            message: 'Analysis requires internet connection',
            offline_mode: true,
            suggestion: 'Connect to internet for real-time analysis'
        };
    } else if (endpoint.includes('/api/alerts/')) {
        offlineData = {
            success: true,
            alerts: [],
            alert_count: 0,
            offline_mode: true,
            message: 'Alert checking requires internet connection'
        };
    }
    
    return new Response(JSON.stringify(offlineData), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
    });
}

// 📄 Create offline HTML page
function createOfflineHTML() {
    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Offline - Bug Risk Dashboard</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin: 0;
                padding: 2rem;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
            .offline-container {
                max-width: 500px;
                padding: 2rem;
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            .offline-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
            }
            .retry-btn {
                background: #3498db;
                color: white;
                border: none;
                padding: 1rem 2rem;
                border-radius: 8px;
                font-size: 1rem;
                cursor: pointer;
                margin-top: 1rem;
            }
            .retry-btn:hover {
                background: #2980b9;
            }
        </style>
    </head>
    <body>
        <div class="offline-container">
            <div class="offline-icon">📱</div>
            <h1>You're Offline</h1>
            <p>Bug Risk Analysis Dashboard is currently offline. Some features may be liproprietary commercialed.</p>
            <p><strong>Available offline:</strong></p>
            <ul style="text-align: left; display: inline-block;">
                <li>View cached dashboard data</li>
                <li>Browse help documentation</li>
                <li>Access previously loaded charts</li>
            </ul>
            <p><strong>Requires internet:</strong></p>
            <ul style="text-align: left; display: inline-block;">
                <li>Real-time JIRA data analysis</li>
                <li>Live trend updates</li>
                <li>Push notifications</li>
            </ul>
            <button class="retry-btn" onclick="window.location.reload();">
                🔄 Try Again
            </button>
        </div>
    </body>
    </html>
    `;
}

// 🔔 Push Notification Handler
self.addEventListener('push', event => {
    console.log('🔔 Service Worker: Push notification received');
    
    let notificationData = {
        title: 'Bug Risk Alert',
        body: 'New critical issues detected',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        tag: 'bug-alert',
        requireInteraction: true,
        actions: [
            {
                action: 'view',
                title: 'View Dashboard',
                icon: '/static/icons/action-view.png'
            },
            {
                action: 'dismiss',
                title: 'Dismiss',
                icon: '/static/icons/action-dismiss.png'
            }
        ],
        data: {
            url: '/',
            timestamp: Date.now()
        }
    };
    
    // Parse push data if available
    if (event.data) {
        try {
            const pushData = event.data.json();
            notificationData = { ...notificationData, ...pushData };
        } catch (error) {
            console.error('❌ Service Worker: Failed to parse push data', error);
        }
    }
    
    event.waitUntil(
        self.registration.showNotification(notificationData.title, {
            body: notificationData.body,
            icon: notificationData.icon,
            badge: notificationData.badge,
            tag: notificationData.tag,
            requireInteraction: notificationData.requireInteraction,
            actions: notificationData.actions,
            data: notificationData.data,
            vibrate: [200, 100, 200], // Vibration pattern for mobile
            timestamp: notificationData.timestamp || Date.now()
        })
    );
});

// 👆 Notification Click Handler
self.addEventListener('notificationclick', event => {
    console.log('👆 Service Worker: Notification clicked');
    
    event.notification.close();
    
    const action = event.action;
    const data = event.notification.data || {};
    
    if (action === 'view' || !action) {
        // Open or focus the dashboard
        event.waitUntil(
            clients.matchAll({ type: 'window', includeUncontrolled: true })
                .then(clientList => {
                    // Try to find existing window
                    for (let client of clientList) {
                        if (client.url.includes(self.location.origin)) {
                            return client.focus();
                        }
                    }
                    
                    // Open new window if none found
                    return clients.openWindow(data.url || '/');
                })
        );
    } else if (action === 'dismiss') {
        console.log('🚫 Service Worker: Notification dismissed');
        // Just close the notification (already done above)
    }
});

// 🔄 Background Sync for offline actions
self.addEventListener('sync', event => {
    console.log('🔄 Service Worker: Background sync triggered');
    
    if (event.tag === 'background-sync') {
        event.waitUntil(handleBackgroundSync());
    }
});

// Handle background sync operations
async function handleBackgroundSync() {
    console.log('🔄 Service Worker: Performing background sync');
    
    try {
        // Try to sync any pending data
        // This could include cached filter preferences, user settings, etc.
        
        // Send message to main thread about sync completion
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
            client.postMessage({
                type: 'BACKGROUND_SYNC_COMPLETE',
                timestamp: Date.now()
            });
        });
        
        console.log('✅ Service Worker: Background sync completed');
    } catch (error) {
        console.error('❌ Service Worker: Background sync failed', error);
    }
}

// 📡 Handle messages from main thread
self.addEventListener('message', event => {
    const { type, data } = event.data || {};
    
    switch (type) {
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;
            
        case 'GET_VERSION':
            event.ports[0].postMessage({ version: CACHE_NAME });
            break;
            
        case 'CLEAR_CACHE':
            caches.delete(CACHE_NAME).then(() => {
                event.ports[0].postMessage({ success: true });
            });
            break;
            
        default:
            console.log('📨 Service Worker: Unknown message type', type);
    }
});

console.log('🚀 Service Worker: Loaded and ready!'); 