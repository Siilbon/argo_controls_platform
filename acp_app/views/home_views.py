from flask import Blueprint, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from acp_app.services.common import get_team
from acp_app.services.intellution import IntellutionDB
from acp_app import db
from acp_app.models import Teammate, Unit
import pandas as pd


class SearchForm(FlaskForm):
    search = StringField(validators=[DataRequired()])
    submit = SubmitField('Search')


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


bp = Blueprint('home', __name__)


@bp.route('/', methods=['GET', 'POST'])
def home():

    team = get_team()

    intel_col = request.args.get('intel_col', 'tag')
    intel_search = None
    intel_form = IntelSearchForm(prefix='intel')

    if intel_form.validate_on_submit() and intel_form.submit.data:
        intel_search = intel_form.search.data
        intel_col = intel_form.column_to_search.data
        intel_form.search.data = ''

        return redirect(
            url_for('intellution.intellution_search',
                    search_term=intel_search,
                    intel_col=intel_col))

    aspen_search = None
    aspen_form = SearchForm(prefix='aspen')

    if aspen_form.validate_on_submit() and aspen_form.submit.data:
        aspen_search = aspen_form.search.data
        aspen_form.search.data = ''
        return redirect(url_for('aspen.aspen_search',
                                search_term=aspen_search))

    print(intel_search, aspen_search)
    return render_template('home/home.html',
                           intel_form=intel_form,
                           intel_search=intel_search,
                           aspen_form=aspen_form,
                           aspen_search=aspen_search,
                           team=team)


@bp.cli.command('init_team')
def init_team():
    controls_team = pd.read_csv(
        filepath_or_buffer='acp_app/data/raw/team/teammates.csv')

    argo_units = pd.read_csv(
        filepath_or_buffer='acp_app/data/raw/team/units.csv')

    controls_team.to_sql('teammates',
                         db.engine,
                         if_exists='replace',
                         index=False)
    argo_units.to_sql('units', db.engine, if_exists='replace', index=False)
    print('Successfully loaded new team configuration!')