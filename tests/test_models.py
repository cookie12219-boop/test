"""Model-level tests: relationships and derived properties."""

from app.models import Director, Genre, Movie


def test_director_links_to_movies(app):
    nolan = Director.query.filter_by(name="Christopher Nolan").one()
    titles = sorted(m.title for m in nolan.movies.all())
    assert titles == ["Inception", "Interstellar"]


def test_director_average_rating(app):
    nolan = Director.query.filter_by(name="Christopher Nolan").one()
    # (8.4 + 8.3) / 2 = 8.35
    assert nolan.average_rating == 8.35


def test_movie_genre_many_to_many(app):
    sci_fi = Genre.query.filter_by(name="Science Fiction").one()
    titles = sorted(m.title for m in sci_fi.movies.all())
    assert titles == ["Inception", "Interstellar"]


def test_cast_list_property(app):
    inception = Movie.query.filter_by(title="Inception").one()
    assert inception.cast_list == [
        "Leonardo DiCaprio",
        "Joseph Gordon-Levitt",
    ]


def test_roi_property(app):
    inception = Movie.query.filter_by(title="Inception").one()
    # 825m / 160m = 5.15625 -> round to 5.16
    assert inception.roi == 5.16


def test_profit_property(app):
    interstellar = Movie.query.filter_by(title="Interstellar").one()
    assert interstellar.profit == 701_000_000 - 165_000_000


def test_roi_returns_none_for_zero_budget(app):
    m = Movie(title="Indie", budget=0, revenue=1000)
    assert m.roi is None
