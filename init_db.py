import sqlite3
import os

def init_db():
    # Ensure var directory exists
    os.makedirs('var', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect('var/greatgames.db')
    
    # Read and execute schema
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()