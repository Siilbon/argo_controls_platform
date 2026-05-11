import click
from flask.cli import with_appcontext
from . import db

@click.command("init-db")
@with_appcontext
def init_db():
    db.create_all()
    click.echo("Database initialized.")