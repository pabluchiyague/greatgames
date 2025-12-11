def test_index_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    # Adjust text depending on your template
    assert b"GreatGames" in resp.data


def test_about_page(client):
    resp = client.get("/about")
    assert resp.status_code == 200
    assert b"About" in resp.data  # or some known text on the page


def test_404(client):
    resp = client.get("/this-does-not-exist")
    assert resp.status_code == 404
