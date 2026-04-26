"""Flask extensions instantiated here so they can be imported anywhere
without causing circular imports through the application factory.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
