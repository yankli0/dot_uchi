# Server applications, storage and backups

Read this when adding/changing server services, containers, persistent data or backups.

The server profile follows [server guidance](../server.md), plus base tools.
Incus, Cockpit, Hermes and Restic/rclone remain server capabilities.
Use role READMEs for common overrides, enrollment and externally reachable ports.

App roles write Compose configuration beneath `{{ <role>_app_dir }}/apps/<app>`.
Lifecycle is explicit through `roles/server/_control`; writing app configuration
must not start containers or move live data. Migration requires a maintenance
procedure that preserves recovery copies and the application's previous running state.

Every container must bind-mount valuable persistent state under
`{{ server_storage_dir }}/<app>` (default `~/storage/<app>`).
Hermes memory is an example of valuable state. Keep caches, downloaded models,
disposable logs and temporary files separate. Placement under `storage` does not
automatically enroll data in backup; select valuable sources explicitly.

[Restic](../roles/server/restic/README.md) and rclone are server-only.
Core and apps have independent repositories, password files, services, timers and
enable flags. Enable each only after authorization, initialization and its own
successful restore test. Preserve existing repositories until explicit migration.
Retention and pruning remain manual.

The current apps job backs up the Hermes data tree and deployment configuration,
excluding caches. A running Hermes is stopped for consistency and restored after
success/failure; a stopped app stays stopped. Interrupted backups retain recovery
intent. Future apps require explicit source selection and a consistency strategy.

Use [backup procedures](../docs/backups.md) for scheduling, migration, independent
restores and interruption recovery, and [Hermes maintenance](../roles/server/hermes/README.md)
for its deployment and state paths.
