"""Serve the app under a URL prefix such as /acp.

IIS may hand the app the full path (/acp/api/team) or one with the prefix
already removed (/api/team), depending on how wfastcgi is set up. Either way the
routes are written without the prefix, so move a leading prefix from PATH_INFO
to SCRIPT_NAME (which Flask uses to build URLs) and leave other paths alone.
"""


class StripPrefix:
    def __init__(self, app, prefix):
        self.app = app
        self.prefix = '/' + prefix.strip('/') if prefix.strip('/') else ''

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        prefix = self.prefix
        if prefix and (path == prefix or path.startswith(prefix + '/')):
            environ['SCRIPT_NAME'] = environ.get('SCRIPT_NAME', '').rstrip('/') + prefix
            environ['PATH_INFO'] = path[len(prefix):] or '/'
        return self.app(environ, start_response)
