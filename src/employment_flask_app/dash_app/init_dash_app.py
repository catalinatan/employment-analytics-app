from dash import Dash
import dash_bootstrap_components as dbc
from employment_flask_app.dash_app.layout import app_layout
from employment_flask_app.dash_app.callbacks import register_callbacks
from flask import g
import os

assets_path = os.path.join(os.getcwd(),"src","employment_flask_app","dash_app","assets")

def init_app(url_path, server=None):
    # Define meta tags for the viewport
    meta_tags = [
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ]

    # Define external stylesheets, using Bootstrap styling from
    # dash_bootstrap_components (dbc)
    external_stylesheets = [
        dbc.themes.BOOTSTRAP,
        dbc.icons.BOOTSTRAP,
        'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css'
    ]

    # Define external scripts, including html2canvas for capturing screenshots
    external_scripts = [
        {
            'src': (
                'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.0/'
                'html2canvas.min.js'
            )
        }
    ]

    # Create and configure the Dash app
    app = Dash(
        server=g.cur_app, 
        url_base_pathname=url_path,
        external_stylesheets=external_stylesheets,
        external_scripts=external_scripts,
        meta_tags=meta_tags, 
        assets_folder=assets_path
    )

    # Set the layout of the app
    app.layout = app_layout

    # Register all callbacks
    register_callbacks(app)

    return app.server