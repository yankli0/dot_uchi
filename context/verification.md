# Verification and completion

Read this when verifying implementation or reporting that a workflow works.

Use local syntax checks, task listings and isolated fixtures during implementation.
Applying profiles to real machines, enrollment and live data migrations require
explicit task authorization. Preserve unrelated worktree changes; do not commit
unless requested.

After Ansible changes, run with a compatible controller environment:

```sh
ANSIBLE_LOCAL_TEMP=/tmp/ansible-local TMPDIR=/tmp ansible-playbook --syntax-check playbooks/site.yml
ANSIBLE_LOCAL_TEMP=/tmp/ansible-local TMPDIR=/tmp ansible-playbook --syntax-check playbooks/control.yml
ansible-lint playbooks/site.yml playbooks/control.yml
```

[Acceptance fixtures](../tests/verify_roles.py) cover profile/tool isolation,
Git/SSH behavior, mount guards, temporary Syncthing pairing, independent local
Restic restores, repository/enrollment guards and mocked Hermes recovery.
They skip OS package installation and use temporary directories.
Ansible needs local Unix sockets; Syncthing fixtures need loopback sockets.

Run checks relevant to the change. Validate native shell/TOML configuration and
local documentation/role references when relocating files.
Report fixture evidence separately from real authentication, remote sync,
Podman deployments and systemd scheduling. Mocked success does not verify a live service.

[Verification report](../docs/role-redesign-verification.md) records previous results
and untested live checks; rerun relevant checks rather than treating that report as
proof for later changes. Current workflow decisions are recorded in these context
guides and the affected role READMEs.
