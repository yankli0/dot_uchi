# Verification and completion

Read this when verifying implementation or reporting that a workflow works.

Use local syntax checks, task listings and isolated fixtures during implementation.
Applying profiles to real machines, enrollment and live data migrations require
explicit task authorization. Preserve unrelated worktree changes; do not commit
unless requested.

After Ansible changes, run with a compatible controller environment:

```sh
python -m unittest discover tests/
ANSIBLE_LOCAL_TEMP=/tmp/ansible-local TMPDIR=/tmp ansible-playbook --syntax-check playbooks/site.yml
ANSIBLE_LOCAL_TEMP=/tmp/ansible-local TMPDIR=/tmp ansible-playbook --syntax-check playbooks/control.yml
ansible-lint playbooks/site.yml playbooks/control.yml
```

The `tests/` suite currently covers:

- `test_syntax.py`: `--syntax-check` for `site.yml` and `control.yml`.
- `test_isolation.py`: `--list-tasks` assertions that `--tags git`,
  `--tags browser`, and `--tags hermes` only touch the expected roles.

A catalog test will be added once the per-app installer is implemented.

Run checks relevant to the change. Validate native shell/TOML configuration and
local documentation/role references when relocating files.
Report fixture evidence separately from real authentication, remote sync,
Podman deployments and systemd scheduling. Mocked success does not verify a live service.

[Verification report](../docs/role-redesign-verification.md) records previous results
and untested live checks; rerun relevant checks rather than treating that report as
proof for later changes. Current workflow decisions are recorded in these context
guides and the affected role READMEs.
