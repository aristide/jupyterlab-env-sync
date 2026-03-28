# jupyterlab-env-sync

[![Build](https://github.com/aristide/jupyterlab-env-sync/actions/workflows/build.yml/badge.svg)](https://github.com/aristide/jupyterlab-env-sync/actions/workflows/build.yml)
[![PyPI](https://img.shields.io/pypi/v/jupyterlab-env-sync.svg)](https://pypi.org/project/jupyterlab-env-sync/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/aristide/jupyterlab-env-sync/master?urlpath=lab)

A JupyterLab 4.x extension that provides a shared service for propagating environment variables to running kernels (Python, R, Julia) and terminals.

Other extensions consume `jupyterlab-env-sync` via the `IEnvSync` token to set, reset, and query environment variables without dealing with kernel injection or terminal lifecycle directly.

## Features

- **Kernel propagation** — injects env var changes into all running Python, R, and Julia kernels
- **Terminal restart** — restarts open terminals so they inherit updated variables, with a toast notification
- **Startup hooks** — new kernels and terminals automatically pick up overrides via IPython/R/Julia startup scripts
- **Multi-extension support** — multiple consumer extensions can set variables independently; ownership is tracked per key
- **Spawner-aware reset** — resetting a variable restores the original spawner value (or deletes it if none existed)

## Requirements

- JupyterLab >= 4.0.0
- Python >= 3.8

## Installation

```bash
pip install jupyterlab-env-sync
```

## API

Consumer extensions depend on the `IEnvSync` token:

```typescript
import { IEnvSync } from 'jupyterlab-env-sync';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:plugin',
  autoStart: true,
  requires: [IEnvSync],
  activate: async (app: JupyterFrontEnd, envSync: IEnvSync) => {
    await envSync.setVar(
      'my-extension',
      'DATABASE_URL',
      'postgres://localhost/mydb'
    );
  }
};
```

### Methods

| Method                | Signature                                   | Description                                                           |
| --------------------- | ------------------------------------------- | --------------------------------------------------------------------- |
| `setVar`              | `(extId, key, value) → Promise<void>`       | Set a variable. Propagates to all kernels and restarts terminals.     |
| `resetVar`            | `(extId, key, force?) → Promise<void>`      | Reset to spawner value. Only the owner can reset unless `force=true`. |
| `getAll`              | `() → Promise<Record<string, IEnvEntry>>`   | All overrides with metadata (value, spawner_value, set_by, set_at).   |
| `getByExtension`      | `(extId) → Promise<Record<string, string>>` | Variables owned by a specific extension (key-value pairs).            |
| `resetAllByExtension` | `(extId) → Promise<void>`                   | Reset all variables owned by an extension.                            |

### Example: MinIO credentials

```typescript
import { IEnvSync } from 'jupyterlab-env-sync';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-minio-extension:plugin',
  autoStart: true,
  requires: [IEnvSync],
  activate: async (app: JupyterFrontEnd, envSync: IEnvSync) => {
    await envSync.setVar('my-minio-extension', 'MINIO_ENDPOINT', 'https://minio.example.com');
    await envSync.setVar('my-minio-extension', 'MINIO_ACCESS_KEY', 'my-access-key');
    await envSync.setVar('my-minio-extension', 'MINIO_ACCESS_SECRET', 'my-secret-key');

    // All running kernels now have these variables in os.environ.
    // New kernels pick them up automatically via the IPython startup hook.
    // Secret values (keys matching SECRET, PASSWORD, TOKEN, PRIVATE_KEY)
    // are masked in kernel startup log output.
  }
};
```

### Consumer `package.json`

```json
{
  "dependencies": {
    "jupyterlab-env-sync": "^1.0.0"
  },
  "jupyterlab": {
    "sharedPackages": {
      "jupyterlab-env-sync": { "bundled": false, "singleton": true }
    }
  }
}
```

> `bundled: false` and `singleton: true` are required so all extensions share the same `IEnvSync` token instance.

## Development

### Development Installation

```bash
# Clone the repository
git clone https://github.com/aristide/jupyterlab-env-sync.git
cd jupyterlab-env-sync

# Set up a virtual environment
virtualenv .venv
source .venv/bin/activate

# Install in development mode
pip install -e ".[test]"

# Link the extension with JupyterLab
jupyter labextension develop . --overwrite

# Enable the server extension
jupyter server extension enable jupyterlab-env-sync

# Build the TypeScript source
jlpm build
```

### Running Tests

```bash
# Python tests (env store + REST handlers)
pytest jupyterlab-env-sync/tests/ -v

# TypeScript tests (kernel injection snippets)
jlpm test

# UI tests (requires Playwright)
cd ui-tests && jlpm install && npx playwright test
```

### Development Uninstallation

```bash
jupyter server extension disable jupyterlab-env-sync
pip uninstall jupyterlab-env-sync
```

## License

BSD-3-Clause
