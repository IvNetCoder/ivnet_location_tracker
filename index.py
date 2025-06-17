from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

# Store location data in memory (for demo purposes)
location_data = []

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ivnet Location Tracker</title>
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
    <body>
        <div class="container">
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
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ivnet Location Tracker</title>
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌍 ivnet Location Tracker</h1>
            <p class="subtitle">Track device location and info securely</p>
            
            <div class="button-container">
                <button onclick="getLocation()" class="primary">📍 Get My Location</button>
                <button onclick="viewDashboard()" class="secondary">📊 View Dashboard</button>
            </div>
            
            <div id="status"></div>
            <div id="locationInfo"></div>
        </div>
        
        <script>
            function showStatus(message, type = 'success') {
                const status = document.getElementById('status');
                status.innerHTML = `<div class="status ${type}">${message}</div>`;
                
                setTimeout(() => {
                    if (type !== 'error') {
                        status.innerHTML = '';
                    }
                }, 5000);
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
                            sessionId: 'session_' + Date.now()
                        };
                        
                        document.getElementById('locationInfo').innerHTML = `
                            <h3>📍 Location Data Captured:</h3>
                            <p><strong>Latitude:</strong> ${data.latitude.toFixed(6)}</p>
                            <p><strong>Longitude:</strong> ${data.longitude.toFixed(6)}</p>
                            <p><strong>Accuracy:</strong> ${data.accuracy} meters</p>
                            <p><strong>Time:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                            <p><strong>Device:</strong> ${data.platform}</p>
                            <p><strong>Session:</strong> ${data.sessionId}</p>
                            <p><strong>🗺️ Maps:</strong> <a href="https://www.google.com/maps?q=${data.latitude},${data.longitude}" target="_blank" style="color: #ffd700;">View on Google Maps</a></p>
                        `;
                        
                        fetch('/api/location', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(data)
                        })
                        .then(response => response.json())
                        .then(result => {
                            showStatus('✅ Location saved successfully! Server is ONLINE!', 'success');
                        })
                        .catch(error => {
                            showStatus('⚠️ Location captured but server error', 'error');
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
            
            function viewDashboard() {
                window.location.href = '/dashboard';
            }
        </script>
    </body>
    </html>
    '''

@app.route('/dashboard')
def dashboard():
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ivnet Dashboard</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                max-width: 1000px; 
                margin: 0 auto; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }}
            .container {{
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }}
            .location-item {{ 
                border: 1px solid rgba(255, 255, 255, 0.2); 
                margin: 15px 0; 
                padding: 20px; 
                border-radius: 10px; 
                background: rgba(255, 255, 255, 0.1);
            }}
            button {{ 
                padding: 12px 20px; 
                margin: 5px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                background: linear-gradient(45deg, #007bff, #0056b3); 
                color: white;
                font-weight: bold;
            }}
            h1 {{ text-align: center; margin-bottom: 30px; }}
            .button-container {{ text-align: center; margin-bottom: 30px; }}
            .stats {{
                display: flex;
                justify-content: space-around;
                margin: 20px 0;
                flex-wrap: wrap;
            }}
            .stat-item {{
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                margin: 5px;
                min-width: 120px;
            }}
            .stat-number {{
                font-size: 24px;
                font-weight: bold;
                color: #ffd700;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 ivnet Location Dashboard</h1>
            
            <div class="button-container">
                <button onclick="location.href='/tracker'">🔙 Back to Tracker</button>
                <button onclick="location.reload()">🔄 Refresh</button>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number">{len(location_data)}</div>
                    <div>Total Locations</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{'Online' if len(location_data) >= 0 else 'Offline'}</div>
                    <div>Server Status</div>
                </div>
            </div>
            
            <div id="locationList">
                {'<div style="text-align: center; padding: 40px; opacity: 0.8;">📍 No location data yet. Use the tracker to start collecting data!</div>' if len(location_data) == 0 else ''.join([f'''
                <div class="location-item">
                    <h3>📍 Track #{item.get('id', i+1)}</h3>
                    <p><strong>📊 Coordinates:</strong> {item.get('latitude', 'Unknown')}, {item.get('longitude', 'Unknown')}</p>
                    <p><strong>🕒 Time:</strong> {item.get('timestamp', 'Unknown')}</p>
                    <p><strong>📱 Device:</strong> {item.get('platform', 'Unknown')}</p>
                    <p><strong>🎯 Accuracy:</strong> {item.get('accuracy', 'Unknown')} meters</p>
                    <p><strong>🔗 Maps:</strong> <a href="https://www.google.com/maps?q={item.get('latitude', 0)},{item.get('longitude', 0)}" target="_blank" style="color: #ffd700;">View on Google Maps</a></p>
                </div>
                ''' for i, item in enumerate(reversed(location_data))])}
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/api/location', methods=['POST'])
def save_location():
    try:
        data = request.get_json()
        
        # Add server-side info
        data['id'] = len(location_data) + 1
        data['server_timestamp'] = datetime.now().isoformat()
        data['ip_address'] = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'Unknown'))
        
        # Store data
        location_data.append(data)
        
        # Print to console (will show in Vercel logs)
        print(f"🔴 NEW LOCATION TRACKED:")
        print(f"   📍 Coordinates: {data.get('latitude')}, {data.get('longitude')}")
        print(f"   🕒 Time: {data.get('timestamp')}")
        print(f"   📱 Device: {data.get('platform')}")
        print(f"   🌐 IP: {data.get('ip_address')}")
        print(f"   🆔 Session: {data.get('sessionId')}")
        
        return jsonify({'status': 'success', 'id': data['id'], 'message': 'Location saved successfully!'})
    except Exception as e:
        print(f"❌ Error saving location: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/locations', methods=['GET'])
def get_locations():
    return jsonify(location_data)

@app.route('/api/clear', methods=['POST'])
def clear_locations():
    global location_data
    location_data = []
    return jsonify({'status': 'success', 'message': 'All data cleared'})

# Test endpoint to check if server is working
@app.route('/api/test')
def test():
    return jsonify({'status': 'online', 'message': 'Server is working!', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True)
