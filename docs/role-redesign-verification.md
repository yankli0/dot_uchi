# Role redesign verification

Implementation checks use the existing Python 3.13 Ansible environment.

Run the test suite with a controller Python that has Ansible and the required
collections installed:

```sh
python -m unittest discover tests/
```

Tests currently cover:

- `tests/test_syntax.py`: `--syntax-check` for `playbooks/site.yml` and
  `playbooks/control.yml`.
- `tests/test_isolation.py`: `--list-tasks` assertions that `--tags git`,
  `--tags browser`, and `--tags hermes` only touch the expected roles.
- `tests/test_catalog.py`: validates the app catalog in
  `roles/client/apps/vars/catalog.yml` and that `inventory/group_vars/client.yml`
  selects only known app ids.

## Previous verification report (historical)

The old `tests/verify_roles.py` suite has been removed. Its claimed 16
acceptance tests are no longer in the repository and should not be treated as
current evidence.

## Live checks

The following still require explicit live verification on real targets:

- Proton Pass authentication and controller-side secret injection.
- Google Drive authorization and remote Restic repository restore.
- Real-device Syncthing connectivity and synchronization completion.
- Real Podman/Hermes deployment and systemd timer execution.

Neither machine's configuration has been applied by the test suite. Fixture
success does not imply live success.
