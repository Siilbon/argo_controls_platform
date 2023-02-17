from flask import current_app
from acp_app import create_app, db
import os
import pytest

@pytest.fixture
def client():
    app = create_app('testing')
    
    with app.test_client() as client:
        with app.app_context():
            pass
        yield client

def test_empty_db(client):
    """Start with a blank database."""
    print('karl client', client)

    rv = client.get('/')
    assert b'No entries here so far' in rv.data