from flask import Blueprint, jsonify
from acp_app import db
from sqlalchemy import select
from acp_app.models import Truthtables
from acp_app.services.common import df_to_records
import pandas as pd

bp = Blueprint('api_ttparser', __name__)


@bp.route('/api/ttparser/<ttname>/<int:seqnum>')
def ttparse(ttname, seqnum):
    query = (
        select(Truthtables)
        .where(Truthtables.name == ttname.upper())
        .where(Truthtables.seq == seqnum)
    )

    df = pd.read_sql(query, db.engine)

    if df.empty:
        return jsonify({'error': f'{ttname.upper()} sequence {seqnum} not found'}), 404

    df = df.drop('idx', axis=1)
    df = df[['name', 'seq', 'step_num', 'next_step', 'step_name', 'eos_cond', 'true_dev']]

    return jsonify({
        'data': df_to_records(df),
        'ttname': ttname.upper(),
        'seqnum': seqnum,
    })