from flask import Blueprint, current_app, render_template, redirect, url_for, abort
from acp_app.services.aspen import AspenConn
from acp_app.services.common import render_dataframe
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import pandas as pd

bp = Blueprint('aspen', __name__)


class AspenConnectionError(Exception):
    def __init__(self, server, message):
        self.server = server
        self.message = message


class SearchForm(FlaskForm):
    search = StringField(validators=[DataRequired()])
    submit = SubmitField('Search')


@bp.route('/aspen/<search_term>', methods=['GET', 'POST'])
def aspen_search(search_term):
    aspen_server = current_app.config.get('ASPEN_SERVER')
    try:
        aspen_conn = AspenConn(aspen_server, '')

        aspen_io_table = render_dataframe(aspen_conn.iogethistdef(search_term),
                                          bootstrap_table=True)

        aspen_ip_table = render_dataframe(aspen_conn.ip_analog(search_term),
                                          bootstrap_table=True)

        aspen_search = None
        aspen_form = SearchForm(prefix='intel')

        if aspen_form.validate_on_submit() and aspen_form.submit.data:
            aspen_search = aspen_form.search.data
            aspen_form.search.data = ''
            return redirect(
                url_for('aspen.aspen_search', search_term=aspen_search))

        return render_template('aspen/aspen_results.html',
                               aspen_form=aspen_form,
                               aspen_io_table=aspen_io_table,
                               aspen_ip_table=aspen_ip_table)
    except:
        raise AspenConnectionError(server=aspen_server,
                                   message='''Unable to connect to server.''')


@bp.route('/aspen_status')
def aspen_status():
    aspen_server = current_app.config.get('ASPEN_SERVER')
    # try:
    #     aspen_conn = AspenConn(aspen_server, '')

    #     aspen_status_table = render_dataframe(aspen_conn.iostatus(),
    #                                           bootstrap_table=True)
    # except:
    #     raise AspenConnectionError(server=aspen_server,
    #                                message='''Unable to connect to server.''')
    aspen_status_table = pd.DataFrame({
        "name": ["provox", "deltav", "foxboro", "other deltav"],
        "good": [10, 300, 200, 510],
        "bad": [490, 23, 34, 53]
    })

    def highlight_max(s):
        '''
        highlight the maximum in a Series yellow.
        '''
        is_max = s == s.max()
        return ['background-color: yellow' if v else '' for v in is_max]

    # aspen_status_table = aspen_status_table.style.apply(highlight_max).render()

    aspen_status_table = render_dataframe(aspen_status_table,
                                          bootstrap_table=True)

    return render_template('aspen/aspen_status.html',
                           aspen_status_table=aspen_status_table)
