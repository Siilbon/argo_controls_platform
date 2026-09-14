"""Who is making the request.

In production IIS does the sign-in (Windows Authentication) and hands Flask the
account name, so there are no passwords here. See web.config and the README's
Deploying section.
"""

from flask import current_app, jsonify, request

# Server variables IIS may use for the signed-in account, e.g. "INGREDION\\ksiil"
_USER_VARIABLES = ('REMOTE_USER', 'AUTH_USER', 'LOGON_USER')


def current_user():
    """The signed-in account name, or None when there isn't one."""
    for name in _USER_VARIABLES:
        user = request.environ.get(name)
        if user:
            return user
    return None


def require_api_user():
    """before_request hook: refuse API calls without a user when REQUIRE_AUTH is on."""
    if not request.path.startswith('/api/'):
        return None  # the page shell holds no data; IIS still guards it
    if current_app.config['REQUIRE_AUTH'] and not current_user():
        return jsonify({'error': 'Sign-in required'}), 401
    return None
