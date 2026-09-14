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
    import pandas as pd
    from datetime import datetime
    from mfgkit.deltav.modules import load_modules
    from .services.deltav import clean_deltav_df
    path = Path('acp_app/data/raw/deltav')
    frames = []
    for name in ['Argo01', 'Argo02']:
        folder = path / name
        modt = folder / 'MODT.TXT'
        if not modt.exists():
            click.echo(f'Skipping {name}: {modt} not found.')
            continue
        df = load_modules(str(modt), str(folder / 'ANT.TXT'), str(folder / 'DT.TXT'))
        df['system'] = name
        # MODT's last-modified time stands in for when the export was taken
        df['uploaded'] = datetime.fromtimestamp(modt.stat().st_mtime)
        frames.append(df)
    if not frames:
        raise click.ClickException(f'No DeltaV exports found under {path}.')
    modules = pd.concat(frames, ignore_index=True)
    modules = clean_deltav_df(modules)
    modules.to_sql('deltav_modules', db.engine, if_exists='replace',
                   index=True, index_label='index')
    click.echo(f'Successfully loaded {len(modules)} DeltaV modules into the database.')


@click.command('init-deltav-io')
@with_appcontext
def init_deltav_io():
    import pandas as pd
    from datetime import datetime
    from mfgkit.deltav.io import parse_charms, parse_trad
    from .services.deltav import clean_io_df
    path = Path('acp_app/data/raw/deltav')
    frames = []
    for name in ['Argo01', 'Argo02']:
        files = sorted((path / name).glob('*.fhx'))
        if not files:
            click.echo(f'Skipping {name}: no .fhx files in {path / name}.')
            continue
        for file in files:
            # FHX exports are UTF-16
            fhx_data = file.read_text(encoding='utf-16')
            for parser, io_type in [(parse_trad, 'Classic'), (parse_charms, 'CHARMs')]:
                df = parser(fhx_data)
                df['io_type'] = io_type
                df['system'] = name
                # The file's last-modified time stands in for when the export was taken
                df['uploaded'] = datetime.fromtimestamp(file.stat().st_mtime)
                frames.append(df)
    if not frames:
        raise click.ClickException(f'No DeltaV FHX exports found under {path}.')
    io = pd.concat(frames, ignore_index=True)
    # The same channel can appear in more than one export; keep the newest copy
    io = (io.sort_values('uploaded')
            .drop_duplicates(['system', 'controller', 'card_slot', 'position'], keep='last')
            .sort_values(['system', 'controller', 'card_slot', 'position']))
    io = clean_io_df(io)
    io.to_sql('deltav_io', db.engine, if_exists='replace', index=True, index_label='index')
    counts = ', '.join(f'{n} {s}' for s, n in io['status'].value_counts().items())
    click.echo(f'Successfully loaded {len(io)} DeltaV IO channels into the database ({counts}).')


@click.command('init-ttparser')
@with_appcontext
def init_ttparser():
    import pandas as pd
    from .services.truthtable_parser import TruthtableDB
    path = Path('acp_app/data/raw/gcc')
    files = sorted(path.glob('**/*.xls'))
    if not files:
        raise click.ClickException(f'No truthtable .xls files found under {path}.')
    tt_master = pd.concat([TruthtableDB(f).tt for f in files])
    tt_master.to_sql('tt_master', db.engine, if_exists='replace',
                     index=True, index_label='idx')
    click.echo('Successfully loaded truthtables into the database.')


# Run in this order by init-all; init-db first so every table exists
INIT_COMMANDS = [init_db, init_team, init_intellution, init_deltav, init_deltav_io, init_ttparser]


@click.command('init-all')
@with_appcontext
def init_all():
    """Run every init command. A load that fails (e.g. missing files) doesn't stop the rest."""
    ctx = click.get_current_context()
    failed = []
    for command in INIT_COMMANDS:
        click.secho(f'\n== {command.name}', bold=True)
        try:
            ctx.invoke(command)
        except Exception as err:
            message = err.format_message() if isinstance(err, click.ClickException) else repr(err)
            click.secho(f'{command.name} failed: {message}', fg='red', err=True)
            failed.append(command.name)

    if failed:
        raise click.ClickException(
            f'{len(INIT_COMMANDS) - len(failed)} of {len(INIT_COMMANDS)} loaded; failed: {", ".join(failed)}')
    click.secho(f'\nAll {len(INIT_COMMANDS)} loads finished.', fg='green')