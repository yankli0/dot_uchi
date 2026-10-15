# core

- Validates the canonical `core_path` before sync or backup setup.
- Creation requires `core_create_if_missing: true`; defaults to false.
- `core_expected_mount` requires an exact mounted path before creating anything.
- Requires directory read/write/traverse access as the configured user.
- Select through `syncthing`/`sync`, or server-only `restic`/`backup`; no enrollment or ports.
