def test_login_success(client, auth):
    resp = auth.login(username="user1", password="password123")
    assert resp.status_code == 200
    # Should see welcome message or username somewhere
    assert b"user1" in resp.data


def test_login_invalid_password(client, auth):
    resp = auth.login(username="user1", password="wrongpassword")
    assert b"Invalid" in resp.data or b"incorrect" in resp.data


def test_logout(client, auth):
    # First log in
    auth.login()
    # Then log out
    resp = auth.logout()
    # Login link should be visible again, etc.
    assert b"Login" in resp.data
