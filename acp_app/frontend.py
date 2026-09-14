"""Serves the built React app (frontend/dist) so one Flask server hosts the whole site.

Run `npm run build` in frontend/ first. In development, use the Vite dev
server instead (it proxies /api here).
"""

from pathlib import Path

from flask import Blueprint, abort, current_app, send_from_directory

bp = Blueprint('frontend', __name__)


@bp.route('/', defaults={'path': ''})
@bp.route('/<path:path>')
def serve(path):
    # Unknown API routes stay JSON 404s instead of returning the app's HTML
    if path.startswith('api/'):
        abort(404)

    dist = Path(current_app.config['FRONTEND_DIST'])
    if path and (dist / path).is_file():
        # send_from_directory refuses paths that escape dist
        return send_from_directory(dist, path)

    if not (dist / 'index.html').is_file():
        return 'Frontend not built. Run "npm run build" in frontend/.', 404

    # Anything else is a page inside the React app. no-cache makes browsers
    # pick up a new deploy; the hashed files under assets/ can cache normally.
    response = send_from_directory(dist, 'index.html')
    response.headers['Cache-Control'] = 'no-cache'
    return response
