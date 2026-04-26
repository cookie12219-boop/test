"""Top-level pages: home, about, health check."""

from flask import Blueprint, render_template
from sqlalchemy import func, desc

from ..extensions import db
from ..models import Movie, Genre, Director

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    """Landing page with quick stats and a teaser of top-rated films."""
    total_movies = Movie.query.count()
    total_directors = Director.query.count()
    total_genres = Genre.query.count()

    # Top-rated, requiring at least 50 votes to filter out noise.
    top_movies = (
        Movie.query
        .filter(Movie.vote_count >= 50)
        .order_by(desc(Movie.vote_average), desc(Movie.vote_count))
        .limit(8)
        .all()
    )

    # Most popular genres by movie count.
    popular_genres = (
        db.session.query(Genre, func.count(Movie.id).label("n"))
        .join(Genre.movies)
        .group_by(Genre.id)
        .order_by(desc("n"))
        .limit(6)
        .all()
    )

    return render_template(
        "home.html",
        total_movies=total_movies,
        total_directors=total_directors,
        total_genres=total_genres,
        top_movies=top_movies,
        popular_genres=popular_genres,
    )


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/healthz")
def healthz():
    """Tiny endpoint for Render's health checks."""
    return {"status": "ok"}
