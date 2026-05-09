"""Route-level smoke tests."""

from app.models import Movie, Genre


def test_home_loads(client):
    rv = client.get("/")
    assert rv.status_code == 200
    body = rv.get_data(as_text=True)
    assert "Reel" in body
    # Top-rated section should include the highest-rated of our seed movies.
    assert "Spirited Away" in body  # 8.5 is the top of our seed


def test_movie_list_loads(client):
    rv = client.get("/movies/")
    assert rv.status_code == 200
    body = rv.get_data(as_text=True)
    assert "Inception" in body


def test_movie_search_filters_results(client):
    rv = client.get("/movies/?q=Inception")
    body = rv.get_data(as_text=True)
    assert "Inception" in body
    assert "Spirited Away" not in body


def test_movie_search_by_actor(client):
    rv = client.get("/movies/?q=McConaughey")
    body = rv.get_data(as_text=True)
    assert "Interstellar" in body
    assert "Inception" not in body


def test_movie_detail_loads(client, app):
    inception = Movie.query.filter_by(title="Inception").one()
    rv = client.get(f"/movies/{inception.id}")
    assert rv.status_code == 200
    body = rv.get_data(as_text=True)
    assert "Inception" in body
    assert "Christopher Nolan" in body
    # Genre context: should suggest Interstellar (same Sci-Fi genre)
    assert "Interstellar" in body


def test_genre_list(client):
    rv = client.get("/genres/")
    assert rv.status_code == 200
    body = rv.get_data(as_text=True)
    assert "Science Fiction" in body
    assert "Animation" in body


def test_genre_detail(client, app):
    sci_fi = Genre.query.filter_by(name="Science Fiction").one()
    rv = client.get(f"/genres/{sci_fi.id}")
    assert rv.status_code == 200
    body = rv.get_data(as_text=True)
    assert "Inception" in body
    assert "Interstellar" in body


def test_compare_with_two_films(client, app):
    a = Movie.query.filter_by(title="Inception").one()
    b = Movie.query.filter_by(title="Spirited Away").one()
    rv = client.get(f"/movies/compare?a={a.id}&b={b.id}")
    assert rv.status_code == 200
    body = rv.get_data(as_text=True)
    assert "Inception" in body
    assert "Spirited Away" in body
    # Verdict copy should appear
    assert "stars higher" in body or "exactly" in body


def test_compare_picker_when_empty(client):
    rv = client.get("/movies/compare")
    assert rv.status_code == 200
    body = rv.get_data(as_text=True)
    assert "Pick two films" in body


def test_compare_returns_404_for_bad_id(client):
    rv = client.get("/movies/compare?a=99999&b=99998")
    assert rv.status_code == 404


def test_about_page(client):
    rv = client.get("/about")
    assert rv.status_code == 200
    assert b"Flask" in rv.data


def test_healthz(client):
    rv = client.get("/healthz")
    assert rv.status_code == 200
    assert rv.get_json() == {"status": "ok"}
