from flask import Blueprint, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, SubmitField
from wtforms.validators import InputRequired
from acp_app.services.eos_to_english import eos_resolve


class GCCEOSSearchForm(FlaskForm):
    eos_type = IntegerField('EOS Type', validators=[InputRequired()])
    eos_mod1 = IntegerField('EOS Mod 1', default=0)
    eos_mod2 = IntegerField('EOS Mod 2', default=0)
    eos_mod3 = IntegerField('EOS Mod 3', default=0)
    eos_mod4 = IntegerField('EOS Mod 4', default=0)
    eos_mod5 = IntegerField('EOS Mod 5', default=0)
    eos_mod6 = IntegerField('EOS Mod 6', default=0)
    eos_mod7 = IntegerField('EOS Mod 7', default=0)
    eos_mod8 = IntegerField('EOS Mod 8', default=0)
    submit = SubmitField('English, please...')


bp = Blueprint('gcc', __name__)


@bp.route('/gcc_eos/', methods=['GET', 'POST'])
def gcc_eos():

    gcc_eos_form = GCCEOSSearchForm(prefix='gcc')

    if gcc_eos_form.validate_on_submit() and gcc_eos_form.submit.data:
        eos_type = int(gcc_eos_form.eos_type.data)
        eos_mod1 = int(gcc_eos_form.eos_mod1.data)
        eos_mod2 = int(gcc_eos_form.eos_mod2.data)
        eos_mod3 = int(gcc_eos_form.eos_mod3.data)
        eos_mod4 = int(gcc_eos_form.eos_mod4.data)
        eos_mod5 = int(gcc_eos_form.eos_mod5.data)
        eos_mod6 = int(gcc_eos_form.eos_mod6.data)
        eos_mod7 = int(gcc_eos_form.eos_mod7.data)
        eos_mod8 = int(gcc_eos_form.eos_mod8.data)
        session['eos_message'], session['step_not_found'], step_branch = eos_resolve(
            eos_type=eos_type,
            eos_mod_1=eos_mod1,
            eos_mod_2=eos_mod2,
            eos_mod_3=eos_mod3,
            eos_mod_4=eos_mod4,
            eos_mod_5=eos_mod5,
            eos_mod_6=eos_mod6,
            eos_mod_7=eos_mod7,
            eos_mod_8=eos_mod8)
        return redirect(url_for('.gcc_eos'))

    if session.get('step_not_found'):
        flash(
            f'''{session.get('eos_message')} not found, it may be valid, but it's not integrated into this tool.  Karl is the main developer, you can let him know if you want a step added.''',
            'alert-danger')

    return render_template('gcc/gcc_eos.html',
                           form=gcc_eos_form,
                           eos_message=session.get('eos_message'))
