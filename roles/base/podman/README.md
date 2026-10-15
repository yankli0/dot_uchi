# podman

- Installs Podman, Compose and Toolbx; enables user lingering and the user socket.
- Select with `podman` or `containers`; also required by server Hermes and app backup.
- Override `podman_packages` if needed. No account enrollment.
- App lifecycle belongs to `roles/server/_control`; socket is local, no network ports.
