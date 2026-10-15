# Dotfiles

Personal client and Fedora server configuration with Ansible.

## Setup

```sh
./install.sh
source .venv/bin/activate
ansible-playbook playbooks/client.yml -K
ansible-playbook playbooks/server.yml -K
```

Bootstrap uses Python 3.13 for the controller. No configuration is applied by bootstrap.
Development and AI tools follow `latest` releases without version pins.
The root [mise.toml](mise.toml) also declares shared development tools for working
in this repository; install them locally with `mise install`.
Git uses supplied `git_user_name`/`git_user_email`, then existing global identity,
then prompts for missing values. Unattended Git runs must supply missing values.
Git prompts do not run for terminal, passwords, or backup selections.
SSH generation is opt-in; see [SSH](roles/base/ssh/README.md).

## Ownership and selection

- `inventory/hosts.yml`: connection details.
- `inventory/group_vars/`: shared choices and client application groups.
- `inventory/host_vars/`: canonical core paths, mounts, peer selections, and enrollment.
- `playbooks/base.yml`: shared tools; included by both profiles.
- `playbooks/client.yml`: client apps, editors, AI tools and local models.
- `playbooks/server.yml`: [server selections](server.md), Incus, Cockpit and Hermes.
- `roles/{base,client,server}/`: tasks and native configuration owned by each tool.
- `playbooks/tasks/{base,client,server}/`: simple package lists and task groups.

Group tags are `terminal`, `dev`, `passwords`, `network`, `containers`, `sync`,
`apps`, and `backup`. Individual tags include `git`, `ssh`, `zsh`, `starship`,
`tmux`, `vim`, `fastfetch`, `mise`, `node`, `deno`, `yarn`, `lazygit`, `gh`,
`pass-cli`, `tailscale`, `podman`, `syncthing`, `restic`, `rclone`, `incus`, `cockpit`,
`hermes`, `neovim`, `zed`, `ai-tools`, `ollama`, and client app groups.
Selecting a tool includes its setup prerequisites. The `base` tag selects all
shared tools; `client` and `server` select their respective complete profiles.

```sh
ansible-playbook playbooks/base.yml --limit xs-ea --tags terminal -K
ansible-playbook playbooks/client.yml --tags browser -K
ansible-playbook playbooks/server.yml --tags hermes -K
ansible-playbook playbooks/server.yml --tags backup -K
ansible-playbook playbooks/site.yml --list-tasks --tags git
```

`roles.yml` remains a compatibility entrypoint to `site.yml`.
Shell history, private keys, credentials and account sessions remain local.
Changing profile selections does not uninstall old applications.

## Enrollment

Run `gh auth login`, `tailscale up`, and `pass-cli login` as the target user.
[Secrets](docs/secrets.md) documents controller-side injection.
[Syncthing](roles/base/syncthing/README.md) explains mutual enrollment, per-device
modes and the external-drive mount guard.
[Backups](docs/backups.md) documents two independent repositories and restore tests.
Restic and rclone belong only to the server profile; clients sync core to the
server with Syncthing and do not install or configure backup tools.
Timers default to disabled. Existing enrolled backups require explicit migration.

Hermes writes to `~/serve/apps/hermes` and stores persistent data in
`~/storage/hermes/data`; [maintenance](roles/server/hermes/README.md) is explicit.
Control lifecycle separately:

```sh
ansible-playbook playbooks/control.yml -e control_action=status
ansible-playbook playbooks/control.yml -e control_action=up -e control_app=hermes
```

`control_app=all` includes existing app directories, including old deployments.

## Local validation

```sh
python -m unittest discover tests/
```

Tests assume a compatible Ansible controller environment (Python 3.13, Ansible
collections installed). They run `--syntax-check` on `site.yml` and `control.yml`
and verify that tags only pull in the expected roles.

Additional manual checks:

```sh
ANSIBLE_LOCAL_TEMP=/tmp/ansible-local TMPDIR=/tmp ansible-playbook --syntax-check playbooks/site.yml
ANSIBLE_LOCAL_TEMP=/tmp/ansible-local TMPDIR=/tmp ansible-playbook --syntax-check playbooks/control.yml
ansible-lint playbooks/site.yml playbooks/control.yml
```

See [implementation verification](docs/role-redesign-verification.md) for fixture checks
and live checks that have not been performed.
