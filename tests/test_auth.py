def test_friends_requires_login(client):
    """
    /friends should redirect to the login page when not logged in.
    """
    resp = client.get("/friends", follow_redirects=False)

    # redirect
    assert resp.status_code == 302
    # your app redirects to /login (not /auth/login)
    assert "/login" in resp.headers["Location"]


def test_profile_edit_requires_login(client):
    """
    /profile/edit should redirect to the login page when not logged in.
    """
    resp = client.get("/profile/edit", follow_redirects=False)

    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_friends_logged_in(client, auth):
    """
    When logged in, /friends should be accessible and render friend activity
    (or the empty/follow prompt if no friends yet).
    """
    auth.login()  # logs in as a normal user from the fixture

    resp = client.get("/friends")
    assert resp.status_code == 200

    # Depending on data, you'll see either activity or the "no friends" message.
    assert (
        b"Friend Activity" in resp.data
        or b"Follow other users to see their activity here" in resp.data
    )
