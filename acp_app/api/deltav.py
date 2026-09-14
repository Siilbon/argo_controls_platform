from flask import Blueprint, jsonify, request
from acp_app.services.common import df_to_records
from acp_app.services.deltav import clean_deltav_df
from acp_app import db
from sqlalchemy import select
from acp_app.models import DeltavModule
import pandas as pd

bp = Blueprint('api_deltav', __name__)

VALID_COLUMNS = {
    'name', 'desc', 'area', 'node_name', 'node_type', 'faceplate', 'detail',
    'default_display',
}


@bp.route('/api/deltav/<search_term>')
def deltav_search(search_term):
    col = request.args.get('col', 'name')

    if col not in VALID_COLUMNS:
        return jsonify({'error': f'Invalid column: {col}'}), 400

    column = getattr(DeltavModule, col)
    query = select(DeltavModule).where(column.ilike(f'%{search_term}%'))

    df = pd.read_sql(query, db.engine)
    df = clean_deltav_df(df)

    return jsonify({
        'data': df_to_records(df),
        'total': len(df),
        'search_term': search_term,
        'col': col,
    })
