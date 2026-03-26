import json

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join


class HelloHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({"data": "Hello World from jupyterlab-env-sync!"}))


def setup_handlers(web_app):
    host_pattern = ".*"
    base_url = web_app.settings["base_url"]
    handlers = [
        (url_path_join(base_url, "jupyterlab-env-sync", "hello"), HelloHandler),
    ]
    web_app.add_handlers(host_pattern, handlers)
