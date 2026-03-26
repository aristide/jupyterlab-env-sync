import os

from ._version import __version__


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "jupyterlab-env-sync"}]


def _jupyter_server_extension_points():
    return [{"module": "jupyterlab-env-sync"}]


def _load_jupyter_server_extension(server_app):
    from .env_store import EnvStore
    from .handlers import setup_handlers
    from .startup_hooks import install_startup_hooks

    runtime_dir = server_app.runtime_dir
    store_path = os.path.join(runtime_dir, 'jupyter_env_overrides.json')
    store = EnvStore(store_path)

    server_app.web_app.settings['env_store'] = store

    install_startup_hooks(runtime_dir)

    setup_handlers(server_app.web_app)
    server_app.log.info('Registered jupyterlab-env-sync server extension')
