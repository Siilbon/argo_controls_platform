from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import func, inspect, select, text
from mfgkit.aspen import AspenConn

from acp_app import db
from acp_app.auth import current_user
from acp_app.models import DeltavIoChannel, DeltavModule, IntellutionTag, TeamMember, Truthtables

bp = Blueprint('api_health', __name__)

# Loaded datasets, keyed by the ids the frontend uses. Tables without an
# `uploaded` column only report a row count.
DATASETS = {
    'intellution': IntellutionTag,
    'deltav': DeltavModule,
    'deltav_io': DeltavIoChannel,
    'truthtables': Truthtables,
    'team': TeamMember,
}


def dataset_status():
    """Row count and last load time for each dataset; loaded is False for a missing table."""
    tables = set(inspect(db.engine).get_table_names())
    status = {}
    for key, model in DATASETS.items():
        if model.__tablename__ not in tables:
            status[key] = {'loaded': False, 'rows': 0, 'uploaded': None}
            continue
        columns = [func.count()]
        if hasattr(model, 'uploaded'):
            columns.append(func.max(model.uploaded))
        row = db.session.execute(select(*columns).select_from(model)).one()
        uploaded = row[1] if len(row) > 1 else None
        if hasattr(uploaded, 'strftime'):
            uploaded = uploaded.strftime('%Y-%m-%d %H:%M:%S')
        status[key] = {'loaded': row[0] > 0, 'rows': row[0], 'uploaded': uploaded}
    return status


@bp.route('/api/me')
def me():
    return jsonify({'user': current_user(), 'auth_required': current_app.config['REQUIRE_AUTH']})


@bp.route('/api/datasets')
def datasets():
    return jsonify(dataset_status())


@bp.route('/api/health')
def health():
    """Database and data status; add ?aspen=1 to also test the Aspen connection.

    Answers 503 when the database (or Aspen, if checked) is unreachable, so a
    monitor can alert on the status code alone.
    """
    body = {'status': 'ok'}
    code = 200

    try:
        db.session.execute(text('SELECT 1'))
        body['database'] = 'ok'
        body['datasets'] = dataset_status()
    except Exception:
        current_app.logger.exception('Health check: database unreachable')
        body['database'] = 'error'
        body['status'], code = 'error', 503

    if request.args.get('aspen'):
        server = current_app.config.get('ASPEN_SERVER')
        try:
            with AspenConn(server, timeout=10) as conn:
                alive = conn.is_alive
        except Exception:
            current_app.logger.exception('Health check: Aspen unreachable')
            alive = False
        body['aspen'] = 'ok' if alive else 'error'
        if not alive:
            body['aspen_error'] = f'Unable to connect to Aspen server: {server}'
            body['status'], code = 'error', 503

    return jsonify(body), code
