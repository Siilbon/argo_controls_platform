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
    df.to_sql('team', db.engine, if_exists='replace', index=True, index_label='id')
    click.echo(f'Successfully loaded {len(df)} team members.')


@click.command('init-intellution')
@with_appcontext
def init_intellution():
    import pandas as pd
    from datetime import datetime
    from mfgkit.intellution import IntellutionDB
    from .services.intellution import clean_intellution_df
    path = Path('acp_app/data/raw/intellution')
    frames = []
    for name in ['WETMILL', 'DEXTROSE', 'REFINERY', 'UTILITY']:
        file = path / f'{name}.csv'
        df = IntellutionDB(str(file)).df
        df['database'] = name
        # The file's last-modified time stands in for when the export was taken
        df['uploaded'] = datetime.fromtimestamp(file.stat().st_mtime)
        frames.append(df)
    tags = pd.concat(frames, ignore_index=True)
    tags = clean_intellution_df(tags)
    tags.to_sql('intellution_tags', db.engine, if_exists='replace',
                index=True, index_label='index')
    click.echo('Successfully loaded intellution data into the database.')


@click.command('init-deltav')
@with_appcontext
def init_deltav():
    from datetime import datetime
    from mfgkit.deltav.modules import load_modules
    from .services.deltav import clean_deltav_df
    path = Path('acp_app/data/raw/deltav')
    modt = path / 'MODT.TXT'
    modules = load_modules(str(modt), str(path / 'ANT.TXT'), str(path / 'DT.TXT'))
    # MODT's last-modified time stands in for when the export was taken
    modules['uploaded'] = datetime.fromtimestamp(modt.stat().st_mtime)
    modules = clean_deltav_df(modules)
    modules.to_sql('deltav_modules', db.engine, if_exists='replace',
                   index=True, index_label='index')
    click.echo(f'Successfully loaded {len(modules)} DeltaV modules into the database.')


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