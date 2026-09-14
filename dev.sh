#!/usr/bin/env bash
# dev.sh — activate the venv, load .env.local, then run any command you pass.
#
# FIRST-TIME SETUP
#   1. Copy the example env file and fill in your values:
#        cp .env.example .env.local
#
#   2. Edit .env.local — at minimum set:
#        SECRET_KEY=<any random string>
#        DEV_DATABASE_URL=<your db connection string>
#        ASPEN_SERVER=<aspen host>
#        CORS_ORIGINS=http://localhost:5173  # React dev server (comma-separated for multiple)
#
# USAGE
#   ./dev.sh flask run               # start the Flask dev server
#   ./dev.sh flask run --debug       # with debug mode / auto-reload
#   ./dev.sh flask init-db           # create database tables
#   ./dev.sh flask init-intellution  # load Intellution tag data
#   ./dev.sh flask init-ttparser     # load Truthtable data
#   ./dev.sh flask init-team         # load team data
#   ./dev.sh python -c "..."         # any other python command

set -e

if [ ! -f .env.local ]; then
    echo "ERROR: .env.local not found."
    echo "Run:  cp .env.example .env.local  then fill in your values."
    exit 1
fi

source .venv/bin/activate

set -a  # auto-export every variable defined in .env.local
source .env.local
set +a

# mfgkit is installed editable, but macOS keeps flagging .venv files hidden and
# Python 3.14 skips hidden .pth files, so put the sibling repo on the path directly.
export PYTHONPATH="$(cd "$(dirname "$0")/../mfgkit" && pwd)${PYTHONPATH:+:$PYTHONPATH}"

if [ $# -eq 0 ]; then
    echo "No command given. Example:  ./dev.sh flask run"
    exit 0
fi

exec "$@"