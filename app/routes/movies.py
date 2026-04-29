"""Movie routes: list, detail, side-by-side compare."""

from flask import Blueprint, abort, current_app, render_template, request
from sqlalchemy import or_, desc, asc

from ..extensions import db
from ..models import Movie, Genre, Director

bp = Blueprint("movies", __name__)


SORT_OPTIONS = {
    "rating": (desc(Movie.vote_average), desc(Movie.vote_count)),
    "popularity": (desc(Movie.popularity),),
    "year_desc": (desc(Movie.release_year),),
    "year_asc": (asc(Movie.release_year),),
    "title": (asc(Movie.title),),
    "revenue": (desc(Movie.revenue),),
}


@bp.route("/")
def list_movies():
    """Paginated, searchable, sortable movie index."""
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = current_app.config["ITEMS_PER_PAGE"]

    q = (request.args.get("q") or "").strip()
    sort = request.args.get("sort", "rating")
    if sort not in SORT_OPTIONS:
        sort = "rating"

    query = Movie.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(Movie.title.ilike(like), Movie.cast_str.ilike(like))
        )

    for order_clause in SORT_OPTIONS[sort]:
        query = query.order_by(order_clause)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "movies/list.html",
        pagination=pagination,
        movies=pagination.items,
        q=q,
        sort=sort,
        sort_options=SORT_OPTIONS,
    )


@bp.route("/<int:movie_id>")
def show_movie(movie_id):
    """Detail page showing the film in context (genre-mates, director-mates)."""
    movie = db.session.get(Movie, movie_id)
    if movie is None:
        abort(404)

    # Context: other movies in the same genres (excluding self).
    genre_ids = [g.id for g in movie.genres]
    related_by_genre = []
    if genre_ids:
        related_by_genre = (
            Movie.query
            .join(Movie.genres)
            .filter(Genre.id.in_(genre_ids))
            .filter(Movie.id != movie.id)
            .order_by(desc(Movie.vote_average))
            .limit(6)
            .all()
        )

    # Context: other movies from the same director.
    related_by_director = []
    if movie.director:
        related_by_director = (
            Movie.query
            .filter(Movie.director_id == movie.director_id)
            .filter(Movie.id != movie.id)
            .order_by(desc(Movie.vote_average))
            .limit(6)
            .all()
        )

    # Context: position in the overall ratings.
    higher_rated = (
        Movie.query
        .filter(Movie.vote_average > movie.vote_average)
        .count()
    )
    total = Movie.query.count()
    percentile = round(100 * (1 - higher_rated / total), 1) if total else 0

    return render_template(
        "movies/show.html",
        movie=movie,
        related_by_genre=related_by_genre,
        related_by_director=related_by_director,
        percentile=percentile,
        higher_rated=higher_rated,
        total=total,
    )


@bp.route("/compare")
def compare():
    """Side-by-side comparison of two movies via ?a=ID&b=ID."""
    a_id = request.args.get("a", type=int)
    b_id = request.args.get("b", type=int)

    movie_a = db.session.get(Movie, a_id) if a_id else None
    movie_b = db.session.get(Movie, b_id) if b_id else None

    # If either lookup failed, drop back to a picker so the user can choose
    # again without seeing a hard 404.
    if (a_id and movie_a is None) or (b_id and movie_b is None):
        abort(404)

    # Surface a small picker of well-rated films if we don't have a full pair.
    suggestions = []
    if not (movie_a and movie_b):
        suggestions = (
            Movie.query
            .filter(Movie.vote_count >= 100)
            .order_by(desc(Movie.vote_average))
            .limit(20)
            .all()
        )

    return render_template(
        "movies/compare.html",
        movie_a=movie_a,
        movie_b=movie_b,
        suggestions=suggestions,
    )
