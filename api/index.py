from flask import Flask, request, jsonify, render_template_string
import json
from datetime import datetime

app = Flask(__name__)

# Store location data in memory (for demo purposes)
location_data = []

# HTML template for the tracker
tracker_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IvNet Location Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
        button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
        .primary { background-color: #007bff; color: white; }
        .secondary { background-color: #6c757d; color: white; }
        #locationInfo { margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>🌍 IvNet Location Tracker</h1>
    <p>Track device location and info securely.</p>
    
    <button onclick="getLocation()" class="primary">📍 Get My Location</button>
    <button onclick="viewDashboard()" class="secondary">📊 View Dashboard</button>
    
    <div id="status"></div>
    <div id="locationInfo"></div>
    
    <script>
        function showStatus(message, type = 'success') {
            const status = document.getElementById('status');
            status.innerHTML = `<div class="status ${type}">${message}</div>`;
        }
        
        function getLocation() {
            showStatus('🔍 Getting location...', 'success');
            
            if (!navigator.geolocation) {
                showStatus('❌ Geolocation not supported', 'error');
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
                        language: navigator.language
                    };
                    
                    // Display location info
                    document.getElementById('locationInfo').innerHTML = `
                        <h3>📍 Location Data:</h3>
                        <p><strong>Latitude:</strong> ${data.latitude}</p>
                        <p><strong>Longitude:</strong> ${data.longitude}</p>
                        <p><strong>Accuracy:</strong> ${data.accuracy} meters</p>
                        <p><strong>Time:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                        <p><strong>Device:</strong> ${data.platform}</p>
                    `;
                    
                    // Send to server
                    fetch('/api/location', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    })
                    .then(response => response.json())
                    .then(result => {
                        showStatus('✅ Location saved successfully!', 'success');
                    })
                    .catch(error => {
                        showStatus('⚠️ Saved locally, server unavailable', 'error');
                    });
                },
                error => {
                    showStatus(`❌ Error: ${error.message}`, 'error');
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

# Dashboard HTML
dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IvNet Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }
        .location-item { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; background-color: #007bff; color: white; }
    </style>
</head>
<body>
    <h1>📊 IvNet Location Dashboard</h1>
    <button onclick="location.href='/tracker'">🔙 Back to Tracker</button>
    <button onclick="refreshData()">🔄 Refresh</button>
    
    <div id="locationList"></div>
    
    <script>
        function refreshData() {
            fetch('/api/locations')
                .then(response => response.json())
                .then(data => {
                    const list = document.getElementById('locationList');
                    if (data.length === 0) {
                        list.innerHTML = '<p>No location data yet. Use the tracker first!</p>';
                        return;
                    }
                    
                    list.innerHTML = data.map(item => `
                        <div class="location-item">
                            <h3>📍 Location #${item.id}</h3>
                            <p><strong>Coordinates:</strong> ${item.latitude}, ${item.longitude}</p>
                            <p><strong>Time:</strong> ${new Date(item.timestamp).toLocaleString()}</p>
                            <p><strong>Device:</strong> ${item.platform}</p>
                            <p><strong>Accuracy:</strong> ${item.accuracy} meters</p>
                        </div>
                    `).join('');
                })
                .catch(error => console.error('Error:', error));
        }
        
        // Load data on page load
        refreshData();
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return '<h1>🌍 IvNet Location Tracker</h1><p><a href="/tracker">Go to Tracker</a> | <a href="/dashboard">View Dashboard</a></p>'

@app.route('/tracker')
def tracker():
    return render_template_string(tracker_html)

@app.route('/dashboard')
def dashboard():
    return render_template_string(dashboard_html)

@app.route('/api/location', methods=['POST'])
def save_location():
    try:
        data = request.get_json()
        data['id'] = len(location_data) + 1
        location_data.append(data)
        return jsonify({'status': 'success', 'id': data['id']})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/locations', methods=['GET'])
def get_locations():
    return jsonify(location_data)

if __name__ == '__main__':
    app.run(debug=True)
