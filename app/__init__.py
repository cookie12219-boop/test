"""Flask application factory.

The application factory pattern keeps the global state to a minimum, lets
tests build isolated app instances with their own config, and makes it
trivial to spin the app up under different configurations (dev, test,
production on Render).
"""

import os
from flask import Flask, render_template

from .extensions import db
from .config import get_config


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(get_config(config_name))

    # Ensure the instance folder exists (needed for SQLite on fresh deploys)
    import os
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "instance"), exist_ok=True)

    db.init_app(app)

    # Register blueprints
    from .routes.main import bp as main_bp
    from .routes.movies import bp as movies_bp
    from .routes.genres import bp as genres_bp
    from .routes.api import bp as api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(movies_bp, url_prefix="/movies")
    app.register_blueprint(genres_bp, url_prefix="/genres")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Register error handlers
    register_error_handlers(app)

    # CLI command for one-shot data loading
    from .cli import register_cli
    register_cli(app)

    # Auto-bootstrap on first request if the DB is empty (handy on Render).
    with app.app_context():
        db.create_all()
        from .models import Movie
        if app.config.get("AUTO_LOAD_DATA", False) and Movie.query.count() == 0:
            from .loader import load_dataset
            csv_path = app.config["DATASET_CSV"]
            if os.path.exists(csv_path):
                app.logger.info("Auto-loading dataset from %s", csv_path)
                load_dataset(csv_path, limit=6500)

    return app


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/400.html", message=str(e)), 400

    @app.errorhandler(500)
    def server_error(_e):
        # Roll back any half-finished session so the next request is clean.
        db.session.rollback()
        return render_template("errors/500.html"), 500
