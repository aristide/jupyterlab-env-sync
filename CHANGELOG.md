# Changelog

<!-- <START NEW CHANGELOG ENTRY> -->

## 1.1.1

### Bug Fixes

- **Fix startup hook crash with flat JSON overrides** — the IPython startup hook assumed the overrides file always used `{"key": {"value": "..."}}` format, but plain `{"key": "value"}` entries caused a `TypeError` that prevented all startup hooks from running. The hook now handles both formats.

### Enhancements

- **Secret masking in startup logs** — environment variables with names containing `SECRET`, `PASSWORD`, `TOKEN`, or `PRIVATE_KEY` are now masked as `****` in kernel startup log output

### Tests

- Added unit tests for startup hook installation, env var loading, and secret masking patterns

<!-- <END NEW CHANGELOG ENTRY> -->

<!-- <START NEW CHANGELOG ENTRY> -->

## 1.1.0

### Enhancements

- **npm publishing with provenance** — added `publish-npm` job to the release workflow that publishes the package to npm with SLSA provenance attestation (`--provenance`)
- **Updated `publishConfig`** — added `"provenance": true` to `package.json` for signed build attestations

<!-- <END NEW CHANGELOG ENTRY> -->

<!-- <START NEW CHANGELOG ENTRY> -->

## 1.0.0

### New Features

- **IEnvSync token** — public API for consumer extensions to set, reset, and query environment variables (`setVar`, `resetVar`, `getAll`, `getByExtension`, `resetAllByExtension`)
- **Server-side persistence** — REST API (`GET/PUT/DELETE /jupyterlab-env-sync/env`) backed by a JSON file in the Jupyter runtime directory; also mutates `os.environ` so new processes inherit values
- **Kernel propagation** — injects env var changes into all running Python, R, and Julia kernels via silent `requestExecute`
- **Terminal restart** — shuts down and reopens terminals when variables change, with a toast notification
- **Startup hooks** — installs IPython, R, and Julia startup scripts so new kernels automatically load overrides
- **Multi-extension ownership** — tracks which extension set each variable; `resetAllByExtension` only cleans up that extension's keys
- **Spawner-aware reset** — captures the original spawner value on first override and restores it on reset
- **Conflict resolution** — last-write-wins with a logged warning when extensions target the same key

### Tests

- Python unit tests for `EnvStore` (set, reset, ownership, spawner restoration)
- Python integration tests for REST handlers via `pytest-jupyter`
- TypeScript unit tests for kernel injection snippet generation (Python, R, Julia)
- Playwright UI tests for REST API and kernel propagation

<!-- <END NEW CHANGELOG ENTRY> -->
