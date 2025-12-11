def test_friends_requires_login(client):
    resp = client.get("/friends", follow_redirects=False)
    # should redirect to login
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]


def test_profile_edit_requires_login(client):
    resp = client.get("/profile/edit", follow_redirects=False)
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]


def test_friends_logged_in(client, auth):
    auth.login()
    resp = client.get("/friends")
    assert resp.status_code == 200
    assert b"Friend Activity" in resp.data  # or some text from friends.html
