# restic

- Server-only: select with `restic`, `rclone` or `backup` in `playbooks/server.yml`.
  Installs Restic/rclone and validates the server's core.
- Core: `core_path` → `rclone:gdrive:Backups/<inventory-host>/core`, 03:00.
- Server apps: Hermes data/config → `rclone:gdrive:Backups/<inventory-host>/apps`, 04:00.
- Separate passwords, user services/timers and `restic_core_enabled`/`restic_apps_enabled`
  flags (both false). Timers have 15-minute randomized delay and persist missed runs.
- Override `restic_core_repository`/`restic_apps_repository` for an existing repository.
  A configured repository cannot be redirected silently.
- Enrollment requires rclone authorization, repository initialization and a successful
  restore test. Set each `restic_<job>_restore_verified_repository` to the tested URI.
- App backup stops a running Hermes and restores its prior state on failure.
  Caches are excluded; new apps need an explicit consistency strategy.
- [Enrollment, migration, interrupted recovery and independent restores](../../../docs/backups.md).
- Retention/pruning remains manual. No inbound ports.
