# hermes

- Select with `hermes` or `apps`; includes Podman and server firewall prerequisites.
- Compose: `{{ hermes_app_dir }}/apps/hermes/docker-compose.yml` (default `~/serve`).
- State: `{{ hermes_storage_dir }}/data` (default `~/storage/hermes`).
  Valuable state such as Hermes memory belongs here for recovery after container recreation.
  Browser/models directories are downloadable caches excluded from app backups.
- Override `hermes_image`, directory variables, `hermes_dashboard_port` (9119 TCP),
  and `hermes_dashboard_insecure`. Gateway is localhost 18642 TCP.
- Existing insecure mode defaults are retained. Authenticated mode requires the
  three `HERMES_DASHBOARD_BASIC_AUTH_*` controller environment variables, or
  `hermes_dashboard_username`, `hermes_dashboard_password`, `hermes_dashboard_secret`.
  Existing stored credentials are preserved when new inputs are absent.
- Compose is private (0600); lifecycle stays in `roles/server/_control`.
- Enrollment: start explicitly, then run Hermes setup:

```sh
ansible-playbook playbooks/control.yml -e control_action=up -e control_app=hermes
podman compose -f ~/serve/apps/hermes/docker-compose.yml exec hermes hermes setup
```

For migration, schedule downtime and disable app backup timers. Record whether
Hermes is running, stop the old deployment, make a recovery copy of its Compose
file and data, then copy existing `~/serve/state/hermes` (or the old volume's actual
path) into `~/storage/hermes/data`. Preserve ownership and permissions.
Inspect the new mount paths before applying `--tags hermes`; start only if it was
previously running and verify the data. Keep recovery copies until verified.
The role never moves live data automatically. [App backup recovery](../../../docs/backups.md).
