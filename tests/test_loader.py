"""Tests for the CSV loader."""

import csv
import os
import tempfile

from app.loader import load_dataset
from app.models import Director, Genre, Movie


HEADER = [
    "id", "imdb_id", "popularity", "budget", "revenue", "original_title",
    "cast", "homepage", "director", "tagline", "keywords", "overview",
    "runtime", "genres", "production_companies", "release_date",
    "vote_count", "vote_average", "release_year", "budget_adj", "revenue_adj",
]


def _write_csv(rows):
    tf = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
    )
    w = csv.writer(tf)
    w.writerow(HEADER)
    for r in rows:
        w.writerow(r)
    tf.flush()
    tf.close()
    return tf.name


def _row(**overrides):
    base = {
        "id": "1", "imdb_id": "tt0000001", "popularity": "12.3",
        "budget": "1000000", "revenue": "5000000",
        "original_title": "Test Film", "cast": "Actor One|Actor Two",
        "homepage": "", "director": "Some Director",
        "tagline": "", "keywords": "alpha|beta", "overview": "A test movie.",
        "runtime": "100", "genres": "Drama|Romance",
        "production_companies": "Acme", "release_date": "1/1/00",
        "vote_count": "200", "vote_average": "7.5", "release_year": "2000",
        "budget_adj": "1000000", "revenue_adj": "5000000",
    }
    base.update(overrides)
    return [base[k] for k in HEADER]


def test_loader_creates_linked_tables(app):
    """Wipe seed data, load a small CSV, then verify cross-table links."""
    path = _write_csv([
        _row(id="1", original_title="Alpha", director="Dir A",
             genres="Drama|Thriller"),
        _row(id="2", original_title="Beta",  director="Dir A",
             genres="Drama"),
        _row(id="3", original_title="Gamma", director="Dir B",
             genres="Horror"),
    ])
    try:
        summary = load_dataset(path)
    finally:
        os.unlink(path)

    assert summary["movies"] == 3
    assert summary["directors"] == 2
    assert summary["genres"] == 3

    drama = Genre.query.filter_by(name="Drama").one()
    titles = sorted(m.title for m in drama.movies.all())
    assert titles == ["Alpha", "Beta"]

    dir_a = Director.query.filter_by(name="Dir A").one()
    assert dir_a.movie_count == 2


def test_loader_handles_messy_numeric_fields(app):
    path = _write_csv([
        _row(id="1", original_title="Messy",
             budget="not-a-number", revenue="", runtime="",
             vote_average="bad", vote_count="oops"),
    ])
    try:
        load_dataset(path)
    finally:
        os.unlink(path)

    m = Movie.query.filter_by(title="Messy").one()
    assert m.budget == 0
    assert m.revenue == 0
    assert m.runtime == 0
    assert m.vote_average == 0.0
    assert m.vote_count == 0


def test_loader_is_idempotent(app):
    path = _write_csv([_row(id="1", original_title="Once")])
    try:
        load_dataset(path)
        load_dataset(path)  # second run should wipe + reinsert, not duplicate
    finally:
        os.unlink(path)
    assert Movie.query.count() == 1


def test_loader_raises_for_missing_file(app):
    import pytest
    with pytest.raises(FileNotFoundError):
        load_dataset("/no/such/file.csv")
