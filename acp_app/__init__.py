import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from config import config_dict

db = SQLAlchemy()


def _rate_limit_key():
    # Count per signed-in user so people behind one proxy don't share a limit
    from .auth import current_user
    return current_user() or get_remote_address()


# No default limits; routes that hit external systems opt in with @limiter.limit
limiter = Limiter(key_func=_rate_limit_key)


def register_commands(app):
    from .commands import INIT_COMMANDS, init_all
    for command in INIT_COMMANDS:
        app.cli.add_command(command)
    app.cli.add_command(init_all)


def configure_logging(app):
    """Send warnings and errors (including mfgkit's) to LOG_FILE when it's set."""
    log_file = app.config.get('LOG_FILE')
    if not log_file or app.testing:
        return
    os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
    handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=5, encoding='utf-8')
    handler.setLevel(logging.WARNING)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
    for logger in (app.logger, logging.getLogger('mfgkit')):
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)


def add_security_headers(response):
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    # The app is never meant to be framed by another site
    response.headers.setdefault('X-Frame-Options', 'DENY')
    response.headers.setdefault('Referrer-Policy', 'same-origin')
    return response


def create_app(config_name):
    # No Flask static folder: the React build is served by the frontend blueprint
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_dict[config_name])
    config_dict[config_name].init_app(app)

    # Keep dict keys in insertion order so API rows match DataFrame column order
    app.json.sort_keys = False

    if app.config['URL_PREFIX']:
        from .prefix import StripPrefix
        app.wsgi_app = StripPrefix(app.wsgi_app, app.config['URL_PREFIX'])

    configure_logging(app)

    # Initialize extensions
    db.init_app(app)
    limiter.init_app(app)
    if app.config['CORS_ORIGINS']:
        CORS(app, origins=app.config['CORS_ORIGINS'])

    from .auth import require_api_user
    app.before_request(require_api_user)
    app.after_request(add_security_headers)

    # Register REST API blueprints
    from .api import register_api_blueprints
    register_api_blueprints(app)

    # Registered after the API so its catch-all route never shadows an API route
    from .frontend import bp as frontend_bp
    app.register_blueprint(frontend_bp)

    register_commands(app)

    return app
