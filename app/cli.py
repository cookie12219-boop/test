"""Custom Flask CLI commands."""

import click
from flask import current_app
from flask.cli import with_appcontext

from .extensions import db
from .loader import load_dataset


def register_cli(app):
    @app.cli.command("init-db")
    @with_appcontext
    def init_db_cmd():
        """Create tables (idempotent)."""
        db.create_all()
        click.echo("Database tables created.")

    @app.cli.command("load-data")
    @click.option(
        "--csv",
        "csv_path",
        default=None,
        help="Path to the TMDB CSV (defaults to config DATASET_CSV).",
    )
    @click.option("--limit", type=int, default=None, help="Max rows to load.")
    @with_appcontext
    def load_data_cmd(csv_path, limit):
        """Wipe and reload the database from the CSV."""
        csv_path = csv_path or current_app.config["DATASET_CSV"]
        summary = load_dataset(csv_path, limit=limit)
        click.echo(
            f"Loaded {summary['movies']} movies, "
            f"{summary['directors']} directors, "
            f"{summary['genres']} genres."
        )
