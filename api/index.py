from flask import Flask
import json

app = Flask(__name__)

# Simple in-memory storage
locations = []

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ivnet Location Tracker</title>
        <link rel="manifest" href="/manifest.json">
        <meta name="theme-color" content="#764ba2">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <meta name="apple-mobile-web-app-title" content="ivnet Tracker">
    </head>
    <body style="font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; margin: 0;">
        <div style="background: rgba(255,255,255,0.1); padding: 40px; border-radius: 15px; max-width: 500px; margin: 0 auto;">
            <h1>🌍 ivnet Location Tracker</h1>
            <p>Professional location tracking system</p>
            <a href="/tracker" style="color: #ffd700; text-decoration: none; font-size: 18px; margin: 10px; display: inline-block; padding: 10px 20px; border: 2px solid #ffd700; border-radius: 8px;">📍 Start Tracking</a>
            <a href="/dashboard" style="color: #ffd700; text-decoration: none; font-size: 18px; margin: 10px; display: inline-block; padding: 10px 20px; border: 2px solid #ffd700; border-radius: 8px;">📊 View Dashboard</a>
        </div>
        
        <script>
            // Register Service Worker
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => console.log('SW registered'))
                    .catch(error => console.log('SW registration failed'));
            }
            
            // Auto-redirect mobile users to tracker for install prompt
            function isMobileDevice() {
                const userAgent = navigator.userAgent.toLowerCase();
                return /android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent);
            }
            
            if (isMobileDevice()) {
                setTimeout(() => {
                    if (window.location.pathname === '/') {
                        window.location.href = '/tracker';
                    }
                }, 2000);
            }
        </script>
    </body>
    </html>
    '''

@app.route('/manifest.json')
def manifest():
    return {
        "name": "ivnet Location Tracker",
        "short_name": "ivnet Tracker",
        "description": "Professional location tracking system",
        "start_url": "/tracker",
        "display": "standalone",
        "background_color": "#667eea",
        "theme_color": "#764ba2",
        "orientation": "portrait",
        "scope": "/",
        "categories": ["utilities", "productivity"],
        "icons": [
            {
                "src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='45' fill='%23667eea'/%3E%3Ctext x='50' y='65' font-size='50' text-anchor='middle' fill='white'%3E📍%3C/text%3E%3C/svg%3E",
                "sizes": "192x192",
                "type": "image/svg+xml",
                "purpose": "any maskable"
            },
            {
                "src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='45' fill='%23667eea'/%3E%3Ctext x='50' y='65' font-size='50' text-anchor='middle' fill='white'%3E📍%3C/text%3E%3C/svg%3E",
                "sizes": "512x512",
                "type": "image/svg+xml",
                "purpose": "any maskable"
            }
        ]
    }

@app.route('/sw.js')
def service_worker():
    return '''
    const CACHE_NAME = 'ivnet-tracker-v1';
    const urlsToCache = [
        '/tracker',
        '/dashboard',
        '/'
    ];

    self.addEventListener('install', event => {
        event.waitUntil(
            caches.open(CACHE_NAME)
                .then(cache => cache.addAll(urlsToCache))
        );
    });

    self.addEventListener('fetch', event => {
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    if (response) {
                        return response;
                    }
                    return fetch(event.request);
                }
            )
        );
    });
    ''', 200, {'Content-Type': 'application/javascript'}

@app.route('/tracker')
def tracker():
    return '''
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ivnet Location Tracker</title>
        <link rel="manifest" href="/manifest.json">
        <meta name="theme-color" content="#764ba2">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <meta name="apple-mobile-web-app-title" content="ivnet Tracker">
    </head>    <body style="font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: white;">
        <!-- PWA Install Prompt (Mobile Only) -->
        <div id="installPrompt" style="display: none; position: fixed; top: 0; left: 0; right: 0; background: linear-gradient(45deg, #28a745, #20c997); color: white; padding: 20px; text-align: center; z-index: 1000; box-shadow: 0 4px 20px rgba(0,0,0,0.4); border-bottom: 3px solid #fff;">
            <div style="display: flex; align-items: center; justify-content: space-between; max-width: 800px; margin: 0 auto; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 200px; margin-bottom: 10px;">
                    <div style="font-size: 20px; font-weight: bold; margin-bottom: 5px;">📱 Install ivnet Tracker</div>
                    <div style="font-size: 14px; opacity: 0.9;">Add to home screen for instant access!</div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button onclick="installApp()" style="background: rgba(255,255,255,0.9); border: none; color: #28a745; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);">📲 Install</button>
                    <button onclick="dismissInstall()" style="background: transparent; border: 2px solid white; color: white; padding: 10px 15px; border-radius: 8px; cursor: pointer; font-weight: bold;">✕</button>
                </div>
            </div>
        </div>

        <!-- Debug Console (only visible if needed) -->
        <div id="debugConsole" style="display: none; position: fixed; bottom: 10px; left: 10px; right: 10px; background: rgba(0,0,0,0.8); color: #00ff00; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px; max-height: 200px; overflow-y: auto; z-index: 999;">
            <div style="color: white; font-weight: bold; margin-bottom: 5px;">Debug Console: <button onclick="clearDebug()" style="float: right; background: #ff4444; color: white; border: none; padding: 2px 8px; border-radius: 3px; cursor: pointer; font-size: 10px;">Clear</button></div>
            <div id="debugContent"></div>
        </div>

        <div style="background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin-top: 20px;">
            <h1 style="text-align: center;">🌍 ivnet Location Tracker</h1>
            <p style="text-align: center; opacity: 0.9;">Track device location and info securely</p>
            
            <!-- Debug Button (for testing) -->
            <div style="text-align: center; margin: 10px 0;">
                <button onclick="toggleDebug()" style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 5px 10px; border-radius: 5px; cursor: pointer; font-size: 12px; opacity: 0.7;">🔍 Debug</button>
                <button onclick="forceShowInstall()" style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 5px 10px; border-radius: 5px; cursor: pointer; font-size: 12px; opacity: 0.7; margin-left: 5px;">📱 Test Install</button>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <button onclick="getLocation()" style="padding: 15px 25px; margin: 10px; border: none; border-radius: 10px; cursor: pointer; font-size: 16px; font-weight: bold; background: linear-gradient(45deg, #007bff, #0056b3); color: white;">📍 Get My Location</button>
                <button onclick="location.href='/dashboard'" style="padding: 15px 25px; margin: 10px; border: none; border-radius: 10px; cursor: pointer; font-size: 16px; font-weight: bold; background: linear-gradient(45deg, #6c757d, #545b62); color: white;">📊 View Dashboard</button>
            </div>
            
            <div id="status"></div>
            <div id="locationInfo"></div>
        </div>
        <script>
            // PWA Install Functionality
            let deferredPrompt;
            let installPromptShown = false;

            // Register Service Worker
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => console.log('SW registered:', registration))
                    .catch(error => console.log('SW registration failed:', error));
            }

            // Detect mobile devices (Android/iOS)
            function isMobileDevice() {
                const userAgent = navigator.userAgent.toLowerCase();
                const isMobile = /android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent);
                const isStandalone = window.matchMedia('(display-mode: standalone)').matches || 
                                   window.navigator.standalone === true ||
                                   document.referrer.includes('android-app://');
                console.log('Mobile check - isMobile:', isMobile, 'isStandalone:', isStandalone);
                return isMobile && !isStandalone;
            }

            // Listen for PWA install prompt
            window.addEventListener('beforeinstallprompt', (e) => {
                console.log('beforeinstallprompt fired');
                e.preventDefault();
                deferredPrompt = e;
                
                // Show install prompt only on mobile devices
                if (isMobileDevice() && !installPromptShown) {
                    setTimeout(() => showInstallPrompt(), 1000);
                }
            });

            // Show install prompt
            function showInstallPrompt() {
                console.log('Showing install prompt');
                if (isMobileDevice() || deferredPrompt) {
                    document.getElementById('installPrompt').style.display = 'block';
                    installPromptShown = true;
                }
            }

            // Install app
            async function installApp() {
                console.log('Install button clicked, deferredPrompt:', !!deferredPrompt);
                
                if (deferredPrompt) {
                    try {
                        // Show the install prompt
                        deferredPrompt.prompt();
                        
                        // Wait for the user to respond to the prompt
                        const choiceResult = await deferredPrompt.userChoice;
                        console.log('User choice:', choiceResult.outcome);
                        
                        if (choiceResult.outcome === 'accepted') {
                            console.log('User accepted the install prompt');
                            // Hide the custom install prompt
                            dismissInstall();
                        } else {
                            console.log('User dismissed the install prompt');
                        }
                        
                        // Clear the deferredPrompt variable
                        deferredPrompt = null;
                    } catch (error) {
                        console.error('Error during installation:', error);
                        // Show iOS instructions as fallback
                        showIOSInstructions();
                    }
                } else {
                    // Fallback for iOS Safari or browsers that don't support PWA install
                    showIOSInstructions();
                }
            }

            // Show iOS install instructions
            function showIOSInstructions() {
                if (/iphone|ipad|ipod/i.test(navigator.userAgent.toLowerCase())) {
                    alert('To install this app on iOS:\\n\\n1. Tap the Share button (⬆️) in Safari\\n2. Scroll down and select "Add to Home Screen"\\n3. Tap "Add" to install\\n\\nThe app will appear on your home screen!');
                } else if (/android/i.test(navigator.userAgent.toLowerCase())) {
                    alert('To install this app:\\n\\n1. Open Chrome browser settings (⋮)\\n2. Select "Add to Home Screen"\\n3. Tap "Add"\\n\\nOr try refreshing the page for the install prompt!');
                } else {
                    alert('This browser doesn\\'t support app installation.\\nTry using Chrome on Android or Safari on iOS!');
                }
                dismissInstall();
            }

            // Dismiss install prompt
            function dismissInstall() {
                document.getElementById('installPrompt').style.display = 'none';
                // Don't show again for this session
                sessionStorage.setItem('installPromptDismissed', 'true');
            }

            // Force show install prompt for testing
            function forceShowInstall() {
                sessionStorage.removeItem('installPromptDismissed');
                installPromptShown = false;
                showInstallPrompt();
            }

            // Check if prompt was already dismissed this session
            window.addEventListener('load', () => {
                console.log('Page loaded, checking install conditions...');
                
                if (sessionStorage.getItem('installPromptDismissed')) {
                    console.log('Install prompt was dismissed this session');
                    return;
                }
                
                // Show prompt after 2 seconds if mobile and not installed
                setTimeout(() => {
                    if (isMobileDevice() && !installPromptShown) {
                        console.log('No beforeinstallprompt yet, showing manual prompt');
                        showInstallPrompt();
                    }
                }, 2000);
            });            // Add double-tap to show install prompt (for testing)
            let tapCount = 0;
            document.addEventListener('click', () => {
                tapCount++;
                setTimeout(() => tapCount = 0, 500);
                if (tapCount === 3) {
                    debugLog('Triple tap detected - forcing install prompt');
                    forceShowInstall();
                }
            });

            // Debug functions
            function debugLog(message) {
                console.log(message);
                const debugContent = document.getElementById('debugContent');
                if (debugContent) {
                    const timestamp = new Date().toLocaleTimeString();
                    debugContent.innerHTML += `[${timestamp}] ${message}<br>`;
                    debugContent.scrollTop = debugContent.scrollHeight;
                }
            }

            function toggleDebug() {
                const debugConsole = document.getElementById('debugConsole');
                if (debugConsole.style.display === 'none') {
                    debugConsole.style.display = 'block';
                    debugLog('Debug console opened');
                    debugLog('User Agent: ' + navigator.userAgent);
                    debugLog('Is Mobile: ' + isMobileDevice());
                    debugLog('Has deferredPrompt: ' + !!deferredPrompt);
                    debugLog('Install prompt shown: ' + installPromptShown);
                    debugLog('Service Worker support: ' + ('serviceWorker' in navigator));
                } else {
                    debugConsole.style.display = 'none';
                }
            }

            function clearDebug() {
                document.getElementById('debugContent').innerHTML = '';
            }

            // Override console.log to show in debug console
            const originalLog = console.log;
            console.log = function(...args) {
                originalLog.apply(console, args);
                debugLog(args.join(' '));
            };

            // Location tracking function
            function getLocation() {
                document.getElementById('status').innerHTML = '<div style="padding: 15px; margin: 15px 0; border-radius: 10px; text-align: center; font-weight: bold; background-color: rgba(23, 162, 184, 0.8);">🔍 Getting location...</div>';
                
                if (!navigator.geolocation) {
                    document.getElementById('status').innerHTML = '<div style="padding: 15px; margin: 15px 0; border-radius: 10px; text-align: center; font-weight: bold; background-color: rgba(220, 53, 69, 0.8);">❌ Geolocation not supported</div>';
                    return;
                }
                
                navigator.geolocation.getCurrentPosition(
                    position => {
                        const data = {
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude,
                            accuracy: position.coords.accuracy,
                            timestamp: new Date().toISOString(),
                            userAgent: navigator.userAgent,
                            platform: navigator.platform
                        };
                        
                        document.getElementById('locationInfo').innerHTML = `
                            <div style="margin: 20px 0; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 10px;">
                                <h3>📍 Location Captured:</h3>
                                <p><strong>Latitude:</strong> ${data.latitude.toFixed(6)}</p>
                                <p><strong>Longitude:</strong> ${data.longitude.toFixed(6)}</p>
                                <p><strong>Accuracy:</strong> ${data.accuracy} meters</p>
                                <p><strong>Time:</strong> ${new Date().toLocaleString()}</p>
                                <p><strong>Device:</strong> ${data.platform}</p>
                                <p><strong>🗺️ Maps:</strong> <a href="https://www.google.com/maps?q=${data.latitude},${data.longitude}" target="_blank" style="color: #ffd700;">View on Google Maps</a></p>
                            </div>
                        `;
                        
                        fetch('/save', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(data)
                        })
                        .then(() => {
                            document.getElementById('status').innerHTML = '<div style="padding: 15px; margin: 15px 0; border-radius: 10px; text-align: center; font-weight: bold; background-color: rgba(40, 167, 69, 0.8);">✅ Location saved! Server ONLINE!</div>';
                        })
                        .catch(() => {
                            document.getElementById('status').innerHTML = '<div style="padding: 15px; margin: 15px 0; border-radius: 10px; text-align: center; font-weight: bold; background-color: rgba(220, 53, 69, 0.8);">⚠️ Server error</div>';
                        });
                    },
                    error => {
                        document.getElementById('status').innerHTML = '<div style="padding: 15px; margin: 15px 0; border-radius: 10px; text-align: center; font-weight: bold; background-color: rgba(220, 53, 69, 0.8);">❌ Location access denied</div>';
                    }
                );
            }
        </script>
    </body>
    </html>
    '''

@app.route('/dashboard')
def dashboard():
    return f'''
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ivnet Dashboard</title>
        <link rel="manifest" href="/manifest.json">
        <meta name="theme-color" content="#764ba2">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <meta name="apple-mobile-web-app-title" content="ivnet Tracker">
    </head>
    <body style="font-family: Arial; max-width: 1000px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: white;">
        <div style="background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px;">
            <h1 style="text-align: center;">📊 ivnet Dashboard</h1>
            
            <div style="text-align: center; margin: 30px 0;">
                <button onclick="location.href='/tracker'" style="padding: 12px 20px; margin: 5px; border: none; border-radius: 8px; cursor: pointer; background: linear-gradient(45deg, #007bff, #0056b3); color: white; font-weight: bold;">🔙 Back to Tracker</button>
                <button onclick="location.reload()" style="padding: 12px 20px; margin: 5px; border: none; border-radius: 8px; cursor: pointer; background: linear-gradient(45deg, #007bff, #0056b3); color: white; font-weight: bold;">🔄 Refresh</button>
            </div>
            
            <div style="text-align: center; padding: 20px;">
                <h2>📍 Total Locations: {len(locations)}</h2>
                <p>Server Status: <span style="color: #00ff00;">ONLINE</span></p>
            </div>
            
            <div>
                {'<p style="text-align: center; padding: 40px;">No locations tracked yet. Use the tracker!</p>' if len(locations) == 0 else ''.join([f'<div style="border: 1px solid rgba(255,255,255,0.2); margin: 15px 0; padding: 20px; border-radius: 10px; background: rgba(255,255,255,0.1);"><h3>📍 Location #{i+1}</h3><p>Coordinates: {loc.get("latitude", "Unknown")}, {loc.get("longitude", "Unknown")}</p><p>Time: {loc.get("timestamp", "Unknown")}</p><p>Device: {loc.get("platform", "Unknown")}</p></div>' for i, loc in enumerate(reversed(locations))])}
            </div>
        </div>        
        <script>
            // Register Service Worker
            if ('serviceWorker' in navigator) {{
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => console.log('SW registered'))
                    .catch(error => console.log('SW registration failed'));
            }}
        </script>
    </body>
    </html>
    '''

@app.route('/save', methods=['POST'])
def save():
    try:
        from flask import request
        data = request.get_json()
        locations.append(data)
        return {{"status": "success"}}
    except:
        return {{"status": "error"}}

@app.route('/test')
def test():
    return {{"status": "online", "locations": len(locations)}}

if __name__ == '__main__':
    app.run()
