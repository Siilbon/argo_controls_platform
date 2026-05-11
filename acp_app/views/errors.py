from flask import Blueprint, render_template, jsonify, request
from acp_app.views.aspen_views import AspenConnectionError

bp = Blueprint('errors', __name__, template_folder='templates')


@bp.app_errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('errors/404_acp.html'), 404


@bp.app_errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('errors/500_acp.html'), 500


@bp.app_errorhandler(AspenConnectionError)
def aspen_not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': e.message, 'server': e.server}), 503
    return render_template('errors/aspen_acp.html',
                           server=e.server,
                           message=e.message), 500
