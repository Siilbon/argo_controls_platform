"""API and app-serving tests that don't need Aspen or plant data files."""

from datetime import datetime

import pandas as pd
import pytest

from acp_app import create_app
from acp_app.services.aspen import (parse_trend_tags, trend_period_seconds, trend_to_json,
                                    trend_window)
from acp_app.services.deltav import io_status


@pytest.fixture
def app(tmp_path):
    app = create_app('testing')
    dist = tmp_path / 'dist'
    (dist / 'assets').mkdir(parents=True)
    (dist / 'index.html').write_text('<div id="root"></div>')
    (dist / 'assets' / 'app.js').write_text('console.log(1)')
    app.config['FRONTEND_DIST'] = str(dist)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# --------------------------------------------------------------------------- #
# Serving the React build
# --------------------------------------------------------------------------- #

def test_root_serves_react_index(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b'id="root"' in res.data
    assert res.headers['Cache-Control'] == 'no-cache'


def test_built_assets_are_served(client):
    res = client.get('/assets/app.js')
    assert res.status_code == 200
    assert b'console.log' in res.data


def test_other_paths_fall_back_to_index(client):
    assert b'id="root"' in client.get('/some/page').data


@pytest.mark.parametrize('path', ['/../config.py', '/%2e%2e/config.py', '/assets/../../config.py'])
def test_files_outside_the_build_are_not_served(client, path):
    res = client.get(path)
    assert b'FRONTEND_DIST' not in res.data


def test_unknown_api_route_is_json_404(client):
    res = client.get('/api/nope')
    assert res.status_code == 404
    assert res.get_json() == {'error': 'Not found'}


def test_missing_build_explains_itself(app, tmp_path):
    app.config['FRONTEND_DIST'] = str(tmp_path / 'missing')
    res = app.test_client().get('/')
    assert res.status_code == 404
    assert b'npm run build' in res.data


# --------------------------------------------------------------------------- #
# GCC EOS
# --------------------------------------------------------------------------- #

def test_gcc_eos_translates(client):
    res = client.post('/api/gcc/eos', json={'eos_type': 1, 'eos_mod1': 145, 'eos_mod2': 1})
    body = res.get_json()
    assert res.status_code == 200
    assert body['step_not_found'] is False
    assert 'Real_Inputs[145].1' in body['message']


def test_gcc_eos_unknown_type(client):
    body = client.post('/api/gcc/eos', json={'eos_type': 99}).get_json()
    assert body['step_not_found'] is True


def test_gcc_eos_rejects_non_integers(client):
    res = client.post('/api/gcc/eos', json={'eos_type': '__import__("os")'})
    assert res.status_code == 400


# --------------------------------------------------------------------------- #
# Aspen trend helpers
# --------------------------------------------------------------------------- #

def test_trend_window_from_hours():
    now = datetime(2026, 9, 14, 12, 0)
    assert trend_window(hours='8', now=now) == (datetime(2026, 9, 14, 4, 0), now)


@pytest.mark.parametrize('kwargs', [
    {},
    {'start': '2026-09-14T10:00', 'end': '2026-09-14T09:00'},
    {'start': '2025-01-01', 'end': '2026-09-14'},
])
def test_trend_window_rejects_bad_ranges(kwargs):
    with pytest.raises(ValueError):
        trend_window(**kwargs)


def test_trend_period_targets_about_1000_points():
    start = datetime(2026, 9, 14)
    assert trend_period_seconds(start, datetime(2026, 9, 15)) == 87
    assert trend_period_seconds(start, datetime(2026, 9, 14, 0, 1)) == 1


def test_parse_trend_tags_splits_and_dedupes():
    assert parse_trend_tags(['FT1, TT2', 'FT1', 'PT3']) == ['FT1', 'TT2', 'PT3']
    with pytest.raises(ValueError):
        parse_trend_tags([' , '])


def test_trend_to_json_keeps_numbers_text_and_missing():
    wide = pd.DataFrame(
        {'FT1': [1.5, None], 'PMP': ['RUNNING', 'STOPPED']},
        index=pd.to_datetime(['2026-09-14 08:00', '2026-09-14 08:10']),
    )
    out = trend_to_json(wide, ['FT1', 'PMP', 'NOPE'])
    assert out['ts'] == ['2026-09-14T08:00:00', '2026-09-14T08:10:00']
    assert out['series'] == [
        {'tag': 'FT1', 'values': [1.5, None]},
        {'tag': 'PMP', 'values': ['RUNNING', 'STOPPED']},
    ]
    assert out['missing'] == ['NOPE']


# --------------------------------------------------------------------------- #
# DeltaV IO status
# --------------------------------------------------------------------------- #

def test_io_status_labels():
    df = pd.DataFrame([
        {'tag': 'FT21001', 'enabled': True, 'card_definition': 'AI_16CH_HART_4-20'},
        {'tag': 'WMCP04C12CH07', 'enabled': False, 'card_definition': 'DI_32CH_HD'},
        {'tag': '', 'enabled': False, 'card_definition': 'CHMIO_UNDEFINED_CHARM'},
        {'tag': 'OLD-TAG', 'enabled': False, 'card_definition': 'DO_32CH_HD'},
        {'tag': '', 'enabled': True, 'card_definition': 'WIRELESS_CLOUD'},
    ])
    assert io_status(df).tolist() == ['Assigned', 'Spare', 'Spare', 'Disabled', 'No DST']


# --------------------------------------------------------------------------- #
# Sign-in, headers, health
# --------------------------------------------------------------------------- #

def test_api_requires_a_user_when_auth_is_on(app, client):
    app.config['REQUIRE_AUTH'] = True
    res = client.get('/api/me')
    assert res.status_code == 401
    assert res.get_json() == {'error': 'Sign-in required'}


def test_windows_auth_user_is_accepted(app, client):
    app.config['REQUIRE_AUTH'] = True
    res = client.get('/api/me', environ_base={'REMOTE_USER': 'CORP\\ksiil'})
    assert res.status_code == 200
    assert res.get_json() == {'user': 'CORP\\ksiil', 'auth_required': True}


def test_page_shell_loads_without_a_user(app, client):
    # IIS guards the page itself; Flask only has to keep data behind sign-in
    app.config['REQUIRE_AUTH'] = True
    assert client.get('/').status_code == 200


def test_production_requires_auth_by_default():
    from config import ProductionConfig
    assert ProductionConfig.REQUIRE_AUTH is True


def test_security_headers(client):
    res = client.get('/api/me')
    assert res.headers['X-Content-Type-Options'] == 'nosniff'
    assert res.headers['X-Frame-Options'] == 'DENY'


def test_health_reports_database_and_empty_datasets(client):
    res = client.get('/api/health')
    body = res.get_json()
    assert res.status_code == 200
    assert body['database'] == 'ok'
    assert body['datasets']['deltav_io'] == {'loaded': False, 'rows': 0, 'uploaded': None}


def test_datasets_report_rows_and_last_load(app, client):
    from acp_app import db
    with app.app_context():
        pd.DataFrame({'tag': ['A', 'B'], 'uploaded': pd.to_datetime(['2026-08-01 00:00', '2026-08-19 11:06'])}) \
            .to_sql('deltav_io', db.engine, index=True, index_label='index')
        status = client.get('/api/datasets').get_json()
    assert status['deltav_io'] == {'loaded': True, 'rows': 2, 'uploaded': '2026-08-19 11:06:00'}


def test_health_fails_when_aspen_is_down(app, client, monkeypatch):
    import acp_app.api.health as health
    def broken(*args, **kwargs):
        raise RuntimeError('no driver')
    monkeypatch.setattr(health, 'AspenConn', broken)
    res = client.get('/api/health?aspen=1')
    assert res.status_code == 503
    assert res.get_json()['aspen'] == 'error'
    assert res.get_json()['aspen_error'].startswith('Unable to connect to Aspen server')


# --------------------------------------------------------------------------- #
# Aspen limits
# --------------------------------------------------------------------------- #

def _fake_aspen(monkeypatch, rows, seen):
    """Swap AspenConn for one backed by mfgkit's fake connection."""
    import acp_app.api.aspen as aspen_api
    from mfgkit.aspen import AspenConn
    from test_aspen import FakeConn

    def factory(server, **kwargs):
        conn = FakeConn()
        conn.queue(['NAME'], rows)
        seen.append((kwargs, conn))
        return AspenConn(server, connect_fn=lambda: conn, **kwargs)
    monkeypatch.setattr(aspen_api, 'AspenConn', factory)


def test_aspen_search_is_capped_on_the_server(app, client, monkeypatch):
    app.config['ASPEN_SEARCH_MAX_ROWS'] = 2
    seen = []
    _fake_aspen(monkeypatch, [('FT1',), ('FT2',), ('FT3',)], seen)

    body = client.get('/api/aspen/analog/FT').get_json()

    kwargs, conn = seen[0]
    assert kwargs['max_rows'] == 3
    assert 'SET MAX_ROWS 3;' in conn.executed
    assert body['total'] == 2
    assert body['truncated'] is True


def test_aspen_routes_are_rate_limited(monkeypatch, tmp_path):
    # Limits are off in the testing config, so build an app with them on
    from config import TestingConfig
    monkeypatch.setattr(TestingConfig, 'RATELIMIT_ENABLED', True)
    monkeypatch.setattr(TestingConfig, 'ASPEN_RATE_LIMIT', '2 per minute')
    client = create_app('testing').test_client()
    _fake_aspen(monkeypatch, [], [])

    codes = [client.get('/api/aspen/analog/FT').status_code for _ in range(3)]
    assert codes == [200, 200, 429]
    assert 'Too many requests' in client.get('/api/aspen/analog/FT').get_json()['error']


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def test_init_all_keeps_going_after_a_failure(app, monkeypatch):
    import click
    import acp_app.commands as commands

    ran = []

    @click.command('init-good')
    def good():
        ran.append('good')

    @click.command('init-bad')
    def bad():
        raise click.ClickException('no files')

    monkeypatch.setattr(commands, 'INIT_COMMANDS', [bad, good])
    result = app.test_cli_runner().invoke(commands.init_all)

    assert ran == ['good']
    assert result.exit_code == 1
    assert 'init-bad failed: no files' in result.output
    assert '1 of 2 loaded; failed: init-bad' in result.output
