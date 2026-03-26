import importlib

collect_ignore_glob = [
    "jupyterlab-env-sync/_version.py",
    "jupyterlab-env-sync/__init__.py",
    "jupyterlab-env-sync/handlers.py",
    "jupyterlab-env-sync/env_store.py",
    "jupyterlab-env-sync/startup_hooks.py",
]

# Only load jupyter_server fixtures if pytest_jupyter is available
if importlib.util.find_spec("pytest_jupyter"):
    pytest_plugins = ("pytest_jupyter.jupyter_server",)

    import pytest

    @pytest.fixture
    def jp_server_config(jp_server_config):
        return {"ServerApp": {"jpserver_extensions": {"jupyterlab-env-sync": True}}}
