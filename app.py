import os
from acp_app import create_app, db
from acp_app.models import TeamMember, IntellutionTag

# 'default' is the production config
app = create_app(os.environ.get('FLASK_CONFIG', 'default'))


@app.shell_context_processor
def make_shell_context():
    return dict(db=db,
                TeamMember=TeamMember,
                IntellutionTag=IntellutionTag)


if __name__ == "__main__":
    app.run()
