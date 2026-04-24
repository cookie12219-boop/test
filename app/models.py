"""Database models.

Schema (linked tables):

    Director (1) ────< (N) Movie (N) >──── (N) Genre
                                 │
                                 └── via `movie_genres` association table

The association is a proper many-to-many table, not a comma-separated
string, so genre queries can use SQL joins.
"""

from .extensions import db


# Association table for the Movie <-> Genre many-to-many relationship.
movie_genres = db.Table(
    "movie_genres",
    db.Column("movie_id", db.Integer, db.ForeignKey("movies.id"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("genres.id"), primary_key=True),
)


class Director(db.Model):
    __tablename__ = "directors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)

    movies = db.relationship(
        "Movie", back_populates="director", lazy="dynamic"
    )

    @property
    def movie_count(self) -> int:
        return self.movies.count()

    @property
    def average_rating(self) -> float:
        rows = self.movies.with_entities(Movie.vote_average).all()
        ratings = [r[0] for r in rows if r[0] is not None]
        return round(sum(ratings) / len(ratings), 2) if ratings else 0.0

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"<Director {self.name}>"


class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False, index=True)

    movies = db.relationship(
        "Movie",
        secondary=movie_genres,
        back_populates="genres",
        lazy="dynamic",
    )

    @property
    def movie_count(self) -> int:
        return self.movies.count()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Genre {self.name}>"


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, index=True)
    imdb_id = db.Column(db.String(20), index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    tagline = db.Column(db.String(500))
    overview = db.Column(db.Text)
    release_year = db.Column(db.Integer, index=True)
    release_date = db.Column(db.String(20))
    runtime = db.Column(db.Integer)
    budget = db.Column(db.BigInteger, default=0)
    revenue = db.Column(db.BigInteger, default=0)
    popularity = db.Column(db.Float, default=0.0)
    vote_average = db.Column(db.Float, default=0.0, index=True)
    vote_count = db.Column(db.Integer, default=0)
    cast_str = db.Column(db.Text)
    keywords_str = db.Column(db.Text)
    production_companies = db.Column(db.Text)

    director_id = db.Column(db.Integer, db.ForeignKey("directors.id"), index=True)
    director = db.relationship("Director", back_populates="movies")

    genres = db.relationship(
        "Genre",
        secondary=movie_genres,
        back_populates="movies",
        lazy="select",
    )

    # ----- Derived helpers -----

    @property
    def cast_list(self) -> list[str]:
        return [c.strip() for c in (self.cast_str or "").split("|") if c.strip()]

    @property
    def keyword_list(self) -> list[str]:
        return [k.strip() for k in (self.keywords_str or "").split("|") if k.strip()]

    @property
    def companies_list(self) -> list[str]:
        return [
            c.strip() for c in (self.production_companies or "").split("|") if c.strip()
        ]

    @property
    def profit(self) -> int:
        if self.budget and self.revenue:
            return int(self.revenue) - int(self.budget)
        return 0

    @property
    def roi(self) -> float | None:
        """Return-on-investment as a multiple of budget, or None."""
        if self.budget and self.budget > 0:
            return round(self.revenue / self.budget, 2)
        return None

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Movie {self.title} ({self.release_year})>"
