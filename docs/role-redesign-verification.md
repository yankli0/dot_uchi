# Role redesign verification

Implementation checks use the existing Python 3.13 Ansible environment.
The fixture suite is `tests/verify_roles.py`; run with a controller Python that
has PyYAML, installed Ansible collections, Syncthing, Zsh and Restic:

```sh
ANSIBLE_PLAYBOOK=ansible-playbook RESTIC_BINARY="$(command -v restic)" \
  python tests/verify_roles.py
```

Fixtures use temporary directories and localhost-only Syncthing endpoints.
OS package tasks are skipped; Podman is mocked. No real machine profile is applied.
Ansible needs local Unix sockets, and Syncthing needs loopback sockets.

Syntax checks for `site.yml` and `control.yml` and Ansible lint passed using the
existing compatible Python 3.13 controller environment.

The 16 acceptance tests passed. They cover:

- Client/server isolation and standalone tool prerequisites in task listings;
  Restic/rclone and both backup jobs belong only to the server profile.
- Git existing identity, explicit precedence, preserved unrelated settings,
  repeat runs and clear unattended failure; unrelated tags omit Git prompts.
- SSH disabled by default, existing private-key preservation, hidden missing-secret
  handling and explicit empty-passphrase generation in a temporary directory.
- Missing external mounts failing before creation, and explicit directory creation.
- Two temporary Syncthing endpoints: initial enrollment, mutual peer declarations,
  per-endpoint paths and modes, repeat runs, preserved unmanaged folders/peers/shares.
  Missing and duplicate IDs fail before installation.
- Separate local Restic repository initialization, backups and independent restores
  using different passwords, cache exclusion, and independent timer schedules.
- Mocked Hermes prior-state restoration on success, backup failure, SIGTERM and
  SIGKILL recovery; a previously stopped app stays stopped.
- Existing repository redirection refusal, enabled legacy-job preservation and
  restore-verification enrollment gates.
- Individual mise selections, runtime prerequisites, preserved native config,
  `latest` versions without repeated installation when current, rendered TOML,
  shell syntax and local documentation links.

No skipped tests. Syncthing fixtures verify configuration, not real-device
connectivity or synchronization completion. Podman is mocked; Restic operations
use real temporary local repositories. Writing-for-agents and domain-modeling
guidance informed the short repository rules and base/client terminology.

Live checks deliberately excluded: Proton Pass authentication, Google Drive
authorization and remote repository restore, real-device connectivity/synchronization,
real Podman/Hermes deployment and systemd timer execution. Neither machine's
configuration has been applied.
