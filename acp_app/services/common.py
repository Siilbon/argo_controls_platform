from acp_app.models import Teammate
from acp_app import db
from sqlalchemy import select
import pandas as pd
import re


def get_team():
    return db.session.execute(
        select(Teammate).filter_by(active=True).order_by(Teammate.id)
    ).scalars().all()


def df_to_records(df):
    """Convert a DataFrame to a JSON-serializable list of dicts (NaN → None)."""
    return df.where(pd.notnull(df), None).to_dict(orient='records')


def render_dataframe(df, bootstrap_table=False):
    df = df.to_html(index=False,
                    classes=['table', 'table-hover', 'table-bordered'])

    if bootstrap_table == True:
        # add the neccessary elements for Bootstrap Table
        table_pattern = r'^<table'
        bootstrap_table = '<table data-toggle="table" data-show-columns="true" data-buttons-align="left"'
        th_pattern = r'\<th[>\s]'
        bootstrap_th = '<th data-sortable="true">'

        df = re.sub(table_pattern, bootstrap_table, df)
        df = re.sub(th_pattern, bootstrap_th, df)

    return df
