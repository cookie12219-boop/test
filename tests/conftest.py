"""Pytest fixtures.

Each test gets a fresh Flask app backed by an in-memory SQLite database
seeded with a tiny, deterministic dataset. This keeps the tests fast and
fully isolated.
"""

import os
import sys
import pytest

# Ensure the project root is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models import Director, Genre, Movie  # noqa: E402


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        _seed()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _seed():
    """Insert a handful of deterministic rows for the test suite to work with."""
    nolan = Director(name="Christopher Nolan")
    miyazaki = Director(name="Hayao Miyazaki")
    db.session.add_all([nolan, miyazaki])

    action = Genre(name="Action")
    sci_fi = Genre(name="Science Fiction")
    animation = Genre(name="Animation")
    family = Genre(name="Family")
    db.session.add_all([action, sci_fi, animation, family])
    db.session.flush()

    m1 = Movie(
        title="Inception",
        release_year=2010,
        runtime=148,
        budget=160_000_000,
        revenue=825_000_000,
        vote_average=8.4,
        vote_count=20000,
        popularity=29.1,
        overview="A thief who steals corporate secrets...",
        tagline="Your mind is the scene of the crime.",
        cast_str="Leonardo DiCaprio|Joseph Gordon-Levitt",
    )
    m1.director = nolan
    m1.genres = [action, sci_fi]

    m2 = Movie(
        title="Interstellar",
        release_year=2014,
        runtime=169,
        budget=165_000_000,
        revenue=701_000_000,
        vote_average=8.3,
        vote_count=15000,
        popularity=27.5,
        overview="A team of explorers travel through a wormhole...",
        cast_str="Matthew McConaughey|Anne Hathaway",
    )
    m2.director = nolan
    m2.genres = [sci_fi]

    m3 = Movie(
        title="Spirited Away",
        release_year=2001,
        runtime=125,
        budget=19_000_000,
        revenue=395_000_000,
        vote_average=8.5,
        vote_count=12000,
        popularity=18.0,
        overview="During her family's move to the suburbs...",
        cast_str="Rumi Hiiragi|Miyu Irino",
    )
    m3.director = miyazaki
    m3.genres = [animation, family]

    db.session.add_all([m1, m2, m3])
    db.session.commit()
