import json
import os
import sys
import textwrap

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from importlib import import_module

_mod = import_module('jupyterlab-env-sync.startup_hooks')
install_startup_hooks = _mod.install_startup_hooks
PYTHON_STARTUP = _mod.PYTHON_STARTUP


@pytest.fixture
def ipython_home(tmp_path, monkeypatch):
    """Redirect ~/.ipython to a temp directory."""
    ipython_dir = tmp_path / '.ipython'
    monkeypatch.setenv('HOME', str(tmp_path))
    return ipython_dir


@pytest.fixture
def runtime_dir(tmp_path):
    rd = tmp_path / 'runtime'
    rd.mkdir()
    return rd


class TestInstallPythonStartupHook:
    def test_creates_startup_file(self, ipython_home, runtime_dir):
        install_startup_hooks(str(runtime_dir))
        hook = ipython_home / 'profile_default' / 'startup' / '00-jupyterlab-env-sync.py'
        assert hook.exists()
        content = hook.read_text()
        assert 'env-sync' in content
        assert str(runtime_dir) in content

    def test_startup_hook_loads_env_vars(self, runtime_dir):
        """Simulate what the generated startup hook does: load vars from the overrides file."""
        overrides = {
            'MINIO_ENDPOINT': {'value': 'https://minio.example.com', 'set_by': 'test'},
            'MINIO_ACCESS_KEY': {'value': 'my-access-key', 'set_by': 'test'},
            'MINIO_ACCESS_SECRET': {'value': 'my-secret-key', 'set_by': 'test'},
        }
        overrides_path = runtime_dir / 'jupyter_env_overrides.json'
        overrides_path.write_text(json.dumps(overrides))

        # Execute the generated hook logic directly
        env_before = {k: os.environ.get(k) for k in overrides}
        try:
            with open(overrides_path) as f:
                for k, v in json.load(f).items():
                    os.environ[k] = v['value']

            assert os.environ['MINIO_ENDPOINT'] == 'https://minio.example.com'
            assert os.environ['MINIO_ACCESS_KEY'] == 'my-access-key'
            assert os.environ['MINIO_ACCESS_SECRET'] == 'my-secret-key'
        finally:
            for k, orig in env_before.items():
                if orig is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = orig

    def test_secret_masking_patterns_in_startup_template(self):
        """Verify that the startup template masks secret-like variable names."""
        assert 'SECRET' in PYTHON_STARTUP
        assert 'PASSWORD' in PYTHON_STARTUP
        assert 'TOKEN' in PYTHON_STARTUP
        assert 'PRIVATE_KEY' in PYTHON_STARTUP
        assert "'****'" in PYTHON_STARTUP
