import os
from acp_app import create_app, db
from acp_app.models import Teammate, Unit, IntellutionTag
from flask_migrate import Migrate

app = create_app(os.environ.get('FLASK_CONFIG'))
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run()


@app.shell_context_processor
def make_shell_context():
    return dict(db=db,
                Teammate=Teammate,
                Unit=Unit,
                IntellutionTag=IntellutionTag)
