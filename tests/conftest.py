import os
import sys
import sqlite3
import pytest
from werkzeug.security import generate_password_hash
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from app import app  
from config import Config


@pytest.fixture
def test_app(tmp_path):
    """
    Creates a Flask app instance configured for testing
    with a temporary SQLite database.
    """
    # Temporary DB path
    db_path = tmp_path / "test_greatgames.db"

    app.config.update(
        TESTING=True,
        DATABASE=str(db_path),
        SECRET_KEY="test-secret-key",
    )

    # Init DB schema
    conn = sqlite3.connect(app.config['DATABASE'])
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())

    # Seed minimal test data: 1 normal user + 1 admin
    password_hash = generate_password_hash("password123")

    conn.execute(
        "INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)",
        ("user1", "user1@example.com", password_hash, 0),
    )

    conn.execute(
        "INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)",
        ("admin", "admin@example.com", password_hash, 1),
    )

    conn.commit()
    conn.close()

    yield app


@pytest.fixture
def client(test_app):
    """
    Flask test client.
    """
    return test_app.test_client()


@pytest.fixture
def runner(test_app):
    """
    If you later add CLI commands, this is handy.
    """
    return test_app.test_cli_runner()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username="user1", password="password123"):
        return self._client.post(
            "/login",  # adjust if your login route is different
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def login_admin(self, password="password123"):
        return self.login(username="admin", password=password)

    def logout(self):
        return self._client.get("/logout", follow_redirects=True)


@pytest.fixture
def auth(client):
    return AuthActions(client)
