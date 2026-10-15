from acp_app.prefix import StripPrefix


def call(prefix, path):
    seen = {}

    def inner(environ, start_response):
        seen.update(path=environ['PATH_INFO'], script=environ.get('SCRIPT_NAME', ''))
        return []

    StripPrefix(inner, prefix)({'PATH_INFO': path}, None)
    return seen


def test_prefix_moves_to_script_name():
    assert call('/acp', '/acp/api/team') == {'path': '/api/team', 'script': '/acp'}
    assert call('/acp', '/acp') == {'path': '/', 'script': '/acp'}


def test_already_stripped_or_other_paths_are_untouched():
    assert call('/acp', '/api/team') == {'path': '/api/team', 'script': ''}
    assert call('/acp', '/acpx/y') == {'path': '/acpx/y', 'script': ''}


def test_no_prefix_configured():
    assert call('', '/acp/api/team') == {'path': '/acp/api/team', 'script': ''}
