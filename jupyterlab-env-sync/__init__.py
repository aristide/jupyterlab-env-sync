from ._version import __version__


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "jupyterlab-env-sync"}]


def _jupyter_server_extension_points():
    return [{"module": "jupyterlab-env-sync"}]


def _load_jupyter_server_extension(server_app):
    from .handlers import setup_handlers

    setup_handlers(server_app.web_app)
    name = "jupyterlab-env-sync"
    server_app.log.info(f"Registered {name} server extension")
