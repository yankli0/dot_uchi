# Architecture and selection

Read this when changing layout, inventory ownership, profile boundaries or tags.

Both client and server include the base profile. Shared capabilities belong in
`roles/base`; desktop capabilities in `roles/client`; server services and backups
in `roles/server`. Simple package lists stay in `playbooks/tasks/<profile>`.
Configured tools own their tasks, native files, common defaults and short README.
Use explicit role paths; keep `playbooks/roles.yml` as the compatibility entrypoint.

Connection details belong in `inventory/hosts.yml`, shared selections in
`inventory/group_vars`, and machine-specific paths/settings in
`inventory/host_vars`. Playbooks orchestrate rather than hold user preferences.
Inspect those files for current values instead of copying them into context guides.

Group and individual tool tags must include the selected tools' prerequisites.
Selecting a client tool must not configure server apps or backups. Selecting
`terminal`, `passwords` or `backup` must not prompt for Git identity.

nginx, Glance and Open WebUI are outside the maintained profiles.
Removing repository configuration does not authorize uninstalling an existing deployment.

See [the glossary](../CONTEXT.md) for terminology and
[README](../README.md) for entrypoints and available selection tags.
