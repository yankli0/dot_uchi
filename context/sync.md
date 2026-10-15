# Core paths and Syncthing

Read this when changing core storage, external mounts, device enrollment or pairing.

Each host has one canonical `core_path` in host variables. Synchronization uses
that endpoint's path; server core backup reuses the server's path.
Only create a missing core directory when `core_create_if_missing` permits it.
Check directory access as the configured user. For the client external drive,
verify `core_expected_mount` before creating directories or configuring sync.

Device IDs are defined once by inventory host name in `syncthing_device_ids`.
These are public identifiers, not credentials; private keys and API/GUI secrets
remain local. Folder membership is explicit. Preserve shared core folder ID
`wekzg-5dp7t` and each endpoint's own folder path.

Allow initial enrollment with no peer IDs, reporting the local ID.
Explicitly declared peers need valid unique IDs. Never pair a device with itself.
Configure both endpoints for mutual sharing; a one-sided change is insufficient.
Default to bidirectional sync, with explicit per-device send-only/receive-only modes.
Preserve unmanaged peers, folders and shares across repeat runs.

Report successful configuration separately from connectivity and synchronization
completion. An offline peer has not been verified as synchronized.
Terminal deployment must not synchronize history, credentials or SSH keys.

See [Syncthing enrollment](../roles/base/syncthing/README.md) and
[core validation](../roles/base/core/README.md) before changing these workflows.
