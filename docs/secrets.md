# Shared secrets with Proton Pass

The base profile installs `pass-cli` on both machines. Log in as the normal user
with `pass-cli login`. For headless key storage, follow Proton's
[configuration guide](https://protonpass.github.io/pass-cli/get-started/configuration/).

Use a secret reference to retrieve a field when needed:

```sh
pass-cli item view 'pass://Servers/Some item/password'
```

For automation, prefer
[environment injection](https://protonpass.github.io/pass-cli/commands/contents/run/).
The shell contains references, and Pass resolves them for the child command:

```sh
export HERMES_DASHBOARD_BASIC_AUTH_USERNAME='pass://Servers/Hermes/username'
export HERMES_DASHBOARD_BASIC_AUTH_PASSWORD='pass://Servers/Hermes/password'
export HERMES_DASHBOARD_BASIC_AUTH_SECRET='pass://Servers/Hermes/session-secret'
pass-cli run -- ansible-playbook playbooks/server.yml --tags hermes
```

Replace vault/item names with your own. Run this on the Ansible controller, which
renders Hermes's environment. Add `-K` if sudo requires a password. The generated
Compose file on the server is private, and its task does not print secret values.

Restic's unattended jobs use separate private `~/.config/restic/core.password`
and `apps.password` files rather than an interactive Pass session.
Keep recovery copies of both passwords, repository URIs, and rclone configuration
in Proton Pass. Rclone authorization stays in the normal user's private
`~/.config/rclone/rclone.conf` (0600).
See [independent backup enrollment and restore](backups.md).

Secret validation runs only when its consuming tool is selected. Git and SSH
inputs can be passed through a temporary private vars file; never put secrets in
tracked inventory or shell command arguments. Generated Compose/environment files
are 0600 and secret-bearing Ansible tasks suppress output.
The examples follow [Pass CLI environment injection](https://protonpass.github.io/pass-cli/commands/contents/run/);
authenticated retrieval has not been verified in an authorized live session.
