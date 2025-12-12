from flask import Flask, g, render_template, session, redirect, url_for
import sqlite3
from config import Config
import os

def log_activity(user_id, activity_type, game_id=None, description=None):
    """
    Helper to insert a row into the activities table.
    activity_type: e.g. 'list_update', 'review'
    description: short text like 'added to wishlist ' – the game title is joined in the query.
    """
    db = get_db()
    db.execute(
        'INSERT INTO activities (user_id, activity_type, game_id, description) VALUES (?, ?, ?, ?)',
        (user_id, activity_type, game_id, description)
    )
    db.commit()

from db import get_db, query_db
from modules.auth import login_required
from modules.admin import admin_bp

  

app = Flask(__name__)
app.config.from_object(Config)

# Ensure necessary directories exist
os.makedirs('var', exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database helper functions
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


# Make query_db available in Jinja templates
app.jinja_env.globals.update(query_db=query_db)

# Register blueprints
from modules.auth import auth_bp
from modules.games import games_bp
from modules.users import users_bp
from modules.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(games_bp)
app.register_blueprint(users_bp)
app.register_blueprint(admin_bp)

# Main routes
@app.route('/')
def index():
    """Landing page - accessible without login"""
    # If user is already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    db = get_db()
    
    # Get featured/popular games
    featured_games = db.execute('''
        SELECT * FROM games 
        ORDER BY average_rating DESC, created_at DESC 
        LIMIT 6
    ''').fetchall()
    
    # Get recent reviews
    recent_reviews = db.execute('''
        SELECT r.*, g.title, g.cover_image_url, u.username
        FROM reviews r
        JOIN games g ON r.game_id = g.id
        JOIN users u ON r.user_id = u.id
        WHERE r.is_anonymous = 0
        ORDER BY r.created_at DESC
        LIMIT 3
    ''').fetchall()
    
    return render_template('index.html', 
                         featured_games=featured_games,
                         recent_reviews=recent_reviews)

@app.route('/home')
# Ensure a user is logged in
@login_required 
def home():
    """Logged-in home page with personalized content"""
    db = get_db()
    
    # Get user's recent activity
    recent_activity = db.execute('''
        SELECT ug.*, g.title, g.cover_image_url
        FROM user_games ug
        JOIN games g ON ug.game_id = g.id
        WHERE ug.user_id = ?
        ORDER BY ug.updated_at DESC
        LIMIT 5
    ''', (session['user_id'],)).fetchall()
    
    # Get recommendations based on genres user likes
    recommendations = db.execute('''
        SELECT DISTINCT g.*
        FROM games g
        WHERE g.genre IN (
            SELECT DISTINCT g2.genre
            FROM games g2
            JOIN user_games ug ON g2.id = ug.game_id
            WHERE ug.user_id = ? AND ug.status = 'completed'
            LIMIT 3
        )
        AND g.id NOT IN (
            SELECT game_id FROM user_games WHERE user_id = ?
        )
        ORDER BY g.average_rating DESC
        LIMIT 6
    ''', (session['user_id'], session['user_id'])).fetchall()
    
    # Get activity from followed users
    following_activity = db.execute('''
        SELECT a.*, u.username, g.title, g.cover_image_url
        FROM activities a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN games g ON a.game_id = g.id
        WHERE a.user_id IN (
            SELECT following_id FROM follows WHERE follower_id = ?
        )
        ORDER BY a.created_at DESC
        LIMIT 10
    ''', (session['user_id'],)).fetchall()
    
    return render_template('home.html',
                         recent_activity=recent_activity,
                         recommendations=recommendations,
                         following_activity=following_activity)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

# Context processor to make session data available in all templates
@app.context_processor
def inject_user():
    if 'user_id' in session:
        return dict(current_user={'id': session['user_id'], 
                                 'username': session['username'],
                                 'is_admin': session.get('is_admin', False)})
    return dict(current_user=None)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)