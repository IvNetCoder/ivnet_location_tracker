from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import datetime
import os
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database setup
def init_db():
    conn = sqlite3.connect('tracking_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tracking_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    browser TEXT,
                    platform TEXT,
                    language TEXT,
                    screen TEXT,
                    timezone TEXT,
                    latitude REAL,
                    longitude REAL,
                    location_accuracy REAL,
                    event_type TEXT,
                    timestamp TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

@app.route('/track', methods=['POST'])
def track_device():
    try:
        data = request.get_json()
        
        # Extract location data
        location = data.get('location', {})
        latitude = None
        longitude = None
        accuracy = None
        
        if isinstance(location, dict) and 'latitude' in location:
            latitude = location.get('latitude')
            longitude = location.get('longitude')
            accuracy = location.get('accuracy')
        
        # Store in database
        conn = sqlite3.connect('tracking_data.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO tracking_logs 
                    (session_id, ip_address, user_agent, browser, platform, language, 
                     screen, timezone, latitude, longitude, location_accuracy, event_type, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (
                     data.get('sessionId'),
                     data.get('ipAddress'),
                     data.get('userAgent'),
                     data.get('browser'),
                     data.get('platform'),
                     data.get('language'),
                     data.get('screen'),
                     data.get('timezone'),
                     latitude,
                     longitude,
                     accuracy,
                     data.get('event', 'initial_load'),
                     data.get('timestamp')
                 ))
        
        conn.commit()
        conn.close()
        
        print(f"📍 New tracking data received:")
        print(f"   Session: {data.get('sessionId')}")
        print(f"   IP: {data.get('ipAddress')}")
        print(f"   Browser: {data.get('browser')}")
        print(f"   Location: {latitude}, {longitude}" if latitude else "   Location: Not available")
        print(f"   Timestamp: {data.get('timestamp')}")
        print("-" * 50)
        
        return jsonify({"status": "success", "message": "Tracking data received"}), 200
        
    except Exception as e:
        print(f"Error processing tracking data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """Web dashboard to view tracking data"""
    try:
        conn = sqlite3.connect('tracking_data.db')
        c = conn.cursor()
        c.execute('''SELECT * FROM tracking_logs ORDER BY created_at DESC LIMIT 100''')
        logs = c.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        columns = ['id', 'session_id', 'ip_address', 'user_agent', 'browser', 'platform', 
                  'language', 'screen', 'timezone', 'latitude', 'longitude', 'location_accuracy', 
                  'event_type', 'timestamp', 'created_at']
        
        logs_data = []
        for log in logs:
            log_dict = dict(zip(columns, log))
            logs_data.append(log_dict)
        
        dashboard_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>IVNet Tracking Dashboard</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    background: #f5f5f5;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    text-align: center;
                }
                .stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .stat-card {
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }
                .stat-value {
                    font-size: 2em;
                    font-weight: bold;
                    color: #667eea;
                }
                .stat-label {
                    color: #666;
                    margin-top: 5px;
                }
                table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                th, td { 
                    padding: 12px; 
                    text-align: left; 
                    border-bottom: 1px solid #ddd; 
                }
                th { 
                    background: #667eea; 
                    color: white; 
                    font-weight: bold;
                }
                tr:hover { 
                    background: #f8f9fa; 
                }
                .location-link {
                    color: #667eea;
                    text-decoration: none;
                }
                .location-link:hover {
                    text-decoration: underline;
                }
                .refresh-btn {
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-bottom: 20px;
                }
                .refresh-btn:hover {
                    background: #5a6fd8;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📍 IVNet Location Tracking Dashboard</h1>
                <p>Real-time device tracking and monitoring</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{{ total_logs }}</div>
                    <div class="stat-label">Total Logs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ unique_sessions }}</div>
                    <div class="stat-label">Unique Sessions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ unique_ips }}</div>
                    <div class="stat-label">Unique IPs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ locations_count }}</div>
                    <div class="stat-label">With Location</div>
                </div>
            </div>
            
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Data</button>
            
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Session ID</th>
                        <th>IP Address</th>
                        <th>Browser</th>
                        <th>Platform</th>
                        <th>Location</th>
                        <th>Event</th>
                    </tr>
                </thead>
                <tbody>
                    {% for log in logs %}
                    <tr>
                        <td>{{ log.created_at }}</td>
                        <td>{{ log.session_id[:8] }}...</td>
                        <td>{{ log.ip_address }}</td>
                        <td>{{ log.browser }}</td>
                        <td>{{ log.platform }}</td>
                        <td>
                            {% if log.latitude and log.longitude %}
                                <a href="https://www.google.com/maps?q={{ log.latitude }},{{ log.longitude }}" 
                                   target="_blank" class="location-link">
                                   {{ "%.6f"|format(log.latitude) }}, {{ "%.6f"|format(log.longitude) }}
                                </a>
                            {% else %}
                                Not available
                            {% endif %}
                        </td>
                        <td>{{ log.event_type }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <script>
                // Auto-refresh every 30 seconds
                setTimeout(() => location.reload(), 30000);
            </script>
        </body>
        </html>
        """
        
        # Calculate statistics
        total_logs = len(logs_data)
        unique_sessions = len(set(log['session_id'] for log in logs_data if log['session_id']))
        unique_ips = len(set(log['ip_address'] for log in logs_data if log['ip_address']))
        locations_count = len([log for log in logs_data if log['latitude'] and log['longitude']])
        
        from jinja2 import Template
        template = Template(dashboard_html)
        
        return template.render(
            logs=logs_data,
            total_logs=total_logs,
            unique_sessions=unique_sessions,
            unique_ips=unique_ips,
            locations_count=locations_count
        )
        
    except Exception as e:
        return f"Error loading dashboard: {str(e)}", 500

@app.route('/api/logs')
def get_logs():
    """API endpoint to get tracking logs"""
    try:
        conn = sqlite3.connect('tracking_data.db')
        c = conn.cursor()
        c.execute('''SELECT * FROM tracking_logs ORDER BY created_at DESC''')
        logs = c.fetchall()
        conn.close()
        
        columns = ['id', 'session_id', 'ip_address', 'user_agent', 'browser', 'platform', 
                  'language', 'screen', 'timezone', 'latitude', 'longitude', 'location_accuracy', 
                  'event_type', 'timestamp', 'created_at']
        
        logs_data = []
        for log in logs:
            log_dict = dict(zip(columns, log))
            logs_data.append(log_dict)
        
        return jsonify(logs_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tracker')
def serve_tracker():
    """Serve the tracker HTML file directly"""
    try:
        with open('ivnet_location_tracker.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Tracker HTML file not found!", 404

@app.route('/')
def index():
    return """
    <h1>IVNet Location Tracker Server</h1>
    <p>Server is running!</p>
    <ul>
        <li><a href="/tracker">📱 Open Tracker App</a></li>
        <li><a href="/dashboard">📊 View Tracking Dashboard</a></li>
        <li><a href="/api/logs">📋 View Raw Logs (JSON)</a></li>
    </ul>
    <p><strong>Share this link for tracking:</strong> <code>http://localhost:5000/tracker</code></p>
    """

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting IVNet Location Tracker Server...")
    print(f"📍 Server will be available at: http://localhost:{port}")
    print("📊 Dashboard will be available at: /dashboard")
    print("📝 Make sure to open ivnet_location_tracker.html in a web browser")
    print("-" * 60)
    
    # Get local IP address
    import socket
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"🌐 For phones/other devices, use: http://{local_ip}:{port}/tracker")
    except:
        pass
    print("-" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=port)
