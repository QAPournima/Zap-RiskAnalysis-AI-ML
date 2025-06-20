// 🔔 Push Notifications Manager for Bug Risk Dashboard
// Handles mobile push notifications for critical bug alerts

class PushNotificationManager {
    constructor() {
        this.isSupported = 'serviceWorker' in navigator && 'PushManager' in window;
        this.subscription = null;
        this.publicVapidKey = null; // Set this from your server
        this.debug = true;
        
        this.init();
    }

    async init() {
        if (!this.isSupported) {
            console.warn('🔔 Push notifications not supported in this browser');
            return;
        }

        console.log('🔔 Push Notification Manager initialized');
        
        // Check current permission status
        this.updatePermissionStatus();
        
        // Try to get existing subscription
        try {
            const registration = await navigator.serviceWorker.getRegistration();
            if (registration) {
                this.subscription = await registration.pushManager.getSubscription();
                if (this.subscription) {
                    console.log('🔔 Existing push subscription found');
                    this.debug && console.log('Subscription:', this.subscription);
                }
            }
        } catch (error) {
            console.error('🔔 Error checking existing subscription:', error);
        }
    }

    // Check if notifications are supported and enabled
    isEnabled() {
        return this.isSupported && Notification.permission === 'granted' && this.subscription;
    }

    // Get current permission status
    getPermissionStatus() {
        if (!this.isSupported) return 'unsupported';
        return Notification.permission;
    }

    // Update permission status in UI
    updatePermissionStatus() {
        const status = this.getPermissionStatus();
        const statusElement = document.getElementById('notificationStatus');
        
        if (statusElement) {
            let statusText, statusClass;
            
            switch (status) {
                case 'granted':
                    statusText = '🔔 Enabled';
                    statusClass = 'enabled';
                    break;
                case 'denied':
                    statusText = '🔕 Blocked';
                    statusClass = 'blocked';
                    break;
                case 'default':
                    statusText = '❓ Not Set';
                    statusClass = 'default';
                    break;
                case 'unsupported':
                    statusText = '❌ Not Supported';
                    statusClass = 'unsupported';
                    break;
            }
            
            statusElement.textContent = statusText;
            statusElement.className = `notification-status ${statusClass}`;
        }
    }

    // Request notification permission
    async requestPermission() {
        if (!this.isSupported) {
            throw new Error('Push notifications not supported');
        }

        if (Notification.permission === 'granted') {
            console.log('🔔 Notification permission already granted');
            return true;
        }

        console.log('🔔 Requesting notification permission...');
        
        const permission = await Notification.requestPermission();
        this.updatePermissionStatus();
        
        if (permission === 'granted') {
            console.log('✅ Notification permission granted');
            await this.subscribe();
            return true;
        } else {
            console.log('❌ Notification permission denied');
            return false;
        }
    }

    // Subscribe to push notifications
    async subscribe() {
        try {
            const registration = await navigator.serviceWorker.getRegistration();
            if (!registration) {
                throw new Error('Service worker not registered');
            }

            // For now, we'll use a placeholder VAPID key
            // In production, you'd get this from your server
            const vapidKey = 'BEl62iUYgUivxIkv69yViEuiBIa40HI8Ybn_gYk4P1UrNNtdfGrMUMJGCmV-n5LpGhH6-GWJ8-x0f6T8_KjP3Ds';
            
            this.subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(vapidKey)
            });

            console.log('🔔 Push subscription created:', this.subscription);
            
            // Send subscription to server
            await this.sendSubscriptionToServer(this.subscription);
            
            // Show success notification
            this.showLocalNotification(
                'Push Notifications Enabled! 🔔',
                'You\'ll now receive alerts for critical bug issues.',
                { tag: 'setup-success' }
            );
            
            return this.subscription;
            
        } catch (error) {
            console.error('🔔 Error subscribing to push notifications:', error);
            throw error;
        }
    }

    // Unsubscribe from push notifications
    async unsubscribe() {
        if (!this.subscription) {
            console.log('🔔 No active subscription to unsubscribe');
            return;
        }

        try {
            await this.subscription.unsubscribe();
            console.log('🔔 Successfully unsubscribed from push notifications');
            
            // Remove subscription from server
            await this.removeSubscriptionFromServer(this.subscription);
            
            this.subscription = null;
            this.updatePermissionStatus();
            
        } catch (error) {
            console.error('🔔 Error unsubscribing:', error);
            throw error;
        }
    }

    // Send subscription to server
    async sendSubscriptionToServer(subscription) {
        try {
            const response = await fetch('/api/push/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    subscription: subscription,
                    userAgent: navigator.userAgent,
                    timestamp: new Date().toISOString()
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            console.log('✅ Subscription sent to server');
            
        } catch (error) {
            console.error('❌ Failed to send subscription to server:', error);
            // Don't throw - local notifications can still work
        }
    }

    // Remove subscription from server
    async removeSubscriptionFromServer(subscription) {
        try {
            const response = await fetch('/api/push/unsubscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    subscription: subscription
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            console.log('✅ Subscription removed from server');
            
        } catch (error) {
            console.error('❌ Failed to remove subscription from server:', error);
        }
    }

    // Show local notification (for testing or immediate alerts)
    showLocalNotification(title, body, options = {}) {
        if (Notification.permission !== 'granted') {
            console.warn('🔔 Cannot show notification - permission not granted');
            return;
        }

        const defaultOptions = {
            icon: '/static/icons/icon-192x192.png',
            badge: '/static/icons/badge-72x72.png',
            tag: 'bug-alert',
            requireInteraction: false,
            timestamp: Date.now(),
            vibrate: [200, 100, 200],
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
            ]
        };

        const notificationOptions = { ...defaultOptions, ...options };
        
        try {
            const notification = new Notification(title, {
                body,
                icon: notificationOptions.icon,
                badge: notificationOptions.badge,
                tag: notificationOptions.tag,
                requireInteraction: notificationOptions.requireInteraction,
                timestamp: notificationOptions.timestamp,
                vibrate: notificationOptions.vibrate,
                data: {
                    url: '/',
                    timestamp: Date.now()
                }
            });

            // Handle notification click
            notification.onclick = function(event) {
                event.preventDefault();
                window.focus();
                notification.close();
            };

            console.log('🔔 Local notification displayed');
            
        } catch (error) {
            console.error('🔔 Error showing local notification:', error);
        }
    }

    // Test notifications with sample data
    async testNotification() {
        const testMessages = [
            {
                title: '🚨 Critical Bug Alert',
                body: 'Authentication component has 15+ critical issues requiring immediate attention',
                tag: 'critical-test'
            },
            {
                title: '⚠️ High Risk Components',
                body: 'iOS project: 3 components in high-risk state detected',
                tag: 'high-risk-test'
            },
            {
                title: '📊 Weekly Bug Summary',
                body: 'This week: 28 new bugs, 15 resolved. Android project needs attention.',
                tag: 'summary-test'
            }
        ];

        const randomMessage = testMessages[Math.floor(Math.random() * testMessages.length)];
        
        this.showLocalNotification(
            randomMessage.title,
            randomMessage.body,
            { 
                tag: randomMessage.tag,
                requireInteraction: true 
            }
        );
    }

    // Check for critical alerts and send notifications
    async checkAndNotifyAlerts() {
        try {
            const response = await fetch('/api/alerts/check');
            const alertData = await response.json();
            
            if (alertData.success && alertData.alerts && alertData.alerts.length > 0) {
                const criticalAlerts = alertData.alerts.filter(alert => 
                    alert.alert_level === 'critical' || alert.alert_level === 'urgent'
                );
                
                if (criticalAlerts.length > 0) {
                    const alert = criticalAlerts[0]; // Show first critical alert
                    
                    this.showLocalNotification(
                        `🚨 Critical: ${alert.component}`,
                        `${alert.bug_count} critical bugs detected in ${alert.project_name}`,
                        {
                            tag: `alert-${alert.component}`,
                            requireInteraction: true,
                            data: {
                                url: `/?project=${alert.project_name}&component=${alert.component}`,
                                alertLevel: alert.alert_level,
                                timestamp: Date.now()
                            }
                        }
                    );
                }
            }
            
        } catch (error) {
            console.error('🔔 Error checking alerts for notifications:', error);
        }
    }

    // Utility function to convert VAPID key
    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    // Schedule periodic alert checks
    startPeriodicAlertCheck(intervalMinutes = 5) {
        console.log(`🔔 Starting periodic alert checks every ${intervalMinutes} minutes`);
        
        // Initial check
        this.checkAndNotifyAlerts();
        
        // Set up interval
        this.alertCheckInterval = setInterval(() => {
            this.checkAndNotifyAlerts();
        }, intervalMinutes * 60 * 1000);
    }

    // Stop periodic alert checks
    stopPeriodicAlertCheck() {
        if (this.alertCheckInterval) {
            clearInterval(this.alertCheckInterval);
            this.alertCheckInterval = null;
            console.log('🔔 Stopped periodic alert checks');
        }
    }

    // Get subscription info for debugging
    getSubscriptionInfo() {
        if (!this.subscription) {
            return null;
        }

        return {
            endpoint: this.subscription.endpoint,
            keys: {
                p256dh: this.subscription.getKey('p256dh'),
                auth: this.subscription.getKey('auth')
            },
            supported: this.isSupported,
            permission: Notification.permission,
            enabled: this.isEnabled()
        };
    }
}

// Global instance
window.pushManager = new PushNotificationManager();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PushNotificationManager;
}

console.log('🔔 Push Notifications module loaded'); 