def test_admin_requires_admin(client, auth):
    # Logged out user → redirect
    resp = client.get("/admin", follow_redirects=False)
    assert resp.status_code == 302

    # Normal user → should also be blocked (redirect or 403)
    auth.login(username="user1", password="password123")
    resp = client.get("/admin", follow_redirects=False)
    assert resp.status_code in (302, 403)


def test_admin_dashboard_ok_for_admin(client, auth):
    auth.login_admin()
    resp = client.get("/admin")
    assert resp.status_code == 200
    assert b"Admin Dashboard" in resp.data  # text from admin.html


def test_admin_manage_games(client, auth):
    auth.login_admin()
    resp = client.get("/admin/games")
    assert resp.status_code == 200
    assert b"Manage Games" in resp.data

def test_admin_add_game(client, auth):
    auth.login_admin()
    resp = client.post(
        "/admin/game/add",
        data={
            "title": "Test Game",
            "genre": "Action",
            "platform": "PC",
            "release_year": 2024,
            "cover_image_url": "",
            "description": "Test game description",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    # Then GET games page and see it listed
    resp2 = client.get("/admin/games")
    assert b"Test Game" in resp2.data
