import sqlite3
import os

def seed_database():
    """Add sample data to the database for testing"""
    
    # Ensure database exists
    if not os.path.exists('var/greatgames.db'):
        print("Database not found. Run init_db.py first!")
        return
    
    conn = sqlite3.connect('var/greatgames.db')
    cursor = conn.cursor()
    
    # Sample games
    sample_games = [
        ('The Legend of Zelda: Breath of the Wild', 'Nintendo EPD', 'Nintendo', 2017, 'Nintendo Switch', 'Action-Adventure', 
         'An open-world action-adventure game that reimagines the Zelda series with a vast, explorable world.', 
         '/static/uploads/zelda_botw_cover.jpg', 9.5),

        ('The Witcher 3: Wild Hunt', 'CD Projekt Red', 'CD Projekt', 2015, 'PC', 'RPG',
         'An epic open-world RPG following Geralt of Rivia as he searches for his adopted daughter.',
         '/static/uploads/witcher3_cover.jpg', 9.3),

        ('Red Dead Redemption 2', 'Rockstar Games', 'Rockstar Games', 2018, 'PlayStation 4', 'Action-Adventure',
         'An epic tale of life in America at the dawn of the modern age, following outlaw Arthur Morgan.',
         '/static/uploads/rdr2_cover.jpg', 9.7),

        ('Hades', 'Supergiant Games', 'Supergiant Games', 2020, 'PC', 'Roguelike',
         'A rogue-like dungeon crawler where you defy the god of the dead as you hack and slash your way out of the Underworld.',
         '/static/uploads/hades_cover.jpg', 9.2),

        ('Celeste', 'Maddy Makes Games', 'Maddy Makes Games', 2018, 'PC', 'Platformer',
         'A challenging platformer about climbing a mountain, while surviving its many perils.',
         '/static/uploads/Celeste_cover.jpg', 9.0),

        ('Minecraft', 'Mojang Studios', 'Mojang Studios', 2011, 'PC', 'Sandbox',
         'A sandbox game where players can build, explore, and survive in a blocky, procedurally generated 3D world.',
         '/static/uploads/minecraft_cover.jpg', 8.8),

        ('Portal 2', 'Valve', 'Valve', 2011, 'PC', 'Puzzle',
         'A first-person puzzle-platform game that challenges players with physics-based puzzles using portal mechanics.',
         '/static/uploads/portal2_cover.jpg', 9.5),

        ('Stardew Valley', 'ConcernedApe', 'ConcernedApe', 2016, 'PC', 'Simulation',
         "A farming simulation RPG where you inherit your grandfather's old farm plot in Stardew Valley.",
         '/static/uploads/stardew_valley_cover.jpg', 9.1),

        ('Hollow Knight', 'Team Cherry', 'Team Cherry', 2017, 'PC', 'Metroidvania',
         'A challenging 2D action-adventure through a vast, interconnected underground kingdom.',
         '/static/uploads/hollow_knight_cover.jpg', 9.3),

        ('God of War', 'Santa Monica Studio', 'Sony Interactive Entertainment', 2018, 'PlayStation 4', 'Action-Adventure',
         'Kratos embarks on a dangerous journey with his son through Norse mythology.',
         '/static/uploads/god_of_war_cover.jpg', 9.4),
    ]

    
    print("Adding sample games...")
    for game in sample_games:
        try:
            cursor.execute('''
                INSERT INTO games (title, developer, publisher, release_year, platform, genre, description, cover_image_url, average_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', game)
        except sqlite3.IntegrityError:
            print(f"Game '{game[0]}' already exists, skipping...")
    
    # Sample tags
    sample_tags = ['Action', 'Adventure', 'RPG', 'Indie', 'Multiplayer', 'Singleplayer', 
                   'Story-Rich', 'Open World', 'Puzzle', 'Platformer']
    
    print("Adding sample tags...")
    for tag in sample_tags:
        try:
            cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag,))
        except sqlite3.IntegrityError:
            print(f"Tag '{tag}' already exists, skipping...")
    
    # Create admin user (password: admin123)
    from werkzeug.security import generate_password_hash
    
    print("Creating admin user...")
    admin_password = generate_password_hash('admin123')
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, name, is_admin, bio)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@greatgames.com', admin_password, 'Administrator', 1, 
              'GreatGames administrator account.'))
    except sqlite3.IntegrityError:
        print("Admin user already exists, skipping...")
    
    # Create test user (password: test123)
    print("Creating test user...")
    test_password = generate_password_hash('test123')
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, name, bio)
            VALUES (?, ?, ?, ?, ?)
        ''', ('testuser', 'test@example.com', test_password, 'Test User',
              'Just a gamer who loves playing and reviewing games!'))
    except sqlite3.IntegrityError:
        print("Test user already exists, skipping...")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database seeded successfully!")
    print("\nYou can now login with:")
    print("  Admin: username='admin', password='admin123'")
    print("  Test User: username='testuser', password='test123'")

if __name__ == '__main__':
    seed_database()