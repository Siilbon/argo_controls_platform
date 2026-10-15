import os
basedir = os.path.abspath(os.path.dirname(__file__))


def env_bool(name, default):
    """Read a true/false environment variable ('1', 'true', 'yes' and 'on' count as true)."""
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    """Read a comma-separated environment variable into a list."""
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Built React app that Flask serves (npm run build in frontend/)
    FRONTEND_DIST = os.environ.get('FRONTEND_DIST', os.path.join(basedir, 'frontend', 'dist'))
    # The site is served under this URL prefix on the shared IIS server (see
    # frontend/vite.config.js). Empty = served from the root.
    URL_PREFIX = os.environ.get('URL_PREFIX', '/acp')
    # Only needed when the frontend is served from another origin (the Vite dev server)
    CORS_ORIGINS = env_list('CORS_ORIGINS')

    # Require a signed-in user on every API request. IIS Windows Authentication
    # supplies the user (see web.config); without it the API answers 401.
    REQUIRE_AUTH = env_bool('REQUIRE_AUTH', False)
    # Rotating log file for errors and warnings; unset logs to the console only
    LOG_FILE = os.environ.get('LOG_FILE')

    ASPEN_SERVER = os.environ.get('ASPEN_SERVER')
    # Seconds before an Aspen query gives up
    ASPEN_TIMEOUT = int(os.environ.get('ASPEN_TIMEOUT', 60))
    # Most rows an Aspen definition search returns; the Aspen server stops there
    ASPEN_SEARCH_MAX_ROWS = int(os.environ.get('ASPEN_SEARCH_MAX_ROWS', 5000))
    # Per user (or IP address when there's no user) for Aspen searches and trends
    ASPEN_RATE_LIMIT = os.environ.get('ASPEN_RATE_LIMIT', '30 per minute')
    # Limits are counted in memory, so each server process keeps its own count
    RATELIMIT_STORAGE_URI = 'memory://'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')
    CORS_ORIGINS = env_list('CORS_ORIGINS', 'http://localhost:5173')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Fail closed: a DMZ deploy without Windows Authentication shouldn't serve data
    REQUIRE_AUTH = env_bool('REQUIRE_AUTH', True)


config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
