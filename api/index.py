from flask import Flask, request, jsonify, render_template_string, send_from_directory
import json
from datetime import datetime
import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Store location data in memory (for demo purposes)
location_data = []

# HTML template for the tracker with proper PWA support
tracker_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ivnet Location Tracker</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#007bff">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="ivnet Tracker">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        .status { 
            padding: 15px; 
            margin: 15px 0; 
            border-radius: 10px; 
            text-align: center;
            font-weight: bold;
        }
        .success { background-color: rgba(40, 167, 69, 0.8); }
        .error { background-color: rgba(220, 53, 69, 0.8); }
        .info { background-color: rgba(23, 162, 184, 0.8); }
        button { 
            padding: 15px 25px; 
            margin: 10px; 
            border: none; 
            border-radius: 10px; 
            cursor: pointer; 
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            min-width: 200px;
        }
        .primary { 
            background: linear-gradient(45deg, #007bff, #0056b3); 
            color: white; 
        }
        .primary:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,123,255,0.4); }
        .secondary { 
            background: linear-gradient(45deg, #6c757d, #545b62); 
            color: white; 
        }
        .secondary:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(108,117,125,0.4); }
        .install { 
            background: linear-gradient(45deg, #28a745, #1e7e34); 
            color: white; 
        }
        .install:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(40,167,69,0.4); }
        #locationInfo { 
            margin: 20px 0; 
            padding: 20px; 
            background: rgba(255, 255, 255, 0.1); 
            border-radius: 10px; 
            backdrop-filter: blur(5px);
        }
        .button-container {
            text-align: center;
            margin: 20px 0;
        }
        h1 { text-align: center; margin-bottom: 10px; }
        .subtitle { text-align: center; margin-bottom: 30px; opacity: 0.9; }
        #installButton {
            display: none;
        }    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 ivnet Location Tracker</h1>
        <p class="subtitle">Track device location and info securely</p>
          <div class="button-container">
            <button onclick="getLocation()" class="primary">📍 Get My Location</button>
            <button onclick="viewDashboard()" class="secondary">📊 View Dashboard</button>
            <button onclick="downloadData()" class="secondary">💾 Download Data</button>
            <button id="installButton" onclick="installApp()" class="install">📱 Install App</button>
        </div>
        
        <div id="status"></div>
        <div id="locationInfo"></div>
    </div>
    
    <script>
        let deferredPrompt;
        
        // Show install button when PWA can be installed
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            document.getElementById('installButton').style.display = 'inline-block';
            showStatus('📱 App can be installed! Click "Install App" button.', 'info');
        });
        
        // Handle successful installation
        window.addEventListener('appinstalled', (evt) => {
            showStatus('✅ App installed successfully!', 'success');
            document.getElementById('installButton').style.display = 'none';
        });
        
        // Install app function
        async function installApp() {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                
                if (outcome === 'accepted') {
                    showStatus('✅ Installing app...', 'success');
                } else {
                    showStatus('ℹ️ Installation cancelled', 'info');
                }
                deferredPrompt = null;
                document.getElementById('installButton').style.display = 'none';
            } else {
                // Fallback for browsers that don't support PWA install
                showStatus('📱 To install: Add to Home Screen from browser menu', 'info');
            }
        }
        
        // Register service worker
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('/sw.js')
                    .then(function(registration) {
                        console.log('SW registered: ', registration);
                    })
                    .catch(function(registrationError) {
                        console.log('SW registration failed: ', registrationError);
                    });
            });
        }
        
        function showStatus(message, type = 'success') {
            const status = document.getElementById('status');
            status.innerHTML = `<div class="status ${type}">${message}</div>`;
            
            // Auto-hide after 5 seconds for non-error messages
            if (type !== 'error') {
                setTimeout(() => {
                    status.innerHTML = '';
                }, 5000);
            }
        }
          function getLocation() {
            showStatus('🔍 Getting location...', 'info');
            
            if (!navigator.geolocation) {
                showStatus('❌ Geolocation not supported by this browser', 'error');
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
                        platform: navigator.platform,
                        language: navigator.language,
                        ipAddress: 'Will be detected by server',
                        sessionId: generateSessionId()
                    };
                    
                    // Save to local storage
                    saveToLocalStorage(data);
                    
                    // Display location info
                    document.getElementById('locationInfo').innerHTML = `
                        <h3>📍 Location Data Captured:</h3>
                        <p><strong>Latitude:</strong> ${data.latitude.toFixed(6)}</p>
                        <p><strong>Longitude:</strong> ${data.longitude.toFixed(6)}</p>
                        <p><strong>Accuracy:</strong> ${data.accuracy} meters</p>
                        <p><strong>Time:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                        <p><strong>Device:</strong> ${data.platform}</p>
                        <p><strong>Language:</strong> ${data.language}</p>
                        <p><strong>Session:</strong> ${data.sessionId}</p>
                    `;
                    
                    // Send to server
                    fetch('/api/location', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    })
                    .then(response => response.json())
                    .then(result => {
                        showStatus('✅ Location saved to server AND locally! Check dashboard or download data.', 'success');
                    })
                    .catch(error => {
                        showStatus('⚠️ Location saved locally (server offline). You can still download the data!', 'error');
                        console.error('Server error:', error);
                    });
                },
                error => {
                    let errorMsg = 'Unknown error';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMsg = 'Location access denied by user';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMsg = 'Location information unavailable';
                            break;
                        case error.TIMEOUT:
                            errorMsg = 'Location request timed out';
                            break;
                    }
                    showStatus(`❌ Error: ${errorMsg}`, 'error');
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        }
        
        function generateSessionId() {
            return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        
        function saveToLocalStorage(data) {
            let savedData = JSON.parse(localStorage.getItem('ivnet_location_data') || '[]');
            savedData.push(data);
            localStorage.setItem('ivnet_location_data', JSON.stringify(savedData));
        }
        
        function downloadData() {
            let savedData = JSON.parse(localStorage.getItem('ivnet_location_data') || '[]');
            
            if (savedData.length === 0) {
                showStatus('❌ No data to download. Track some locations first!', 'error');
                return;
            }
            
            const dataStr = JSON.stringify(savedData, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `ivnet_location_data_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
            showStatus(`✅ Downloaded ${savedData.length} location records!`, 'success');
        }
        
        function viewDashboard() {
            window.location.href = '/dashboard';
        }
        
        // Check if app is already installed
        window.addEventListener('DOMContentLoaded', (event) => {
            if (window.matchMedia('(display-mode: standalone)').matches) {
                showStatus('🎉 App is running in standalone mode!', 'success');
            }
        });
    </script>
</body>
</html>
'''

# Dashboard HTML with improved styling
dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">    <title>ivnet Dashboard</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#007bff">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 1000px; 
            margin: 0 auto; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        .location-item { 
            border: 1px solid rgba(255, 255, 255, 0.2); 
            margin: 15px 0; 
            padding: 20px; 
            border-radius: 10px; 
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
        }
        button { 
            padding: 12px 20px; 
            margin: 5px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            background: linear-gradient(45deg, #007bff, #0056b3); 
            color: white;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        button:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 5px 15px rgba(0,123,255,0.4); 
        }
        h1 { text-align: center; margin-bottom: 30px; }
        .button-container { text-align: center; margin-bottom: 30px; }
        .no-data { 
            text-align: center; 
            padding: 40px; 
            opacity: 0.8; 
            font-size: 18px;
        }
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .stat-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin: 5px;
            min-width: 120px;
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #ffd700;
        }
    </style>
</head>
<body>    <div class="container">
        <h1>📊 ivnet Location Dashboard</h1>
        
        <div class="button-container">
            <button onclick="location.href='/tracker'">🔙 Back to Tracker</button>
            <button onclick="refreshData()">🔄 Refresh Data</button>
            <button onclick="clearData()">🗑️ Clear All</button>
        </div>
        
        <div class="stats" id="stats"></div>
        <div id="locationList"></div>
    </div>
    
    <script>
        function refreshData() {
            fetch('/api/locations')
                .then(response => response.json())
                .then(data => {
                    updateStats(data);
                    displayLocations(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('locationList').innerHTML = 
                        '<div class="no-data">❌ Error loading data</div>';
                });
        }
        
        function updateStats(data) {
            const stats = document.getElementById('stats');
            stats.innerHTML = `
                <div class="stat-item">
                    <div class="stat-number">${data.length}</div>
                    <div>Total Tracks</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${data.length > 0 ? new Date(data[data.length-1].timestamp).toLocaleDateString() : 'N/A'}</div>
                    <div>Last Track</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${data.length > 0 ? Math.round(data[data.length-1].accuracy || 0) + 'm' : 'N/A'}</div>
                    <div>Last Accuracy</div>
                </div>
            `;
        }
        
        function displayLocations(data) {
            const list = document.getElementById('locationList');
            
            if (data.length === 0) {
                list.innerHTML = '<div class="no-data">📍 No location data yet.<br>Use the tracker to start collecting data!</div>';
                return;
            }
            
            list.innerHTML = data.reverse().map((item, index) => `
                <div class="location-item">
                    <h3>📍 Track #${item.id} (${data.length - index} of ${data.length})</h3>
                    <p><strong>📊 Coordinates:</strong> ${item.latitude.toFixed(6)}, ${item.longitude.toFixed(6)}</p>
                    <p><strong>🕒 Time:</strong> ${new Date(item.timestamp).toLocaleString()}</p>
                    <p><strong>📱 Device:</strong> ${item.platform || 'Unknown'}</p>
                    <p><strong>🎯 Accuracy:</strong> ${item.accuracy ? Math.round(item.accuracy) + ' meters' : 'Unknown'}</p>
                    <p><strong>🌐 Language:</strong> ${item.language || 'Unknown'}</p>
                    <p><strong>🔗 Maps Link:</strong> <a href="https://www.google.com/maps?q=${item.latitude},${item.longitude}" target="_blank" style="color: #ffd700;">View on Google Maps</a></p>
                </div>
            `).join('');
        }
        
        function clearData() {
            if (confirm('Are you sure you want to clear all location data?')) {
                fetch('/api/clear', { method: 'POST' })
                    .then(response => response.json())
                    .then(result => {
                        refreshData();
                        alert('✅ All data cleared!');
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('❌ Error clearing data');
                    });
            }
        }
        
        // Load data on page load
        refreshData();
        
        // Auto refresh every 30 seconds
        setInterval(refreshData, 30000);
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return '''
    <html>
    <head>        <title>ivnet Location Tracker</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                margin: 0;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                max-width: 500px;
                margin: 0 auto;
            }
            a { 
                color: #ffd700; 
                text-decoration: none; 
                font-size: 18px; 
                margin: 10px; 
                display: inline-block;
                padding: 10px 20px;
                border: 2px solid #ffd700;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            a:hover { 
                background: #ffd700; 
                color: #333; 
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>        <div class="container">
            <h1>🌍 ivnet Location Tracker</h1>
            <p>Professional location tracking system</p>
            <div>
                <a href="/tracker">📍 Start Tracking</a>
                <a href="/dashboard">📊 View Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/tracker')
def tracker():
    return render_template_string(tracker_html)

@app.route('/dashboard')
def dashboard():
    return render_template_string(dashboard_html)

@app.route('/manifest.json')
def manifest():    return {
        "name": "ivnet Location Tracker",
        "short_name": "ivnet Tracker",
        "description": "Track device location and info securely",
        "start_url": "/tracker",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#007bff",
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%23007bff'/%3E%3Ctext x='50' y='60' text-anchor='middle' fill='white' font-size='40'%3E📍%3C/text%3E%3C/svg%3E",
                "sizes": "192x192",
                "type": "image/svg+xml"
            },
            {
                "src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%23007bff'/%3E%3Ctext x='50' y='60' text-anchor='middle' fill='white' font-size='40'%3E📍%3C/text%3E%3C/svg%3E",
                "sizes": "512x512",
                "type": "image/svg+xml"
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
  '/api/locations',
  '/manifest.json'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});
''', 200, {'Content-Type': 'application/javascript'}

@app.route('/api/location', methods=['POST'])
def save_location():
    try:
        data = request.get_json()
        
        # Add server-side info
        data['id'] = len(location_data) + 1
        data['server_timestamp'] = datetime.now().isoformat()
        data['ip_address'] = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        data['user_agent'] = request.headers.get('User-Agent')
        
        # Store data
        location_data.append(data)
        
        # Send notification to your devices (multiple methods)
        send_location_notification(data)
        
        return jsonify({'status': 'success', 'id': data['id']})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def send_location_notification(data):
    """Send location data to your devices via multiple methods"""
    try:
        # Method 1: Email notification
        send_email_notification(data)
        
        # Method 2: Telegram notification (if you use Telegram)
        send_telegram_notification(data)
        
        # Method 3: Discord webhook (if you use Discord)
        send_discord_notification(data)
        
    except Exception as e:
        print(f"Notification error: {e}")

def send_email_notification(data):
    """Send location via email to your address"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    try:
        # Configure these with your email settings
        SENDER_EMAIL = "ivan.yochev2001@gmail.com"  # Change this
        SENDER_PASSWORD = "wkwo tfgq ehbc oxkc"   # Change this
        RECEIVER_EMAIL = "ivan.yochev2010@gmail.com" # Change this
        
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = f"🔴 LOCATION ALERT - Track #{data['id']}"
        
        # Create email body
        location_url = f"https://www.google.com/maps?q={data['latitude']},{data['longitude']}"
        
        body = f"""
🚨 NEW LOCATION TRACKED 🚨

📍 COORDINATES: {data['latitude']}, {data['longitude']}
🎯 ACCURACY: {data.get('accuracy', 'Unknown')} meters
⏰ TIME: {data.get('timestamp', 'Unknown')}
📱 DEVICE: {data.get('platform', 'Unknown')}
🌐 IP ADDRESS: {data.get('ip_address', 'Unknown')}
🔗 GOOGLE MAPS: {location_url}

Session ID: {data.get('sessionId', 'Unknown')}
User Agent: {data.get('userAgent', 'Unknown')}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, text)
        server.quit()
        
        print("✅ Email notification sent!")
        
    except Exception as e:
        print(f"Email error: {e}")

def send_telegram_notification(data):
    """Send location via Telegram bot"""
    import requests
    
    try:
        # Configure these with your Telegram bot settings
        BOT_TOKEN = "YOUR_BOT_TOKEN"  # Get from @BotFather
        CHAT_ID = "YOUR_CHAT_ID"      # Your Telegram user ID
        
        location_url = f"https://www.google.com/maps?q={data['latitude']},{data['longitude']}"
        
        message = f"""
🚨 *LOCATION ALERT* 🚨

📍 *Coordinates:* `{data['latitude']}, {data['longitude']}`
🎯 *Accuracy:* {data.get('accuracy', 'Unknown')} meters
⏰ *Time:* {data.get('timestamp', 'Unknown')}
📱 *Device:* {data.get('platform', 'Unknown')}
🌐 *IP:* {data.get('ip_address', 'Unknown')}

[🗺️ View on Google Maps]({location_url})
        """
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Telegram notification sent!")
        else:
            print(f"Telegram error: {response.text}")
            
    except Exception as e:
        print(f"Telegram error: {e}")

def send_discord_notification(data):
    """Send location via Discord webhook"""
    import requests
    
    try:
        # Configure this with your Discord webhook URL
        WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"
        
        location_url = f"https://www.google.com/maps?q={data['latitude']},{data['longitude']}"
        
        embed = {
            "title": "🚨 LOCATION ALERT",
            "color": 15158332,  # Red color
            "fields": [
                {"name": "📍 Coordinates", "value": f"{data['latitude']}, {data['longitude']}", "inline": True},
                {"name": "🎯 Accuracy", "value": f"{data.get('accuracy', 'Unknown')} meters", "inline": True},
                {"name": "⏰ Time", "value": data.get('timestamp', 'Unknown'), "inline": False},
                {"name": "📱 Device", "value": data.get('platform', 'Unknown'), "inline": True},
                {"name": "🌐 IP Address", "value": data.get('ip_address', 'Unknown'), "inline": True},
                {"name": "🗺️ Google Maps", "value": f"[View Location]({location_url})", "inline": False}
            ],
            "timestamp": data.get('timestamp', datetime.now().isoformat())
        }
        
        payload = {"embeds": [embed]}
        
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        
        if response.status_code == 204:
            print("✅ Discord notification sent!")
        else:
            print(f"Discord error: {response.text}")
            
    except Exception as e:
        print(f"Discord error: {e}")

@app.route('/api/locations', methods=['GET'])
def get_locations():
    return jsonify(location_data)

@app.route('/api/clear', methods=['POST'])
def clear_locations():
    global location_data
    location_data = []
    return jsonify({'status': 'success', 'message': 'All data cleared'})

if __name__ == '__main__':
    app.run(debug=True)

# Vercel serverless function handler
def handler(request):
    return app(request.environ, request.start_response)

# Export the Flask app for Vercel
application = app
