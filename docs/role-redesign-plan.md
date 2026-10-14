# Role redesign: review and plan

Status: proposal only. No role behavior has changed. The current configuration and
`server.md` are preserved in commit `d2edfbb` on `plan/role-groups-and-server-scope`.
Vocabulary is in [CONTEXT.md](../CONTEXT.md).

## Intended result

- The server profile follows [server.md](../server.md), with necessary system prerequisites.
- The workstation selects apps and tools by purpose: browser, communication,
  notes, 3D modeling, development, shell, and containers.
- Install mise and use it to manage development runtimes and supported development CLIs.
- Keep host choices explicit and role configuration small.

## Current usage in the repository

This review covers declared installs, playbooks, defaults, tasks, and templates.
It does not establish which programs are actually used on either machine.

| Current owner | Declared behavior | Proposed direction |
| --- | --- | --- |
| `playbooks/site.yml`, first play | Twelve roles on every host, including Node, AI CLIs, Ollama, and three editors/shell tools | Separate server and workstation selections; share only required prerequisites |
| `dot_roles/_base` | Packages, Git identity, SSH key generation, fastfetch configuration | Small system baseline; move personal Git/SSH and shell conveniences to purpose groups |
| `dot_roles/flatpak` | Chrome, Zen, Discord, Slack | Browser and communication groups; keep Flatpak as an installation mechanism |
| `dot_roles/node` | System Node; Debian NodeSource setup; global Yarn and Deno | Development tools managed by mise |
| `dot_roles/lazygit` | Build from Go using `@latest` | Supported mise backend/version; remove Go from baseline if no other consumer needs it |
| `dot_roles/ai-tools` | npm installs, architecture-specific OpenCode package, Claude installer, copied config | Development subgroup with optional AI tools; migrate supported CLIs to mise and retain justified exceptions |
| `dot_roles/ollama` | Installs and enables a system service on all hosts | Explicit workstation option; outside the server baseline |
| `server_roles` | nginx, Glance, Hermes, Open WebUI | Hermes selected for server; other services excluded from the profile |
| `install.sh` | pip installs plus Tailscale and Pass CLI | Minimal controller bootstrap; host software belongs to selected groups |

Notes and 3D modeling have no declared apps yet. Define these groups without
inventing application choices. Chrome/Zen and Discord/Slack already provide
concrete browser and communication memberships.

## Server scope

| Capability from `server.md` | Current coverage | Planned ownership |
| --- | --- | --- |
| nano, vim, git, curl, wget | `_base` supplies git/curl; `vim` supplies vim; nano/wget absent | Server baseline |
| Timezone and chronyd | No tasks | Server system setup |
| Subordinate UID/GID mappings | No tasks | Container system setup; reconcile existing mappings before applying |
| GitHub CLI | `gh` installs package; documented repository setup absent | Server CLI tools; login is enrollment |
| Tailscale and trusted interface | Installer present; interface rule absent | Network tools; connection is enrollment |
| Proton Pass CLI | Bootstrap installer only | Server CLI tools; login is enrollment |
| Podman and podman-compose | Podman present; Compose provider absent | Container tools |
| Incus, membership, network, HTTPS endpoint | No tasks | Server virtualization; initial storage/network choices and client trust are enrollment |
| Toolbx | No tasks | Container tools |
| Syncthing, `~/core`, lingering, folder/device pairing | No tasks | Sync group; device IDs supplied per host |
| Hermes | Compose and optional nginx templates exist | Server app; preserve `_control` lifecycle ownership |
| Cockpit with Podman/files extensions | No tasks | Server administration |
| rclone, restic, backup service/timer | No tasks | Backup group; authorization/password/repository initialization are enrollment |

Only the Incus client belongs on the workstation side of the client instructions.
The server keeps Incus service, network, and trust configuration.

Omit zsh, tmux, Neovim, lazygit, Node, AI CLIs, Ollama, nginx, Glance, and Open WebUI
from the server profile. Keep the system Python needed for remote Ansible execution
and other documented dependencies. Mise belongs to the workstation development
selection; installing it must not implicitly add development tools to the server.

Removing a role from a profile does not uninstall an existing package or stop an
existing service. A later migration must inventory the server and prepare a
separate, explicit retirement step. `_control` currently discovers all app directories,
so old app directories can still be targeted by `control_app=all`.

## Purpose groups and configuration

Keep `dot_roles/` and `server_roles/` initially to reduce migration churn. Introduce
purpose roles such as `apps-browser`, `apps-communication`, `apps-notes`,
`apps-3d-modeling`, `tools-dev`, `tools-shell`, and `tools-containers`. Server groups
can cover system, network, virtualization, sync, administration, and backup.
These are proposed names, not implemented roles.

A group owns its application selection and delegates complex configuration to
focused existing roles where useful. Small package-only roles can become entries
in a group. Preserve Neovim's substantial configuration rather than merging every
file into one large development role. Share installation helpers only when there
is real repeated logic.

Use static role selections in profile plays first. Avoid a new registry or generic
dispatcher. Keep `roles.yml` only if running an individual role needs a distinct
workflow; otherwise give groups and retained leaf roles accurate tags in `site.yml`.
Host targeting still requires `--limit server` or `--limit workstation`: tags alone
are not a reliable host boundary. Currently `--tags server` also selects the entire
all-host core play, and `site.yml --tags hermes` does not select the Hermes role.

Put host identity, chosen memberships, paths, and reachable ports in inventory or
group variables. Keep defaults for commonly changed selections, versions, and
service settings. Fixed package names, installer endpoints, and derived paths
usually do not need their own override variables.

## Opportunities to lighten configuration

- Move gcc and Go out of `_base`. Prefer a prebuilt lazygit installation when supported.
- `htop` and `btop` overlap: select one unless both are wanted. Fastfetch, fzf,
  ripgrep, and bat belong to optional shell tools rather than the server baseline.
- No tasks invoke Stow; Ansible copies the dotfiles. Remove it from automatic
  installation unless it has a separate personal use.
- Keep Vim as the server editor; choose workstation editors explicitly.
- The zsh file references eza and zoxide but no role installs either. Declare them
  in shell tools if wanted. Review whether Oh My Zsh is needed for the current
  simple theme and sole Git plugin before adding more shell customization.
- Replace per-tool install prefixes and npm globals with one mise-owned tool
  configuration. Avoid having Ansible and another installer own the same executable.
- Correct misleading install reporting: Node commands always report unchanged;
  several existence guards also prevent version upgrades. Decide installation and
  upgrade behavior explicitly.
- Make Flatpak installation a prerequisite where used; the current role assumes
  the executable exists. Keep browser/communication selections independent.
- Consolidate the server app root and derive compose/state paths from it. Current
  roles hard-code `~/serve`; `server.md` references `~/containers` and `~/storage`.
  Keep the existing root during the first migration, then choose paths before moving data.

## Mise plan

Ansible installs mise for the target normal user, renders selected development
tools into `~/.config/mise/config.toml`, and runs installation as that user.
Interactive shells activate mise; Ansible tasks use its absolute executable and
`mise exec` where needed so SSH tasks do not depend on shell startup files.

Move Node, Deno, Yarn, and supported development CLIs first. Add Go or a development
Python only when selected. Preserve `/usr/bin/python3` for Ansible and system tooling.
Choose maintained versions during implementation and pin exact versions or record
a lockfile; avoid making every tool float at `latest`.

Mise supports a global config and project overrides; npm-backed CLIs may still
require an explicitly declared Node runtime. Project application dependencies
stay in their project manifests. See the official [getting started guide](https://mise.jdx.dev/getting-started.html),
[configuration guide](https://mise.jdx.dev/configuration.html), and
[npm backend](https://mise.jdx.dev/dev-tools/backends/npm.html).

## Implementation sequence

1. Separate server/workstation selections and add accurate group/role tags.
   Verify the server selection against the scope table before running it.
2. Add mise and migrate the existing development installations, retaining user configs.
3. Introduce purpose groups and remove duplicated package-only configuration.
4. Implement missing server capabilities in small increments: system/network,
   containers/Incus, administration, sync, then backups. Document enrollment steps.
5. Reconcile Hermes paths and direct dashboard access without requiring nginx;
   keep compose generation separate from `_control` actions.
6. Inventory existing server services and data, then prepare retirement of extras
   and any storage moves as a separately reviewed migration.

Before those steps, resolve app choices for notes/3D modeling, desired workstation
editors and shell tools, Incus initialization choices, sync device IDs, and the
backup repository/source paths. These do not block the initial profile separation.

Validate syntax and selected tasks for both host profiles and individual group
tags. On implementation, check a second run for unintended changes, verify
installed versions and user services, and test a backup restore. Document ports
for Incus (8443), Syncthing (22000 TCP/UDP), and Hermes (9119) from `server.md`;
verify Cockpit's listener and any additional ports before adding firewall rules.
Do not mechanically reproduce append commands for subuid/subgid or repeatedly
run enrollment and repository initialization.

## Review validation

The snapshot's tracked diff is entirely line-ending changes when inspected with
`git diff --ignore-space-at-eol`; `server.md` was newly added.
The baseline syntax-check command was attempted:

```sh
ANSIBLE_LOCAL_TEMP=/tmp/ansible-local TMPDIR=/tmp ansible-playbook --syntax-check playbooks/site.yml
```

It failed before loading the playbook because the local launcher cannot import
`ansible` (`ModuleNotFoundError`). Repair the controller environment before
implementation validation. No hosts were changed during this review.
