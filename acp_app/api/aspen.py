from flask import Blueprint, jsonify, current_app
from acp_app.services.aspen import AspenConn
from acp_app.services.common import df_to_records

bp = Blueprint('api_aspen', __name__)


@bp.route('/api/aspen/search/<search_term>')
def aspen_search(search_term):
    aspen_server = current_app.config.get('ASPEN_SERVER')
    try:
        conn = AspenConn(aspen_server, '')
        return jsonify({
            'io_data': df_to_records(conn.iogetdef(search_term)),
            'ip_data': df_to_records(conn.ip_analog(search_term)),
        })
    except Exception:
        return jsonify({'error': f'Unable to connect to Aspen server: {aspen_server}'}), 503


@bp.route('/api/aspen/status')
def aspen_status():
    aspen_server = current_app.config.get('ASPEN_SERVER')
    try:
        conn = AspenConn(aspen_server, '')
        return jsonify({'status': df_to_records(conn.iostatus())})
    except Exception:
        return jsonify({'error': f'Unable to connect to Aspen server: {aspen_server}'}), 503