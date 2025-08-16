"""
Copied from:
https://flask.palletsprojects.com/en/stable/tutorial/database/#define-and-access-the-database
To create the database you need to run the following command in a Terminal:
flask --app tutor.flask_para_sqlite init-db
"""
import importlib.resources
import sqlite3
from datetime import datetime

import click
from flask import current_app, g


# Copied from https://flask.palletsprojects.com/en/stable/tutorial/database/
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

        # Enable foreign key support
        g.db.execute('PRAGMA foreign_keys = ON;')

        # Print SQL to the terminal for debugging purposes
        g.db.set_trace_callback(trace_callback)

    return g.db


# Copied from https://flask.palletsprojects.com/en/stable/tutorial/database/
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# Modified copy from https://flask.palletsprojects.com/en/stable/tutorial/
# database/#create-the-tables
# The SQL file has the data as well as the schema
def init_db():
    db = get_db()

    with importlib.resources.path(
        'employment_flask_app.data', 'employment.sql'
    ) as sql_path:
        with current_app.open_resource(str(sql_path)) as f:
            db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Create new tables and add the data."""
    init_db()
    click.echo('Initialized the database.')


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)


# Copied from https://flask.palletsprojects.com/en/stable/tutorial/database/
# #register-with-the-application
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def trace_callback(query):
    """Trace function to log queries."""
    print("Executing query:", query)
