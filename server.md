# Fedora server

The server profile installs the original server capabilities: timezone/Chrony,
firewalld, Cockpit, Podman/Compose/Toolbx, Incus, Tailscale, Syncthing, Hermes,
rclone and Restic. It also includes the explicitly shared terminal, Git, mise
development tools and Proton Pass CLI. nginx, Glance and Open WebUI are outside
the maintained profiles.

```sh
ansible-playbook playbooks/server.yml -K
```

Set storage paths and backup enrollment in inventory. Defaults place deployments
under `~/serve/apps` and state under `~/storage`. Services installed by roles may
start during a real apply; writing Hermes configuration does not start the app.

All server apps/containers must keep valuable persistent state under
`~/storage/<app>` (or the configured `server_storage_dir`) for backup.
Back up selected valuable data, such as Hermes memory, while keeping caches and
other reproducible files separate. See the [storage policy](docs/backups.md#server-app-storage-policy).

- [Incus](roles/server/incus/README.md): `incus admin init`, then enrollment on Tailscale;
  HTTPS 8443 TCP is bound to its tailnet address.
- Cockpit: HTTPS 9090 TCP, opened by firewalld.
- [Hermes](roles/server/hermes/README.md): dashboard 9119 TCP, gateway localhost 18642;
  migration requires maintenance downtime.
- [Syncthing](roles/base/syncthing/README.md): core pairing on both devices;
  22000 TCP/UDP transfers, local GUI 8384 TCP.
- [Independent backups](docs/backups.md): core at 03:00, apps at 04:00;
  both disabled until authorization, initialization and restore verification.
- [Secrets](docs/secrets.md): explicit Proton Pass enrollment and controller injection.
- [Control](roles/server/_control/README.md): explicit app lifecycle.
