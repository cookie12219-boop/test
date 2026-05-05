"""Minimal JSON endpoints (kept tiny - the project is a Python/Flask
assessment and the brief explicitly forbids JavaScript on pages).
These endpoints just exist so external tooling and tests have a stable
data contract to assert against.
"""

from flask import Blueprint, abort, jsonify

from ..extensions import db
from ..models import Movie, Genre

bp = Blueprint("api", __name__)


@bp.route("/movies/<int:movie_id>")
def movie_json(movie_id):
    movie = db.session.get(Movie, movie_id)
    if movie is None:
        abort(404)
    return jsonify({
        "id": movie.id,
        "title": movie.title,
        "year": movie.release_year,
        "director": movie.director.name if movie.director else None,
        "genres": [g.name for g in movie.genres],
        "vote_average": movie.vote_average,
        "vote_count": movie.vote_count,
        "runtime": movie.runtime,
        "budget": movie.budget,
        "revenue": movie.revenue,
    })


@bp.route("/stats")
def stats_json():
    return jsonify({
        "movies": Movie.query.count(),
        "genres": Genre.query.count(),
    })
