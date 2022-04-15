# Argo Controls Platform

This tool is a Flask app for sharing python utilities using a user friendly web interface.  The directory structure is:

```
├── acp_app/ (All of the source code for the site)
│   ├── data/ (Folder for data)
│   │   ├── raw/ (Raw data CSVs and other files)
│   │   └── data.sqlite (SQLite database)
│   ├── services/ (Folder for python script utilities)
│   ├── static/ (Folder for css, js and other static files)
│   ├── templates/ (Folder for html Jinja Templates)
│   ├── views/ (Folder for Flask view files)
│   ├── __init__.py
│   └── models.py (Contains the database models)
├── migrations/ (Folder for database migration scripts)
├── tests/ (Folder for tests)
├── .gitignore (What files for version control to ignore)
├── app.py (Main script to run the site)
├── config.py (Flask configs)
├── README.md
├── requirements.txt (required python packages)
└── web.config (wfastcgi config for IIS)

```
## Command Line Commands

First activate the virtual environment (.venv) by opening the command prompt and running the following command:

`>cd C:\argo_controls_platform\.venv\Scripts & activate & cd C:\argo_controls_platform\`

To update the intellution database just put the new files under acp_app/data/raw/intellution and run:

`(.venv)$ flask intellution init`

To update the team database change the files under acp_app/data/raw/team and run:

`(.venv)$ flask home init_team`

## Environment Variables
To control the configuration the following environment variables are used:
- `FLASK_APP`:  The main script, app.py in this example
- `SECRET_KEY`:  A hard to guess string
- `ASPEN_SERVER`:  The Aspen Server
- `FLASK_CONFIG`:  What type of configuration to use, the default is production
- `TEST_DATABASE_URL`:  Testing database url
- `DEV_DATABASE_URL`:  Development database url
- `DATABASE_URL`:  Production database url [sqlite:///c:/argo_controls_platform/acp_app/data/data.sqlite]
