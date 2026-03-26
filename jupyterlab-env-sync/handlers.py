import json

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join


class EnvAllHandler(APIHandler):
    """GET /jupyterlab-env-sync/env — return all overrides or filter by extension_id."""

    @tornado.web.authenticated
    def get(self):
        store = self.settings['env_store']
        extension_id = self.get_argument('extension_id', None)
        if extension_id:
            data = store.get_by_extension(extension_id)
        else:
            data = store.get_all()
        self.finish(json.dumps(data))


class EnvVarHandler(APIHandler):
    """PUT/DELETE /jupyterlab-env-sync/env/{key} — set or reset a single variable."""

    @tornado.web.authenticated
    def put(self, key):
        store = self.settings['env_store']
        body = json.loads(self.request.body)
        extension_id = body['extension_id']
        value = body['value']
        entry = store.set_var(extension_id, key, value)
        self.set_status(200)
        self.finish(json.dumps(entry))

    @tornado.web.authenticated
    def delete(self, key):
        store = self.settings['env_store']
        body = json.loads(self.request.body) if self.request.body else {}
        extension_id = body.get('extension_id', '')
        force = body.get('force', False)
        ok = store.reset_var(extension_id, key, force=force)
        if ok:
            self.set_status(200)
            self.finish(json.dumps({'status': 'reset'}))
        else:
            self.set_status(403)
            self.finish(json.dumps({'error': 'not owner and force not set'}))


class EnvExtensionHandler(APIHandler):
    """DELETE /jupyterlab-env-sync/env/extension/{extension_id} — reset all vars for an extension."""

    @tornado.web.authenticated
    def delete(self, extension_id):
        store = self.settings['env_store']
        keys = store.reset_all_by_extension(extension_id)
        self.finish(json.dumps({'reset_keys': keys}))


def setup_handlers(web_app):
    host_pattern = '.*'
    base_url = web_app.settings['base_url']
    handlers = [
        (url_path_join(base_url, 'jupyterlab-env-sync', 'env'), EnvAllHandler),
        (
            url_path_join(
                base_url, 'jupyterlab-env-sync', 'env', 'extension', '([^/]+)'
            ),
            EnvExtensionHandler,
        ),
        (url_path_join(base_url, 'jupyterlab-env-sync', 'env', '([^/]+)'), EnvVarHandler),
    ]
    web_app.add_handlers(host_pattern, handlers)
