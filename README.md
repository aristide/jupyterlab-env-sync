# jupyterlab-env-sync

A JupyterLab extension.

## Requirements

- JupyterLab >= 4.0.0
- Python >= 3.8

## Installation

```bash
pip install jupyterlab-env-sync
```

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

### Development Uninstallation

```bash
jupyter server extension disable jupyterlab-env-sync
pip uninstall jupyterlab-env-sync
```
