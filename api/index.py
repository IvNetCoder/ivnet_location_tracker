from flask import Flask
import json

app = Flask(__name__)

# Simple in-memory storage
locations = []

@app.route('/')
def home():
    return '''
    <html>
    <body style="font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; margin: 0;">
        <div style="background: rgba(255,255,255,0.1); padding: 40px; border-radius: 15px; max-width: 500px; margin: 0 auto;">
            <h1>🌍 ivnet Location Tracker</h1>
            <p>Professional location tracking system</p>
            <a href="/tracker" style="color: #ffd700; text-decoration: none; font-size: 18px; margin: 10px; display: inline-block; padding: 10px 20px; border: 2px solid #ffd700; border-radius: 8px;">📍 Start Tracking</a>
            <a href="/dashboard" style="color: #ffd700; text-decoration: none; font-size: 18px; margin: 10px; display: inline-block; padding: 10px 20px; border: 2px solid #ffd700; border-radius: 8px;">📊 View Dashboard</a>
        </div>
    </body>
    </html>
    '''

@app.route('/tracker')
def tracker():
    return '''
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ivnet Location Tracker</title>
    </head>
    <body style="font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: white;">
        <div style="background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px;">
            <h1 style="text-align: center;">🌍 ivnet Location Tracker</h1>
            <p style="text-align: center; opacity: 0.9;">Track device location and info securely</p>
            
            <div style="text-align: center; margin: 20px 0;">
                <button onclick="getLocation()" style="padding: 15px 25px; margin: 10px; border: none; border-radius: 10px; cursor: pointer; font-size: 16px; font-weight: bold; background: linear-gradient(45deg, #007bff, #0056b3); color: white;">📍 Get My Location</button>
                <button onclick="location.href='/dashboard'" style="padding: 15px 25px; margin: 10px; border: none; border-radius: 10px; cursor: pointer; font-size: 16px; font-weight: bold; background: linear-gradient(45deg, #6c757d, #545b62); color: white;">📊 View Dashboard</button>
            </div>
            
            <div id="status"></div>
            <div id="locationInfo"></div>
        </div>
        
        <script>
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
