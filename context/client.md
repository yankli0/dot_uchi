# Client profile

Read this when changing desktop application selections, editors or AI clients.

The client profile adds desktop tools to base. Browser, communication, notes and
3D-modeling selections live in `inventory/group_vars/client.yml`.
Preserve selected applications; unspecified lists stay empty.
[Flatpak](../roles/client/flatpak/README.md) owns installation/remote prerequisites.

Neovim, Zed, OpenCode, Claude Code, pi and local Ollama belong to the client.
[AI tools](../roles/client/ai-tools/README.md) use mise and `latest`, with Node
included when selected alone. Editor native configuration stays with its role.
Account/provider authorization and model downloads remain explicit enrollment.

Preserve native application configuration and credentials while editing roles.
Keep private generated configuration private and suppress secret-bearing output.
Do not move client editors or AI selections into server orchestration.

Clients use Syncthing for core sharing. Restic/rclone installation, backup
configuration and timers belong only to the server profile, including when
`backup`, `restic` or `rclone` tags are requested from the client playbook.

See [client orchestration](../playbooks/client.yml) for current selections and
[sync](sync.md) for the external-drive guard.
