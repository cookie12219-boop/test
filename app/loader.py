"""Load the TMDB CSV into the database.

Idempotent: running the loader twice with the same CSV gives the same DB.
Uses bulk inserts and a single commit at the end to keep the operation
fast on 5000+ rows.
"""

import csv
import os
from typing import Iterable

from .extensions import db
from .models import Director, Genre, Movie, movie_genres


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _split_pipe(value: str) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split("|") if part.strip()]


def _row_to_kwargs(row: dict) -> dict:
    return {
        "tmdb_id": _safe_int(row.get("id"), 0) or None,
        "imdb_id": (row.get("imdb_id") or "").strip() or None,
        "title": (row.get("original_title") or "").strip() or "Untitled",
        "tagline": (row.get("tagline") or "").strip(),
        "overview": (row.get("overview") or "").strip(),
        "release_year": _safe_int(row.get("release_year"), 0) or None,
        "release_date": (row.get("release_date") or "").strip(),
        "runtime": _safe_int(row.get("runtime"), 0),
        "budget": _safe_int(row.get("budget"), 0),
        "revenue": _safe_int(row.get("revenue"), 0),
        "popularity": _safe_float(row.get("popularity"), 0.0),
        "vote_average": _safe_float(row.get("vote_average"), 0.0),
        "vote_count": _safe_int(row.get("vote_count"), 0),
        "cast_str": (row.get("cast") or "").strip(),
        "keywords_str": (row.get("keywords") or "").strip(),
        "production_companies": (row.get("production_companies") or "").strip(),
    }


def load_dataset(csv_path: str, limit: int | None = None) -> dict:
    """Load (or reload) the TMDB CSV into the database.

    Returns a small summary dict with counts.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset CSV not found: {csv_path}")

    # Wipe existing rows so re-runs are deterministic.
    # The order matters: clear the association table first, then the
    # parent tables, otherwise SQLAlchemy raises IntegrityError when it
    # encounters orphaned association rows.
    db.session.execute(movie_genres.delete())
    Movie.query.delete()
    Genre.query.delete()
    Director.query.delete()
    db.session.commit()

    director_cache: dict[str, Director] = {}
    genre_cache: dict[str, Genre] = {}

    movies_added = 0
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            if limit is not None and idx >= limit:
                break

            director_name = (row.get("director") or "").strip()
            if not director_name:
                director_name = "Unknown"
            # Some rows have multiple directors joined by '|'; keep the first.
            director_name = director_name.split("|")[0].strip() or "Unknown"

            director = director_cache.get(director_name)
            if director is None:
                director = Director(name=director_name)
                db.session.add(director)
                director_cache[director_name] = director

            genres_for_row = []
            for g_name in _split_pipe(row.get("genres") or ""):
                genre = genre_cache.get(g_name)
                if genre is None:
                    genre = Genre(name=g_name)
                    db.session.add(genre)
                    genre_cache[g_name] = genre
                genres_for_row.append(genre)

            movie_kwargs = _row_to_kwargs(row)
            movie = Movie(**movie_kwargs)
            movie.director = director
            movie.genres = genres_for_row
            db.session.add(movie)
            movies_added += 1

            # Periodic flush keeps memory usage bounded on large CSVs.
            if movies_added % 500 == 0:
                db.session.flush()

    db.session.commit()
    return {
        "movies": movies_added,
        "directors": len(director_cache),
        "genres": len(genre_cache),
    }
