from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from modules.auth import login_required
from app import get_db
import os
from werkzeug.utils import secure_filename

users_bp = Blueprint('users', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@users_bp.route('/profile/<username>')
def profile(username):
    db = get_db()
    
    # Get user
    user = db.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('index'))
    
    # Get users games by status
    wishlist = db.execute('''
        SELECT g.*, ug.added_at 
        FROM games g
        JOIN user_games ug ON g.id = ug.game_id
        WHERE ug.user_id = ? AND ug.status = 'wishlist'
        ORDER BY ug.added_at DESC
    ''', (user['id'],)).fetchall()
    
    currently_playing = db.execute('''
        SELECT g.*, ug.added_at 
        FROM games g
        JOIN user_games ug ON g.id = ug.game_id
        WHERE ug.user_id = ? AND ug.status = 'currently_playing'
        ORDER BY ug.added_at DESC
    ''', (user['id'],)).fetchall()
    
    completed = db.execute('''
        SELECT g.*, ug.added_at 
        FROM games g
        JOIN user_games ug ON g.id = ug.game_id
        WHERE ug.user_id = ? AND ug.status = 'completed'
        ORDER BY ug.added_at DESC
    ''', (user['id'],)).fetchall()
    
    # Get user's reviews
    reviews = db.execute('''
        SELECT r.*, g.title, g.cover_image_url
        FROM reviews r
        JOIN games g ON r.game_id = g.id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
        LIMIT 5
    ''', (user['id'],)).fetchall()
    
    # Statistics
    stats = {
        'total_games': len(wishlist) + len(currently_playing) + len(completed),
        'completed': len(completed),
        'wishlist': len(wishlist),
        'currently_playing': len(currently_playing),
        'reviews': db.execute('SELECT COUNT(*) as count FROM reviews WHERE user_id = ?', 
                            (user['id'],)).fetchone()['count']
    }
    
    # Check if current user follows this profile
    is_following = False
    if 'user_id' in session and session['user_id'] != user['id']:
        follow = db.execute(
            'SELECT 1 FROM follows WHERE follower_id = ? AND following_id = ?',
            (session['user_id'], user['id'])
        ).fetchone()
        is_following = follow is not None
    
    return render_template('profile.html',
                         profile_user=user,
                         wishlist=wishlist,
                         currently_playing=currently_playing,
                         completed=completed,
                         reviews=reviews,
                         stats=stats,
                         is_following=is_following)

@users_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    db = get_db()

    if request.method == 'POST':
        name = request.form.get('name') or None
        bio = request.form.get('bio') or None
        file = request.files.get('profile_picture')

        profile_picture_path = None

        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Invalid image type. Please upload a PNG, JPG, or GIF.', 'danger')
                return redirect(url_for('users.edit_profile'))

            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()

            # Give each user a stable filename
            filename = f"user_{session['user_id']}.{ext}"

            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)

            full_path = os.path.join(upload_folder, filename)
            file.save(full_path)

            # Store path relative to /static so we can use url_for('static', ...)
            profile_picture_path = f"uploads/{filename}"

        if profile_picture_path:
            db.execute(
                'UPDATE users SET name = ?, bio = ?, profile_picture = ? WHERE id = ?',
                (name, bio, profile_picture_path, session['user_id'])
            )
        else:
            db.execute(
                'UPDATE users SET name = ?, bio = ? WHERE id = ?',
                (name, bio, session['user_id'])
            )

        db.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('users.profile', username=session['username']))

    user = db.execute(
        'SELECT * FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()

    return render_template('edit_profile.html', user=user)


@users_bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow_user(username):
    db = get_db()
    
    user_to_follow = db.execute(
        'SELECT id FROM users WHERE username = ?', (username,)
    ).fetchone()
    
    if not user_to_follow:
        flash('User not found.', 'danger')
        return redirect(url_for('index'))
    
    if user_to_follow['id'] == session['user_id']:
        flash('You cannot follow yourself.', 'warning')
        return redirect(url_for('users.profile', username=username))
    
    # Check if already following
    existing = db.execute(
        'SELECT 1 FROM follows WHERE follower_id = ? AND following_id = ?',
        (session['user_id'], user_to_follow['id'])
    ).fetchone()
    
    if existing:
        # Unfollow
        db.execute(
            'DELETE FROM follows WHERE follower_id = ? AND following_id = ?',
            (session['user_id'], user_to_follow['id'])
        )
        flash(f'Unfollowed {username}.', 'info')
    else:
        # Follow
        db.execute(
            'INSERT INTO follows (follower_id, following_id) VALUES (?, ?)',
            (session['user_id'], user_to_follow['id'])
        )
        flash(f'Now following {username}!', 'success')
    
    db.commit()
    return redirect(url_for('users.profile', username=username))

@users_bp.route('/friends')
@login_required
def friends():
    db = get_db()
    
    # Get users you follow
    following = db.execute('''
        SELECT u.*, 
               (SELECT COUNT(*) FROM user_games WHERE user_id = u.id) as game_count
        FROM users u
        JOIN follows f ON u.id = f.following_id
        WHERE f.follower_id = ?
    ''', (session['user_id'],)).fetchall()
    
    # Get your followers
    followers = db.execute('''
        SELECT u.*,
               (SELECT COUNT(*) FROM user_games WHERE user_id = u.id) as game_count
        FROM users u
        JOIN follows f ON u.id = f.follower_id
        WHERE f.following_id = ?
    ''', (session['user_id'],)).fetchall()
    
    # Get recent activity from people you follow
    activity = db.execute('''
        SELECT a.*, u.username, g.title, g.cover_image_url
        FROM activities a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN games g ON a.game_id = g.id
        WHERE a.user_id IN (
            SELECT following_id FROM follows WHERE follower_id = ?
        )
        ORDER BY a.created_at DESC
        LIMIT 20
    ''', (session['user_id'],)).fetchall()


    following_ids = {u['id'] for u in following}

    return render_template(
        'friends.html',
        following=following,
        followers=followers,
        activity=activity,
        following_ids=following_ids,   
    )
@users_bp.route('/friends/discover', methods=['GET'])
@login_required
def discover_friends():
    db = get_db()

    q = request.args.get('q', '').strip()

    # Get IDs of users you already follow (for button)
    following_rows = db.execute(
        'SELECT following_id FROM follows WHERE follower_id = ?',
        (session['user_id'],)
    ).fetchall()
    following_ids = {row['following_id'] for row in following_rows}

    # Build base query: exclude user
    params = [session['user_id']]
    where_clauses = ['u.id != ?']

    if q:
        like = f'%{q}%'
        where_clauses.append('(u.username LIKE ? OR (u.name IS NOT NULL AND u.name LIKE ?))')
        params.extend([like, like])

    sql = f'''
        SELECT u.*,
               (SELECT COUNT(*) FROM user_games WHERE user_id = u.id) AS game_count
        FROM users u
        WHERE {' AND '.join(where_clauses)}
        ORDER BY game_count DESC, u.username ASC
        LIMIT 50
    '''

    users = db.execute(sql, tuple(params)).fetchall()

    return render_template(
        'discover_friends.html',
        users=users,
        query=q,
        following_ids=following_ids
    )
