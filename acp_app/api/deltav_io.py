from flask import Blueprint, jsonify, request
from acp_app.services.common import df_to_records
from acp_app.services.deltav import IO_COLS
from acp_app import db
from sqlalchemy import String, cast, select
from acp_app.models import DeltavIoChannel
import pandas as pd

bp = Blueprint('api_deltav_io', __name__)

VALID_COLUMNS = {
    'system', 'status', 'controller', 'card_slot', 'position', 'tag', 'description',
    'io_type', 'card_definition', 'channel_definition', 'controller_assignment',
}


@bp.route('/api/deltav-io/<search_term>')
def deltav_io_search(search_term):
    col = request.args.get('col', 'tag')

    if col not in VALID_COLUMNS:
        return jsonify({'error': f'Invalid column: {col}'}), 400

    # Cast so the number columns (card_slot, position) can be searched as text too
    column = cast(getattr(DeltavIoChannel, col), String)
    query = (select(DeltavIoChannel)
             .where(column.ilike(f'%{search_term}%'))
             .order_by(DeltavIoChannel.system, DeltavIoChannel.controller,
                       DeltavIoChannel.card_slot, DeltavIoChannel.position))

    df = pd.read_sql(query, db.engine)[IO_COLS]

    return jsonify({
        'data': df_to_records(df),
        'total': len(df),
        'search_term': search_term,
        'col': col,
    })
