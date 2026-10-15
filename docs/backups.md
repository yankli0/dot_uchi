# Independent core and app backups

Run `playbooks/server.yml --tags backup` to install/configure, without enabling
either timer. Restic and rclone are server-only. Core backup uses the server's
canonical `core_path`; clients synchronize their core to the server with Syncthing.

| Job | Source | Default repository | Schedule |
| --- | --- | --- | --- |
| core | `core_path` | `rclone:gdrive:Backups/<inventory-host>/core` | 03:00 |
| apps | `~/storage/hermes/data`, `~/serve/apps/hermes` | `rclone:gdrive:Backups/<inventory-host>/apps` | 04:00 |

Each has its own password, environment, script, user service and timer.
Both jobs are server-only. Randomized delay is 15 minutes; timers persist missed
runs. No retention or pruning runs automatically.

## Server app storage policy

Every server app/container must keep valuable persistent state in a host
bind mount under `{{ server_storage_dir }}/<app>` (default `~/storage/<app>`),
so recovery does not depend on a container's writable layer or an anonymous volume.
For Hermes, memory is an example of valuable state that must survive recreation.

Choose backup sources explicitly for data that cannot be recreated: memory,
user content, and necessary application configuration or database exports.
Keep caches, downloaded models, disposable logs, and temporary files separate
from those sources. Storing a file under `storage` does not automatically make it
valuable or enroll it in backup; never back up the entire storage tree by default.
Each new app must document its valuable state paths, exclusions, consistency
procedure and restore test before joining the apps job.

## Enrollment and restore tests

As the target normal user, run `rclone config` to authorize a remote named `gdrive`.
For a headless server, authorize in a browser on another device with `rclone authorize`
and transfer the resulting token privately as requested by the wizard.
Protect `~/.config/rclone/rclone.conf` with mode 0600. Keep its recovery copy in Pass.

Create independent `~/.config/restic/core.password` and, on the server,
`apps.password` files with mode 0600 in a 0700 directory. Use an existing
repository's password when adopting it. Back up both passwords and repository
URIs in Proton Pass; losing a password makes its repository unrecoverable.

On the server, for each job independently (replace `core` with `apps` for the second):

```sh
source ~/.config/restic/core.env
restic snapshots
# ONLY if this is a new repository:
restic init
~/.local/bin/restic-core-backup
restic check
restore_dir=$(mktemp -d /tmp/restic-core-restore.XXXXXX)
restic restore latest --target "$restore_dir"
```

Inspect and compare restored data with its source. A successful snapshot listing
alone does not prove restoration. The apps fixture must include data and Compose
configuration; browser/model caches are intentionally excluded.

After authorization, initialization and successful restore, set only that job's
host variables:

```yaml
restic_core_enabled: true
restic_core_restore_verified_repository: rclone:gdrive:Backups/gmk-de/core
# Independently, after testing apps:
restic_apps_enabled: true
restic_apps_restore_verified_repository: rclone:gdrive:Backups/gmk-de/apps
```

Rerun the corresponding profile with `--tags backup`. It requires local credentials,
the exact restore-tested repository URI and successful repository access before
enabling the timer. Enable flags are explicit authorization for scheduling.
Repeat restore verification if the repository changes.

```sh
systemctl --user list-timers restic-core.timer restic-apps.timer
journalctl --user -u restic-core.service -u restic-apps.service -n 50 --no-pager
```

## Hermes consistency and interrupted recovery

App backup records whether the `hermes` container is running. If running, it
creates a private recovery marker, stops the container, backs up data/config,
then starts that same container. A previously stopped or absent container stays
stopped. No new container is created. Plan for downtime for the entire app backup.
Do not run lifecycle commands or change deployments during that window.

An exit trap restores Hermes even on Restic failure. The systemd service also runs
`restic-apps-backup --recover` after interruption. If the process is killed outside
systemd or the machine loses power, `~/.config/restic/hermes.resume` remains.
The next app backup recovers it first; to recover immediately after boot:

```sh
~/.local/bin/restic-apps-backup --recover
```

A lock prevents overlapping backup/recovery. If Podman recovery fails, the marker
stays and the command fails; inspect the container/logs and rerun recovery.
Do not delete the marker until the original running state has been restored.
Browser/models and cache directories are excluded. Future apps need a declared
export/quiesce strategy and explicit source list before joining this job.

## Existing repositories and migration

The old `restic-backup` environment, password, service and timer are preserved.
An enabled or active legacy job blocks new job configuration. Use the migration
procedure below before enrolling the independent jobs.

1. Record the old repository, password, source and timer state; make recovery copies.
2. Disable the old timer explicitly with `systemctl --user disable --now restic-backup.timer`.
   Let any active `restic-backup.service` finish, then verify it is inactive.
3. Choose whether core adopts the old repository or uses a new one. To adopt it,
   set `restic_core_repository` to its existing URI, copy its password securely into
   `core.password`, and test a restore. To migrate, initialize/test the new core repo
   separately. Keep the old repository/password available for historical restores.
4. Configure the new jobs; independently complete their enrollment and restore tests.
5. Enable only the verified jobs. Keep old local files archived for recovery.

For an already configured new job, the role rejects a changed repository URI,
even if its timer is disabled. Disable the job timer, wait for its service to
finish, preserve its environment/password, test the destination, then manually
archive/remove only that job's old `core.env` or `apps.env` before applying the new
configuration. This deliberate maintenance step prevents silent redirection.

## Independent restores and secret recovery

Core: recover its password/rclone config from Pass, source `core.env`, and restore
the chosen snapshot to a temporary directory. Compare it before copying files
into `core_path`. Pause Syncthing on both endpoints during recovery so deletions or
older versions do not propagate; resume only after reviewing the recovered tree.

Apps: disable `restic-apps.timer`, recover its password/rclone config, source
`apps.env`, and restore into a temporary directory. Inspect restored Hermes data
and Compose files (which may contain secrets). Stop Hermes for the maintenance
window, preserve current state/configuration, then copy the restored directories
to their configured locations, preserving ownership and private file permissions.
Start only if previously running, verify the application, then re-enable the timer.
Cache downloads can be recreated. Recover provider credentials separately from
Pass if they were not part of the application's persistent data.

Restic restores absolute source paths beneath the chosen target; do not restore
directly over live state without inspection. Core and apps passwords/repositories
are independent: a restore from one does not require the other's password.
Use manual `restic forget --dry-run` and inspect retention decisions before pruning.
