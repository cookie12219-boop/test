"""Application configuration.

Three named configs:

- DevelopmentConfig: local development with verbose logging.
- TestingConfig: in-memory SQLite, no auto-loading, used by pytest.
- ProductionConfig: enables auto-loading so a fresh Render deployment
  bootstraps itself the first time a request is served.

Resolution order for `get_config`:
1. Explicit `name` argument.
2. `FLASK_CONFIG` environment variable.
3. Default to development.
"""

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_CSV = os.path.join(BASE_DIR, "data", "tmdb-movies.csv")
DEFAULT_DB = os.path.join(BASE_DIR, "instance", "movies.sqlite")


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{DEFAULT_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATASET_CSV = os.environ.get("DATASET_CSV", DEFAULT_CSV)
    AUTO_LOAD_DATA = False
    ITEMS_PER_PAGE = 30


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    AUTO_LOAD_DATA = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    AUTO_LOAD_DATA = False
    WTF_CSRF_ENABLED = False
    ITEMS_PER_PAGE = 5


class ProductionConfig(BaseConfig):
    DEBUG = False
    AUTO_LOAD_DATA = True


_CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None):
    if name is None:
        name = os.environ.get("FLASK_CONFIG", "development")
    return _CONFIGS.get(name, DevelopmentConfig)
