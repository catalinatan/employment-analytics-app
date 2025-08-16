import os

from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from employment_flask_app.dash_app import init_dash_app


# Define a base class for the SQLAlchemy ORM models
class Base(DeclarativeBase):
    pass


# Initialize the SQLAlchemy object with the custom base class
db = SQLAlchemy(model_class=Base)


# Function to create and configure the Flask application
def create_app(test_config=None):
    # Create the Flask app instance
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder='./templates'
    )

    # Set default configuration for the app
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=(
            # SQLite database URI
            "sqlite:///" + os.path.join(app.instance_path, "flaskr.sqlite")
        )
    )

    # Initialize the app with the SQLAlchemy extension
    db.init_app(app)

    if test_config is None:
        # Load the instance configuration if it exists and not in testing mode
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test configuration if provided
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Import and register the routes blueprint
    from . import routes
    app.register_blueprint(routes.bp)

    # Create database tables and initialize the Dash app within the
    # Flask app context
    with app.app_context():
        db.create_all()  # Create all database tables
        g.cur_app = app  # Store the current app in the global context
        # Initialize the Dash app with a specific URL path
        app = init_dash_app.init_app('/dashboard/')

    return app  # Return the configured Flask app instance
