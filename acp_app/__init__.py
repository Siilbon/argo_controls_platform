import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config_dict

db = SQLAlchemy()


def register_commands(app):
    from .commands import init_db, init_team, init_intellution, init_deltav, init_ttparser
    app.cli.add_command(init_db)
    app.cli.add_command(init_team)
    app.cli.add_command(init_intellution)
    app.cli.add_command(init_deltav)
    app.cli.add_command(init_ttparser)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])
    config_dict[config_name].init_app(app)

    # Keep dict keys in insertion order so API rows match DataFrame column order
    app.json.sort_keys = False

    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Register legacy Jinja2 blueprints (kept for CLI commands during transition)
    from .views import aspen_views
    app.register_blueprint(aspen_views.bp)

    from .views import errors
    app.register_blueprint(errors.bp)

    from .views import gcc_views
    app.register_blueprint(gcc_views.bp)

    from .views import home_views
    app.register_blueprint(home_views.bp)

    from .views import intellution_views
    app.register_blueprint(intellution_views.bp)

    from .views import ttparser_views
    app.register_blueprint(ttparser_views.bp)

    # Register REST API blueprints
    from .api import register_api_blueprints
    register_api_blueprints(app)

    register_commands(app)

    return app
