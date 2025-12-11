from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from modules.auth import login_required
from db import get_db

games_bp = Blueprint('games', __name__)

@games_bp.route('/game/<int:game_id>')
def game_detail(game_id):
    db = get_db()
    
    # Get game details
    game = db.execute(
        'SELECT * FROM games WHERE id = ?', (game_id,)
    ).fetchone()
    
    if not game:
        flash('Game not found.', 'danger')
        return redirect(url_for('games.browse'))
    
    # Get reviews
    reviews = db.execute('''
        SELECT r.*, u.username, u.name 
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.game_id = ?
        ORDER BY r.created_at DESC
    ''', (game_id,)).fetchall()
    
    # Get tags
    tags = db.execute('''
        SELECT t.name 
        FROM tags t
        JOIN game_tags gt ON t.id = gt.tag_id
        WHERE gt.game_id = ?
    ''', (game_id,)).fetchall()
    
    # Check user's status with this game
    user_game_status = None
    user_review = None
    if 'user_id' in session:
        user_game = db.execute(
            'SELECT status FROM user_games WHERE user_id = ? AND game_id = ?',
            (session['user_id'], game_id)
        ).fetchone()
        user_game_status = user_game['status'] if user_game else None
        
        user_review = db.execute(
            'SELECT * FROM reviews WHERE user_id = ? AND game_id = ?',
            (session['user_id'], game_id)
        ).fetchone()
    
    return render_template('game.html', 
                         game=game, 
                         reviews=reviews, 
                         tags=tags,
                         user_game_status=user_game_status,
                         user_review=user_review)

@games_bp.route('/game/<int:game_id>/add-to-list', methods=['POST'])
@login_required
def add_to_list(game_id):
    status = request.form.get('status')
    
    if status not in ['wishlist', 'currently_playing', 'completed']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('games.game_detail', game_id=game_id))
    
    db = get_db()
    
    # Check if already exists
    existing = db.execute(
        'SELECT id FROM user_games WHERE user_id = ? AND game_id = ?',
        (session['user_id'], game_id)
    ).fetchone()
    
    if existing:
        # Update status
        db.execute(
            'UPDATE user_games SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND game_id = ?',
            (status, session['user_id'], game_id)
        )
    else:
        # Insert new
        db.execute(
            'INSERT INTO user_games (user_id, game_id, status) VALUES (?, ?, ?)',
            (session['user_id'], game_id, status)
        )
    
    db.commit()
    flash(f'Game added to {status.replace("_", " ")}!', 'success')
    return redirect(url_for('games.game_detail', game_id=game_id))

@games_bp.route('/game/<int:game_id>/review', methods=['POST'])
@login_required
def add_review(game_id):
    rating = request.form.get('rating', type=int)
    review_text = request.form.get('review_text', '').strip()
    is_anonymous = request.form.get('is_anonymous') == 'on'
    
    if not rating or rating < 1 or rating > 10:
        flash('Rating must be between 1 and 10.', 'danger')
        return redirect(url_for('games.game_detail', game_id=game_id))
    
    db = get_db()
    
    # Check if review exists
    existing = db.execute(
        'SELECT id FROM reviews WHERE user_id = ? AND game_id = ?',
        (session['user_id'], game_id)
    ).fetchone()
    
    if existing:
        # Update review
        db.execute('''
            UPDATE reviews 
            SET rating = ?, review_text = ?, is_anonymous = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND game_id = ?
        ''', (rating, review_text, is_anonymous, session['user_id'], game_id))
    else:
        # Insert new review
        db.execute('''
            INSERT INTO reviews (user_id, game_id, rating, review_text, is_anonymous)
            VALUES (?, ?, ?, ?, ?)
        ''', (session['user_id'], game_id, rating, review_text, is_anonymous))
    
    # Update average rating
    avg_rating = db.execute(
        'SELECT AVG(rating) as avg FROM reviews WHERE game_id = ?',
        (game_id,)
    ).fetchone()['avg']
    
    db.execute(
        'UPDATE games SET average_rating = ? WHERE id = ?',
        (avg_rating, game_id)
    )
    
    db.commit()
    flash('Review submitted successfully!', 'success')
    return redirect(url_for('games.game_detail', game_id=game_id))

@games_bp.route('/browse')
def browse():
    db = get_db()
    
    # Get search and filter parameters
    query = request.args.get('q', '').strip()
    genre = request.args.get('genre', '').strip()
    platform = request.args.get('platform', '').strip()
    sort_by = request.args.get('sort', 'title')  # title, rating, year
    
    # Build SQL query
    sql = 'SELECT * FROM games WHERE 1=1'
    params = []
    
    if query:
        sql += ' AND title LIKE ?'
        params.append(f'%{query}%')
    
    if genre:
        sql += ' AND genre LIKE ?'
        params.append(f'%{genre}%')
    
    if platform:
        sql += ' AND platform LIKE ?'
        params.append(f'%{platform}%')
    
    # Sorting
    if sort_by == 'rating':
        sql += ' ORDER BY average_rating DESC'
    elif sort_by == 'year':
        sql += ' ORDER BY release_year DESC'
    else:
        sql += ' ORDER BY title ASC'
    
    games = db.execute(sql, params).fetchall()
    
    # Get all unique genres and platforms for filters
    genres = db.execute('SELECT DISTINCT genre FROM games WHERE genre IS NOT NULL').fetchall()
    platforms = db.execute('SELECT DISTINCT platform FROM games WHERE platform IS NOT NULL').fetchall()
    
    return render_template('browse.html', 
                         games=games, 
                         genres=genres, 
                         platforms=platforms,
                         current_query=query,
                         current_genre=genre,
                         current_platform=platform,
                         current_sort=sort_by)