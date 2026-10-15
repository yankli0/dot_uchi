# control

- Explicit server app lifecycle; select `playbooks/control.yml` (`control` tag).
- `control_action`: status (default), up, down, restart.
- `control_app`: hermes (default), one app directory name, or all.
- `control_homelab_dir` defaults to `server_app_dir`; apps live beneath `apps/`.
- Requires enrolled Podman/Compose and an existing deployment; no installation here.
- `all` includes old app directories. No independent listening ports.
