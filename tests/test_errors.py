"""Error-handling tests."""


def test_404_for_unknown_movie(client):
    rv = client.get("/movies/99999")
    assert rv.status_code == 404
    body = rv.get_data(as_text=True)
    assert "404" in body
    # The error page should still render the masthead, proving template
    # inheritance survives the error path.
    assert "Reel" in body


def test_404_for_unknown_genre(client):
    rv = client.get("/genres/99999")
    assert rv.status_code == 404


def test_404_for_unknown_route(client):
    rv = client.get("/this/does/not/exist")
    assert rv.status_code == 404


def test_api_404_for_unknown_movie(client):
    rv = client.get("/api/movies/99999")
    assert rv.status_code == 404


def test_invalid_sort_falls_back_to_default(client):
    # Bad sort shouldn't 500; it should just behave as 'rating'.
    rv = client.get("/movies/?sort=notreal")
    assert rv.status_code == 200
