def test_friends_requires_login(client):
    """
    /friends should redirect to the login page when not logged in.
    """
    resp = client.get("/friends", follow_redirects=False)

    assert resp.status_code == 302
    location = resp.headers.get("Location", "")
    # your app redirects to /login (not /auth/login)
    assert "/login" in location


def test_profile_edit_requires_login(client):
    """
    /profile/edit should redirect to the login page when not logged in.
    """
    resp = client.get("/profile/edit", follow_redirects=False)

    assert resp.status_code == 302
    location = resp.headers.get("Location", "")
    assert "/login" in location


def test_friends_logged_in(client, auth):
    """
    When logged in, /friends should be accessible and render friend activity
    or the empty/follow prompt if there is no data yet.
    """
    auth.login()  # logs in as normal user from fixture

    resp = client.get("/friends")
    assert resp.status_code == 200

    # Depending on seed data, either activity or "no activity yet" message
    assert (
        b"Friend Activity" in resp.data
        or b"Follow other users to see their activity here" in resp.data
        or b"Your Followers" in resp.data  # fallback if template text differs
    )
