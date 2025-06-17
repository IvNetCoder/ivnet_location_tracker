from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
import os
import sqlite3

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    conn = sqlite3.connect('/tmp/tracking_data.db')
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
        conn = sqlite3.connect('/tmp/tracking_data.db')
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
        
        return jsonify({"status": "success", "message": "Tracking data received"}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    return "<h1>Dashboard coming soon...</h1>"

@app.route('/')
def index():
    return """
    <h1>IVNet Location Tracker</h1>
    <p><a href="/tracker">Open Tracker</a></p>
    <p><a href="/dashboard">View Dashboard</a></p>
    """

# Vercel entry point
def handler(request):
    return app(request.environ, lambda *args: None)
