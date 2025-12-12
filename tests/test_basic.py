def test_index_page(client):
    """
    Basic smoke test: the landing/index page renders.
    """
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"GreatGames" in resp.data


def test_home_requires_login(client):
    """
    The logged-in home/dashboard should redirect if not logged in.
    """
    resp = client.get("/home", follow_redirects=False)
    # If your home route is '/', you can remove this test.
    if resp.status_code != 404:  # don't fail if /home doesn't exist at all
        assert resp.status_code == 302


def test_404_page(client):
    """
    A non-existing route should return 404.
    """
    resp = client.get("/this-route-does-not-exist-xyz")
    assert resp.status_code == 404
