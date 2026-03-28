import os
import logging

logger = logging.getLogger(__name__)

MARKER = '# jupyterlab-env-sync auto-generated'

PYTHON_STARTUP = '''\
# jupyterlab-env-sync auto-generated — DO NOT EDIT
import json as _json, os as _os, sys as _sys
_p = _os.path.join(_os.environ.get('JUPYTER_RUNTIME_DIR', '/tmp'), 'jupyter_env_overrides.json')
if _os.path.exists(_p):
    _SECRET_PATTERNS = ('SECRET', 'PASSWORD', 'TOKEN', 'PRIVATE_KEY')
    with open(_p) as _f:
        for _k, _v in _json.load(_f).items():
            _val = _v['value'] if isinstance(_v, dict) else _v
            _os.environ[_k] = _val
            _masked = any(_s in _k.upper() for _s in _SECRET_PATTERNS)
            _display = '****' if _masked else _val
            print(f'[env-sync] {_k}={_display}', file=_sys.stderr)
    del _SECRET_PATTERNS
del _json, _os, _sys, _p
'''

R_STARTUP = '''\
# jupyterlab-env-sync auto-generated — DO NOT EDIT
local({
  p <- file.path(Sys.getenv("JUPYTER_RUNTIME_DIR", "/tmp"), "jupyter_env_overrides.json")
  if (file.exists(p)) {
    d <- jsonlite::fromJSON(p, simplifyVector = FALSE)
    for (k in names(d)) do.call(Sys.setenv, setNames(list(d[[k]]$value), k))
  }
})
# jupyterlab-env-sync end
'''

JULIA_STARTUP = '''\
# jupyterlab-env-sync auto-generated — DO NOT EDIT
let p = joinpath(get(ENV, "JUPYTER_RUNTIME_DIR", "/tmp"), "jupyter_env_overrides.json")
    if isfile(p)
        import JSON
        for (k, v) in JSON.parsefile(p)
            ENV[k] = v["value"]
        end
    end
end
# jupyterlab-env-sync end
'''


def _write_python_hook(runtime_dir):
    """Install IPython startup hook."""
    startup_dir = os.path.expanduser('~/.ipython/profile_default/startup')
    os.makedirs(startup_dir, exist_ok=True)
    hook_path = os.path.join(startup_dir, '00-jupyterlab-env-sync.py')

    content = PYTHON_STARTUP.replace(
        "'/tmp'",
        repr(runtime_dir)
    )
    with open(hook_path, 'w') as f:
        f.write(content)
    logger.info('Installed Python startup hook at %s', hook_path)


def _append_hook(filepath, content):
    """Append a hook block to a profile file if not already present."""
    existing = ''
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            existing = f.read()

    if MARKER in existing:
        return

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'a') as f:
        f.write('\n' + content)
    logger.info('Installed startup hook at %s', filepath)


def _write_r_hook(runtime_dir):
    """Append R startup hook to ~/.Rprofile."""
    content = R_STARTUP.replace('/tmp', runtime_dir)
    _append_hook(os.path.expanduser('~/.Rprofile'), content)


def _write_julia_hook(runtime_dir):
    """Append Julia startup hook to ~/.julia/config/startup.jl."""
    content = JULIA_STARTUP.replace('/tmp', runtime_dir)
    _append_hook(
        os.path.expanduser('~/.julia/config/startup.jl'),
        content
    )


def install_startup_hooks(runtime_dir):
    """Install startup hooks for Python, R, and Julia kernels."""
    try:
        _write_python_hook(runtime_dir)
    except Exception:
        logger.exception('Failed to install Python startup hook')
    try:
        _write_r_hook(runtime_dir)
    except Exception:
        logger.exception('Failed to install R startup hook')
    try:
        _write_julia_hook(runtime_dir)
    except Exception:
        logger.exception('Failed to install Julia startup hook')
