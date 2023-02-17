import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_dict

db = SQLAlchemy()


def create_app(config_name):
    # Initialize app with configuration
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])
    config_dict[config_name].init_app(app)
    print(config_dict[config_name])

    # Initialize extentions
    db.init_app(app)

    # Register blueprints
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

    return app
