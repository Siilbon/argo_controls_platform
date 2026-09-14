def register_api_blueprints(app):
    from .team import bp as team_bp
    from .aspen import bp as aspen_bp
    from .intellution import bp as intellution_bp
    from .deltav import bp as deltav_bp
    from .gcc import bp as gcc_bp
    from .ttparser import bp as ttparser_bp

    app.register_blueprint(team_bp)
    app.register_blueprint(aspen_bp)
    app.register_blueprint(intellution_bp)
    app.register_blueprint(deltav_bp)
    app.register_blueprint(gcc_bp)
    app.register_blueprint(ttparser_bp)