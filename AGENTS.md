# AGENTS

- Keep role documentation short and practical, matching existing `roles/*/*/README.md` style.
- Prefer `rg` for searches and inspect role defaults/templates before changing behavior.
- Do not revert unrelated user changes in this repository.
- For manual edits, use `apply_patch`.
- Run `ANSIBLE_LOCAL_TEMP=/tmp/ansible-local TMPDIR=/tmp ansible-playbook --syntax-check playbooks/site.yml` after Ansible role changes when possible.
- Server app roles should write compose files into `{{ <role>_app_dir }}/apps/<app>` and leave lifecycle operations to `roles/server/_control`.
- Server apps must bind-mount valuable state under `{{ server_storage_dir }}/<app>`; back up selected valuable data, such as Hermes memory, separately from reproducible files.
- Keep only commonly overridden values in role defaults and document externally reachable ports in each server role README.
- Shared development tools use mise with `latest`; Restic/rclone and backup jobs are server-only.
- Preserve local credentials, private keys, application state and existing repositories; enrollment and migrations are explicit.

## Context

Before changing a part, read its guide and the affected role README/defaults/templates.
Keep the relevant guide current when ownership or workflow changes.

- Layout, inventory, profile boundaries or tags: [architecture](context/architecture.md).
- Shared shell, development tools, Git or SSH: [base](context/base.md).
- Desktop apps, editors or AI clients: [client](context/client.md).
- Server apps, containers, storage or backups: [server](context/server.md).
- Core paths, mounts, device IDs or pairing: [sync](context/sync.md).
- Credentials, account enrollment or secret injection: [secrets](context/secrets.md).
- Implementation checks, fixtures or claims of success: [verification](context/verification.md).
