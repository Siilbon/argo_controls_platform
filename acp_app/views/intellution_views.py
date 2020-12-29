from flask import Blueprint, render_template, request, redirect, url_for
from acp_app.services.common import render_dataframe
from acp_app.services.intellution import IntellutionDB, clean_intellution_df
from acp_app import db
from sqlalchemy import select
from acp_app.models import IntellutionTag
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange
import pandas as pd

bp = Blueprint('intellution', __name__)


class IntelSearchForm(FlaskForm):
    search = StringField(validators=[DataRequired()])
    submit = SubmitField('Search')

    columns_for_search = [(col, col) for col in [
        'name', 'tag', 'desc', 'ft_topic', 'ioad', 'source', 'opc_topic',
        'ienab', 'opendesc', 'closedesc', 'pri', 'sa1', 'sa2', 'sa3',
        'all_areas', 'almext1', 'almext2', 'prefix', 'loop', 'suffix',
        'alias_root', 'alias_field', 'alias_rest'
    ]]
    column_to_search = SelectField(choices=columns_for_search, default='tag')


@bp.route('/intellution/<search_term>', methods=['GET', 'POST'])
def intellution_search(search_term):
    # Build query for searching for tag
    intel_col = request.args.get('intel_col', 'tag')
    intel_query = select([IntellutionTag]).where(
        (eval(f'IntellutionTag.{intel_col}').ilike(f'%{search_term}%')))

    intellution_table = pd.read_sql(intel_query, db.engine)
    intellution_table = clean_intellution_df(intellution_table)
    intellution_table_len = intellution_table.shape[0]
    intellution_table = render_dataframe(intellution_table, True)

    intel_search = None
    intel_form = IntelSearchForm(prefix='intel')

    if intel_form.validate_on_submit() and intel_form.submit.data:
        intel_search = intel_form.search.data.strip()
        intel_col = intel_form.column_to_search.data
        intel_form.search.data = ''

        return redirect(
            url_for('intellution.intellution_search',
                    search_term=intel_search,
                    intel_col=intel_col))

    return render_template('intellution/intel_results.html',
                           intel_form=intel_form,
                           intellution_table=intellution_table,
                           intel_len=intellution_table_len,
                           intel_search=search_term,
                           intel_col=intel_col)


@bp.cli.command('init')
def load_intellution_db():
    intellution_path = 'acp_app/data/raw/intellution'
    wm_path = f'{intellution_path}/WETMILL.csv'
    ref_path = f'{intellution_path}/REFINERY.csv'
    dex_path = f'{intellution_path}/DEXTROSE.csv'
    util_path = f'{intellution_path}/UTILITY.csv'

    wm = IntellutionDB(wm_path)
    dex = IntellutionDB(dex_path)
    ref = IntellutionDB(ref_path)
    util = IntellutionDB(util_path)

    intellution_tags = pd.concat([wm.df, dex.df, ref.df, util.df],
                                 ignore_index=True)

    intellution_tags.to_sql('intellution_tags',
                            db.engine,
                            if_exists='replace',
                            index=True,
                            index_label='index')

    print('Successfully loaded intellution data into the database')

    return True
