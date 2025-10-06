"""
Professional Analytics Dashboard for PhoneCheckerBot
Enterprise-grade web interface for monitoring and analytics.
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import json
import os
from datetime import datetime, timedelta
from functools import wraps
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv('DASHBOARD_SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration
ANALYTICS_DB = 'analytics.db'
ADMIN_PASSWORD_HASH = None

def init_admin_password():
    """Initialize admin password from environment"""
    global ADMIN_PASSWORD_HASH
    admin_password = os.getenv('DASHBOARD_ADMIN_PASSWORD', 'admin123')
    ADMIN_PASSWORD_HASH = generate_password_hash(admin_password)

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_analytics_db():
    """Initialize analytics database with required tables"""
    with sqlite3.connect(ANALYTICS_DB) as conn:
        # User analytics table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        ''')
        
        # Performance metrics table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT,
                duration_ms REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        ''')
        
        # System health table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS system_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                active_users INTEGER
            )
        ''')
        
        # Spam detection stats
        conn.execute('''
            CREATE TABLE IF NOT EXISTS spam_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT,
                is_spam BOOLEAN,
                confidence_score REAL,
                detection_method TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['authenticated'] = True
            session['login_time'] = datetime.now().isoformat()
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password', 'error')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PhoneCheckerBot Admin</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 40px; background: #f5f5f5; }
            .login-container { max-width: 400px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .logo { text-align: center; color: #2c3e50; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; color: #555; }
            input[type="password"] { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
            .btn { width: 100%; padding: 12px; background: #3498db; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; }
            .btn:hover { background: #2980b9; }
            .error { color: #e74c3c; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h1 class="logo">🤖 PhoneCheckerBot</h1>
            <h2 style="text-align: center; color: #7f8c8d;">Admin Dashboard</h2>
            <form method="post">
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">Login</button>
                {% if error %}
                <div class="error">{{ error }}</div>
                {% endif %}
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/dashboard')
@require_auth
def dashboard():
    """Main analytics dashboard"""
    # Get analytics data
    stats = get_dashboard_stats()
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PhoneCheckerBot Analytics Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f8f9fa; }}
            .header {{ background: #2c3e50; color: white; padding: 20px; }}
            .header h1 {{ margin: 0; display: inline-block; }}
            .logout {{ float: right; background: #e74c3c; padding: 10px 20px; text-decoration: none; color: white; border-radius: 4px; }}
            .container {{ padding: 20px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
            .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
            .chart-container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .chart-container h3 {{ margin-top: 0; color: #2c3e50; }}
            .chart-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .refresh-btn {{ background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-bottom: 20px; }}
            .refresh-btn:hover {{ background: #229954; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 PhoneCheckerBot Analytics</h1>
            <a href="/admin/logout" class="logout">Logout</a>
        </div>
        
        <div class="container">
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Data</button>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats.get('total_users', 0)}</div>
                    <div class="stat-label">Total Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats.get('daily_requests', 0)}</div>
                    <div class="stat-label">Today's Requests</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats.get('spam_detected', 0)}</div>
                    <div class="stat-label">Spam Numbers Detected</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats.get('avg_response_time', 0)}ms</div>
                    <div class="stat-label">Avg Response Time</div>
                </div>
            </div>
            
            <div class="chart-row">
                <div class="chart-container">
                    <h3>📊 Daily Activity (Last 7 Days)</h3>
                    <canvas id="activityChart" width="400" height="200"></canvas>
                </div>
                <div class="chart-container">
                    <h3>🎯 Spam Detection Rate</h3>
                    <canvas id="spamChart" width="400" height="200"></canvas>
                </div>
            </div>
            
            <div class="chart-container">
                <h3>⚡ Performance Metrics</h3>
                <canvas id="performanceChart" width="800" height="300"></canvas>
            </div>
            
            <div class="chart-container">
                <h3>📱 Recent Activity</h3>
                <div style="max-height: 400px; overflow-y: auto;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #ecf0f1;">
                                <th style="padding: 10px; text-align: left;">Time</th>
                                <th style="padding: 10px; text-align: left;">User</th>
                                <th style="padding: 10px; text-align: left;">Action</th>
                                <th style="padding: 10px; text-align: left;">Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            {generate_recent_activity_rows(stats.get('recent_activity', []))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <script>
            // Activity Chart
            const activityCtx = document.getElementById('activityChart').getContext('2d');
            new Chart(activityCtx, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(stats.get('activity_labels', []))},
                    datasets: [{{
                        label: 'Requests',
                        data: {json.dumps(stats.get('activity_data', []))},
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{ beginAtZero: true }}
                    }}
                }}
            }});
            
            // Spam Detection Chart
            const spamCtx = document.getElementById('spamChart').getContext('2d');
            new Chart(spamCtx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Clean Numbers', 'Spam Detected'],
                    datasets: [{{
                        data: [{stats.get('clean_numbers', 85)}, {stats.get('spam_numbers', 15)}],
                        backgroundColor: ['#27ae60', '#e74c3c']
                    }}]
                }},
                options: {{
                    responsive: true
                }}
            }});
            
            // Performance Chart
            const perfCtx = document.getElementById('performanceChart').getContext('2d');
            new Chart(perfCtx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(stats.get('perf_labels', []))},
                    datasets: [{{
                        label: 'Response Time (ms)',
                        data: {json.dumps(stats.get('perf_data', []))},
                        backgroundColor: '#9b59b6'
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{ beginAtZero: true }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    '''

def generate_recent_activity_rows(activities):
    """Generate HTML rows for recent activity table"""
    if not activities:
        return '<tr><td colspan="4" style="padding: 20px; text-align: center; color: #7f8c8d;">No recent activity</td></tr>'
    
    rows = []
    for activity in activities[:10]:  # Show last 10 activities
        rows.append(f'''
            <tr style="border-bottom: 1px solid #ecf0f1;">
                <td style="padding: 10px;">{activity.get('time', 'N/A')}</td>
                <td style="padding: 10px;">User {activity.get('user_id', 'N/A')}</td>
                <td style="padding: 10px;">{activity.get('action', 'N/A')}</td>
                <td style="padding: 10px;">{activity.get('details', 'N/A')}</td>
            </tr>
        ''')
    return ''.join(rows)

def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    try:
        with sqlite3.connect(ANALYTICS_DB) as conn:
            # Basic stats
            total_users = conn.execute("SELECT COUNT(DISTINCT user_id) FROM user_analytics").fetchone()[0] or 0
            
            # Daily requests (last 24 hours)
            yesterday = datetime.now() - timedelta(hours=24)
            daily_requests = conn.execute(
                "SELECT COUNT(*) FROM user_analytics WHERE timestamp > ?", 
                (yesterday,)
            ).fetchone()[0] or 0
            
            # Spam detection stats
            spam_detected = conn.execute("SELECT COUNT(*) FROM spam_stats WHERE is_spam = 1").fetchone()[0] or 0
            
            # Average response time
            avg_response = conn.execute("SELECT AVG(duration_ms) FROM performance_metrics").fetchone()[0] or 0
            
            # Activity data for chart (last 7 days)
            activity_data = []
            activity_labels = []
            for i in range(6, -1, -1):
                date = datetime.now() - timedelta(days=i)
                day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                
                count = conn.execute(
                    "SELECT COUNT(*) FROM user_analytics WHERE timestamp BETWEEN ? AND ?",
                    (day_start, day_end)
                ).fetchone()[0] or 0
                
                activity_data.append(count)
                activity_labels.append(date.strftime('%m/%d'))
            
            # Performance data
            perf_data = []
            perf_labels = []
            operations = conn.execute(
                "SELECT operation, AVG(duration_ms) FROM performance_metrics GROUP BY operation LIMIT 5"
            ).fetchall()
            
            for op, avg_time in operations:
                perf_labels.append(op.split('.')[-1])  # Get function name only
                perf_data.append(round(avg_time, 2))
            
            # Recent activity
            recent_activity = []
            recent = conn.execute(
                "SELECT user_id, action, timestamp, details FROM user_analytics ORDER BY timestamp DESC LIMIT 10"
            ).fetchall()
            
            for user_id, action, timestamp, details in recent:
                recent_activity.append({
                    'user_id': user_id,
                    'action': action,
                    'time': timestamp.split('.')[0] if timestamp else 'N/A',  # Remove microseconds
                    'details': details[:50] + '...' if details and len(details) > 50 else details or ''
                })
            
            return {
                'total_users': total_users,
                'daily_requests': daily_requests,
                'spam_detected': spam_detected,
                'avg_response_time': round(avg_response, 2),
                'activity_data': activity_data,
                'activity_labels': activity_labels,
                'perf_data': perf_data,
                'perf_labels': perf_labels,
                'clean_numbers': max(0, 100 - spam_detected),
                'spam_numbers': spam_detected,
                'recent_activity': recent_activity
            }
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        return {
            'total_users': 0, 'daily_requests': 0, 'spam_detected': 0, 'avg_response_time': 0,
            'activity_data': [0]*7, 'activity_labels': ['N/A']*7,
            'perf_data': [0], 'perf_labels': ['N/A'],
            'clean_numbers': 85, 'spam_numbers': 15, 'recent_activity': []
        }

@app.route('/admin/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/analytics')
@require_auth
def api_analytics():
    """API endpoint for analytics data"""
    return jsonify(get_dashboard_stats())

@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'dashboard'
    })

@app.route('/')
def index():
    """Redirect to admin dashboard"""
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_admin_password()
    init_analytics_db()
    
    # Add some sample data for demonstration
    try:
        with sqlite3.connect(ANALYTICS_DB) as conn:
            # Sample user analytics
            sample_actions = ['phone_lookup', 'verify_otp', 'report_spam', 'check_status']
            for i in range(50):
                user_id = 1000 + (i % 10)
                action = sample_actions[i % len(sample_actions)]
                timestamp = datetime.now() - timedelta(hours=i//2)
                conn.execute(
                    "INSERT OR IGNORE INTO user_analytics (user_id, action, timestamp) VALUES (?, ?, ?)",
                    (user_id, action, timestamp)
                )
            
            # Sample performance metrics
            operations = ['bot.handle_message', 'db.lookup_phone', 'api.verify_otp', 'ml.classify_spam']
            for i in range(20):
                operation = operations[i % len(operations)]
                duration = 50 + (i * 10)  # Simulate varying response times
                timestamp = datetime.now() - timedelta(hours=i)
                conn.execute(
                    "INSERT OR IGNORE INTO performance_metrics (operation, duration_ms, timestamp) VALUES (?, ?, ?)",
                    (operation, duration, timestamp)
                )
    except Exception as e:
        print(f"Error adding sample data: {e}")
    
    port = int(os.getenv('DASHBOARD_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('DEBUG', 'false').lower() == 'true')