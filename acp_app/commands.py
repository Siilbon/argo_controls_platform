import click
from flask.cli import with_appcontext
from pathlib import Path
from . import db


@click.command('init-db')
@with_appcontext
def init_db():
    db.create_all()
    click.echo('Database initialized.')


@click.command('init-team')
@with_appcontext
def init_team():
    import pandas as pd
    df = pd.read_csv('acp_app/data/raw/team/team.csv')
    df.to_sql('team', db.engine, if_exists='replace', index=False)
    click.echo(f'Successfully loaded {len(df)} team members.')


@click.command('init-intellution')
@with_appcontext
def init_intellution():
    import pandas as pd
    from .services.intellution import IntellutionDB
    path = 'acp_app/data/raw/intellution'
    wm  = IntellutionDB(f'{path}/WETMILL.csv')
    dex = IntellutionDB(f'{path}/DEXTROSE.csv')
    ref = IntellutionDB(f'{path}/REFINERY.csv')
    util = IntellutionDB(f'{path}/UTILITY.csv')
    tags = pd.concat([wm.df, dex.df, ref.df, util.df], ignore_index=True)
    tags.to_sql('intellution_tags', db.engine, if_exists='replace',
                index=True, index_label='index')
    click.echo('Successfully loaded intellution data into the database.')


@click.command('init-ttparser')
@with_appcontext
def init_ttparser():
    import pandas as pd
    from .services.truthtable_parser import TruthtableDB
    files = Path('acp_app/data/raw/gcc').glob('**/*.xls')
    tt_master = pd.concat([TruthtableDB(f).tt for f in files])
    tt_master.to_sql('tt_master', db.engine, if_exists='replace',
                     index=True, index_label='idx')
    click.echo('Successfully loaded truthtables into the database.')