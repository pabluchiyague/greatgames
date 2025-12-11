from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from modules.auth import admin_required
from db import get_db


admin_bp = Blueprint('admin', __name__)

# =========================
# DASHBOARD
# =========================

@admin_bp.route('/admin')
@admin_required
def dashboard():
    db = get_db()

    # Stats
    stats = {
        'total_users': db.execute('SELECT COUNT(*) AS count FROM users').fetchone()['count'],
        'total_games': db.execute('SELECT COUNT(*) AS count FROM games').fetchone()['count'],
        'total_reviews': db.execute('SELECT COUNT(*) AS count FROM reviews').fetchone()['count'],
    }

    # Recently registered users
    recent_users = db.execute('''
        SELECT id, username, email, is_admin, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT 5
    ''').fetchall()

    # Recently added games
    recent_games = db.execute('''
        SELECT id, title, genre, platform, average_rating
        FROM games
        ORDER BY created_at DESC
        LIMIT 5
    ''').fetchall()

    return render_template(
        'admin.html',
        stats=stats,
        recent_users=recent_users,
        recent_games=recent_games
    )

# =========================
# GAME MANAGEMENT
# =========================

@admin_bp.route('/admin/games')
@admin_required
def manage_games():
    db = get_db()
    q = request.args.get('q', '').strip()

    sql = 'SELECT * FROM games'
    params = []

    if q:
        sql += ' WHERE title LIKE ? OR genre LIKE ? OR platform LIKE ?'
        like = f'%{q}%'
        params.extend([like, like, like])

    sql += ' ORDER BY created_at DESC'

    games = db.execute(sql, params).fetchall()

    return render_template('admin_manage_games.html', games=games, query=q)


@admin_bp.route('/admin/game/add', methods=['GET', 'POST'])
@admin_required
def add_game():
    db = get_db()

    if request.method == 'POST':
        title = (request.form.get('title') or '').strip()
        genre = (request.form.get('genre') or '').strip()
        platform = (request.form.get('platform') or '').strip()
        release_year = request.form.get('release_year') or None
        cover_image_url = (request.form.get('cover_image_url') or '').strip()
        description = (request.form.get('description') or '').strip()

        if not title:
            flash('Title is required.', 'danger')
            return redirect(url_for('admin.add_game'))

        db.execute('''
            INSERT INTO games (title, genre, platform, release_year, cover_image_url, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, genre, platform, release_year, cover_image_url, description))
        db.commit()

        flash('Game added successfully!', 'success')
        return redirect(url_for('admin.manage_games'))

    # Reuse edit template but with game=None or use separate template
    return render_template('admin_add_game.html')


@admin_bp.route('/admin/game/<int:game_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_game(game_id):
    db = get_db()
    game = db.execute('SELECT * FROM games WHERE id = ?', (game_id,)).fetchone()

    if not game:
        flash('Game not found.', 'danger')
        return redirect(url_for('admin.manage_games'))

    if request.method == 'POST':
        title = (request.form.get('title') or '').strip()
        genre = (request.form.get('genre') or '').strip()
        platform = (request.form.get('platform') or '').strip()
        release_year = request.form.get('release_year') or None
        cover_image_url = (request.form.get('cover_image_url') or '').strip()
        description = (request.form.get('description') or '').strip()

        if not title:
            flash('Title is required.', 'danger')
            return redirect(url_for('admin.edit_game', game_id=game_id))

        db.execute('''
            UPDATE games
            SET title = ?, genre = ?, platform = ?, release_year = ?, cover_image_url = ?, description = ?
            WHERE id = ?
        ''', (title, genre, platform, release_year, cover_image_url, description, game_id))
        db.commit()

        flash('Game updated successfully!', 'success')
        return redirect(url_for('admin.manage_games'))

    return render_template('admin_edit_game.html', game=game)


@admin_bp.route('/admin/game/<int:game_id>/delete', methods=['POST'])
@admin_required
def delete_game(game_id):
    db = get_db()

    db.execute('DELETE FROM games WHERE id = ?', (game_id,))
    db.commit()

    flash('Game deleted successfully!', 'success')
    return redirect(url_for('admin.manage_games'))

# =========================
# USER MANAGEMENT
# =========================

@admin_bp.route('/admin/users')
@admin_required
def manage_users():
    db = get_db()
    q = request.args.get('q', '').strip()

    sql = 'SELECT id, username, email, name, is_admin, created_at FROM users'
    params = []

    if q:
        sql += ' WHERE username LIKE ? OR email LIKE ? OR (name IS NOT NULL AND name LIKE ?)'
        like = f'%{q}%'
        params.extend([like, like, like])

    sql += ' ORDER BY created_at DESC'

    users = db.execute(sql, params).fetchall()

    return render_template('admin_manage_users.html', users=users, query=q)


@admin_bp.route('/admin/user/<int:user_id>/toggle_admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    # Do not let an admin change their own admin flag
    if user_id == session.get('user_id'):
        flash('You cannot modify your own admin status.', 'warning')
        return redirect(url_for('admin.manage_users'))

    db = get_db()
    user = db.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,)).fetchone()

    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.manage_users'))

    new_status = 0 if user['is_admin'] else 1
    db.execute('UPDATE users SET is_admin = ? WHERE id = ?', (new_status, user_id))
    db.commit()

    flash('Admin status updated.', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    # Don’t let admins delete their own account from here
    if user_id == session.get('user_id'):
        flash('You cannot delete your own account from the admin panel.', 'warning')
        return redirect(url_for('admin.manage_users'))

    db = get_db()
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()

    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.manage_users'))
