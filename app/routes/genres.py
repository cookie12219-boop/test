"""Genre browsing routes."""

from flask import Blueprint, abort, current_app, render_template, request
from sqlalchemy import func, desc

from ..extensions import db
from ..models import Genre, Movie

bp = Blueprint("genres", __name__)


@bp.route("/")
def list_genres():
    rows = (
        db.session.query(
            Genre,
            func.count(Movie.id).label("n"),
            func.avg(Movie.vote_average).label("avg_rating"),
        )
        .join(Genre.movies)
        .group_by(Genre.id)
        .order_by(desc("n"))
        .all()
    )
    return render_template("genres/list.html", rows=rows)


@bp.route("/<int:genre_id>")
def show_genre(genre_id):
    genre = db.session.get(Genre, genre_id)
    if genre is None:
        abort(404)

    page = max(request.args.get("page", 1, type=int), 1)
    per_page = current_app.config["ITEMS_PER_PAGE"]

    pagination = (
        genre.movies
        .order_by(desc(Movie.vote_average), desc(Movie.vote_count))
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    total_for_genre = genre.movies.count()
    avg_rating = (
        db.session.query(func.avg(Movie.vote_average))
        .join(Movie.genres)
        .filter(Genre.id == genre.id)
        .scalar()
    )

    return render_template(
        "genres/show.html",
        genre=genre,
        pagination=pagination,
        movies=pagination.items,
        total_for_genre=total_for_genre,
        avg_rating=round(avg_rating or 0, 2),
    )
