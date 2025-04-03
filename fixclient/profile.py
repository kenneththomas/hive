import sqlite3
from pathlib import Path
from flask import jsonify, render_template, request

# Database setup
DB_PATH = Path('fixclient/instance/ourteam.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_profile(scope_id):
    """Get profile information for a given scope_id (email)"""
    conn = get_db()
    try:
        profile = conn.execute('SELECT * FROM employee WHERE email = ?', (scope_id,)).fetchone()
        return dict(profile) if profile else None
    finally:
        conn.close()

def update_profile(scope_id, data):
    """Update profile information for a given scope_id"""
    conn = get_db()
    try:
        # Only update fields that are provided in the request
        update_fields = []
        update_values = []
        for field in ['name', 'title', 'department', 'email', 'phone', 'picture_url', 'bio', 'location']:
            if field in data:
                update_fields.append(f"{field} = ?")
                update_values.append(data[field])
        
        if update_fields:
            update_values.append(scope_id)
            query = f"UPDATE employee SET {', '.join(update_fields)} WHERE email = ?"
            conn.execute(query, update_values)
            conn.commit()
        
        # Get updated profile
        return get_profile(scope_id)
    finally:
        conn.close()

def register_profile_routes(app):
    """Register all profile-related routes with the Flask app"""
    
    @app.route('/profile/<scope_id>')
    def profile_page(scope_id):
        """Render the profile page for a given scope_id"""
        profile = get_profile(scope_id)
        return render_template('profile.html', profile=profile, scope_id=scope_id)

    @app.route('/api/profile/<scope_id>')
    def get_profile_api(scope_id):
        """API endpoint to get profile information"""
        profile = get_profile(scope_id)
        return jsonify(profile if profile else {})

    @app.route('/api/profile/<scope_id>', methods=['POST'])
    def update_profile_api(scope_id):
        """API endpoint to update profile information"""
        data = request.json
        profile = update_profile(scope_id, data)
        return jsonify(profile if profile else {}) 