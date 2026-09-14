from acp_app import db
from acp_app.models import TeamMember
from sqlalchemy import select
import pandas as pd


def get_team():
    return db.session.execute(
        select(TeamMember).where(TeamMember.active == True).order_by(TeamMember.id)
    ).scalars().all()


def df_to_records(df):
    """Convert a DataFrame to a JSON-serializable list of dicts (NaN → None)."""
    # jsonify renders datetimes as HTTP dates labelled GMT; send sortable
    # local-time strings instead
    df = df.copy()
    for col in df.select_dtypes(include=['datetime', 'datetimetz']):
        df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    # Cast to object first: typed columns (float, pandas 3 str) turn None
    # back into NaN, which jsonify emits as invalid JSON.
    return df.astype(object).where(pd.notnull(df), None).to_dict(orient='records')
