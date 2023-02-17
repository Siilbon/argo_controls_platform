import pandas as pd
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField
from acp_app import db
from sqlalchemy import select
from acp_app.models import Truthtables, IntellutionTag
from wtforms.validators import DataRequired
from acp_app.services.common import render_dataframe
from acp_app.services.truthtable_parser import TruthtableDB
from pathlib import Path


class TruthtableParseForm(FlaskForm):

    ttname = StringField('Truthtable Unit Name', validators=[DataRequired()])
    seqnum = IntegerField('Sequence', validators=[DataRequired()])
    submit = SubmitField('Read Truthtable')


bp = Blueprint('ttparser', __name__)


@bp.route('/truthtable_parser/<ttname>/<seqnum>', methods=['GET', 'POST'])
def ttparse(ttname, seqnum):
    # initialize
    tt_table = pd.DataFrame()
    SortError = False

    try:
        tt_query = (select([
            Truthtables
        ]).where(Truthtables.name == f'{ttname.upper()}').where(
            Truthtables.seq == seqnum))

        tt_table = pd.read_sql(tt_query, db.engine)
        tt_table = tt_table.drop('idx', axis=1)
        tt_table = tt_table[[
            'name', 'seq', 'step_num', 'next_step', 'step_name', 'eos_cond',
            'true_dev'
        ]]
        tt_table = tt_table.rename(
            columns={
                'name': 'Truthtable',
                'seq': 'Sequence Number',
                'step_num': 'Step Number',
                'step_name': 'Step Name',
                'eos_cond': 'End of Step Conditions',
                'next_step': 'Next Step',
                'true_dev': 'Open/On'
            })

    except:
        SortError = True

    if tt_table.shape[0] == 0:
        SortError = True

    tt_table = render_dataframe(tt_table, True)
    ttparse_form = TruthtableParseForm(prefix='ttparser')

    if ttparse_form.validate_on_submit() and ttparse_form.submit.data:
        ttname = str(ttparse_form.ttname.data)
        seqnum = int(ttparse_form.seqnum.data)
        return redirect(
            url_for('ttparser.ttparse', ttname=ttname, seqnum=seqnum))

    if SortError:
        flash(
            f'{ttname} - Sequence {seqnum} not found. The truthtable name or sequence may be invaild.',
            'alert-danger')

    return render_template('ttparser/ttparser.html',
                           ttparse_form=ttparse_form,
                           ttname=ttname,
                           seqnum=seqnum,
                           tt_table=tt_table)


@bp.cli.command('init')
def load_truthtable_db():
    all_tts = []
    path = f'acp_app/data/raw/gcc'

    files = Path(path).glob('**/*.xls')
    for file in files:
        truthtable = TruthtableDB(file)
        all_tts.append(truthtable.tt)
    tt_master = pd.concat(all_tts)

    tt_master.to_sql('tt_master',
                     db.engine,
                     if_exists='replace',
                     index=True,
                     index_label='idx')

    print('Successfully loaded truthtables into the database')

    return True
