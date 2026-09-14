from flask import jsonify, request


def register_api_blueprints(app):
    from .team import bp as team_bp
    from .aspen import bp as aspen_bp
    from .intellution import bp as intellution_bp
    from .deltav import bp as deltav_bp
    from .deltav_io import bp as deltav_io_bp
    from .gcc import bp as gcc_bp
    from .ttparser import bp as ttparser_bp
    from .health import bp as health_bp

    app.register_blueprint(team_bp)
    app.register_blueprint(aspen_bp)
    app.register_blueprint(intellution_bp)
    app.register_blueprint(deltav_bp)
    app.register_blueprint(deltav_io_bp)
    app.register_blueprint(gcc_bp)
    app.register_blueprint(ttparser_bp)
    app.register_blueprint(health_bp)

    register_error_handlers(app)


def register_error_handlers(app):
    """Return API errors as JSON the frontend can show, not Flask's HTML pages."""

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return e

    @app.errorhandler(429)
    def rate_limited(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': f'Too many requests ({e.description}); wait a minute and try again'}), 429
        return e

    @app.errorhandler(500)
    def server_error(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return e
