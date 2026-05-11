from flask import Blueprint, jsonify, request
from acp_app.services.common import df_to_records
from acp_app.services.intellution import clean_intellution_df
from acp_app import db
from sqlalchemy import select
from acp_app.models import IntellutionTag
import pandas as pd

bp = Blueprint('api_intellution', __name__)

VALID_COLUMNS = {
    'name', 'tag', 'desc', 'ft_topic', 'ioad', 'source', 'opc_topic',
    'ienab', 'opendesc', 'closedesc', 'pri', 'sa1', 'sa2', 'sa3',
    'all_areas', 'almext1', 'almext2', 'prefix', 'loop', 'suffix',
    'alias_root', 'alias_field', 'alias_rest',
}


@bp.route('/api/intellution/<search_term>')
def intellution_search(search_term):
    col = request.args.get('col', 'tag')

    if col not in VALID_COLUMNS:
        return jsonify({'error': f'Invalid column: {col}'}), 400

    column = getattr(IntellutionTag, col)
    query = select(IntellutionTag).where(column.ilike(f'%{search_term}%'))

    df = pd.read_sql(query, db.engine)
    df = clean_intellution_df(df)

    return jsonify({
        'data': df_to_records(df),
        'total': len(df),
        'search_term': search_term,
        'col': col,
    })