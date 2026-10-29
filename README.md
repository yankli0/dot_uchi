# dotfiles — Ansible-managed client machines

Declarative config for the personal clients (Fedora + COSMIC): system base,
shell, apps, editor, per-host themes and shell layout. Old-archived flavor
lives under `archive/` (not maintained).

## Layout

```
src/        everything Ansible applies (ansible.cfg + inventory, site.yml, roles, assets)
chezmoi/    user dotfiles owned by chezmoi (static files + .tmpl, data from Ansible)
ansible/    machinery that is not applied (callback_plugins, requirements.yml)
mise.toml   dev tooling + entry-point tasks (mise run …)
scripts/    secrets pipeline, SSH agent, vault password (Proton Pass → encrypted cache)
secrets.list  variable → Proton Pass reference manifest (no values)
tests/      structural repo validation
```

## Machines

| Host | Theme | Shell layout |
| --- | --- | --- |
| `brisingamen` | catppuccin mocha/rosewater + wallpaper | bottom panel, autohide, glass on |
| `gleipnir` | gruvbox dark/green + wallpaper | left edge-flush square panel, no autohide |

Per-host config lives entirely in `src/inventory/host_vars/<host>/vars.yml` (the
canonical knob doc; secrets alias the Proton Pass cache there); group defaults
in `src/inventory/group_vars/` (packages, tools, editors catalogs). One
`src/site.yml` entry point serves every host — no per-host playbooks.

## Running (mise tasks)

```sh
mise run check          # dry run on this machine (--check --diff)
mise run check <host>   # dry run on another machine (also remembers it)
mise run apply-to       # apply to this machine (fetches secrets, sudo prompt)
mise run use <host>     # pin the target when hostname doesn't match a host
mise run host           # show which host apply/check would target
mise run apply          # apply to every machine
mise run refresh-secrets# rebuild the encrypted secrets cache from Proton Pass
mise run ssh-agent      # inspect the SSH agent unit
```

The target host resolves as: explicit argument → remembered choice
(`~/.local/state/dotfiles-host`) → machine hostname when it matches a
managed host. So on a provisioned machine, bare `mise run apply-to` and
`mise run check` just do the right thing.

## SSH (agent only, no key files on disk)

GNOME Keyring is the default SSH agent — it ships with Fedora, needs no
extra daemon, and socket-activates at `$XDG_RUNTIME_DIR/keyring/ssh`.
The `base/ssh_agent` role enables its SSH component (a unit override adding
`ssh` to the stock `pkcs11,secrets`) and points the whole session at it via
an `environment.d` drop-in setting `SSH_AUTH_SOCK`. Hosts that keep their
keys in the secrets provider instead set `ssh_agent: pass-cli` in
`src/inventory/host_vars/<host>/vars.yml`; the role then deploys the
`templates/pass-cli.service.j2` unit (pass-cli serves the `Dotfiles` vault)
and repoints the session socket. Verify with `ssh-add -L`;
`mise run ssh-agent` inspects the unit. There is no
`ansible_ssh_private_key_file` anywhere; targets get the matching **public**
key via an idempotent `authorized_key` task. "Host key changed" reinstall
noise is fixed with `ssh-keygen -R <host>`.

Lint/test gates (tooling lives in the repo venv, put on PATH by mise):

```sh
cd src && yamllint assets inventory roles site.yml ../ansible ../chezmoi
cd src && ansible-lint
cd src && ansible-playbook site.yml --syntax-check
pytest -q tests/
```

Bootstrap a new machine: `./install.sh [--with-pass-cli]`, then `pass-cli login`,
then use the tasks above (raw `ansible-playbook` from `src/` still works).

## Secrets (provider → Ansible vault cache)

Secrets live in an external provider — Proton Pass today (via `pass-cli`),
but the pipeline is provider-agnostic: the active backend is an adapter in
`scripts/providers/<name>.sh` selected by `DOTFILES_SECRETS_PROVIDER`, so
switching sources later means adding one adapter file, not rewiring. The repo
stores no secret values — only a values-free manifest and a locally generated,
encrypted cache that Ansible consumes:

```
provider (pass-cli today) ──adapter──▶ scripts/sync-secrets.sh ──▶ src/inventory/group_vars/all/vault.yml
                                                                    (encrypted, gitignored, generated)
                                                                           │
                                                            templates and tasks use {{ VAR }}
```

- `secrets.list` maps a variable name to a provider reference
  (`<vault>/<item>/<field>` — provider-agnostic form) and is safe to commit.
  Variable naming:
  - `<HOST>_<NAME>` — machine-scoped secret, never shared between machines;
  - `<NAME>` — account-wide secret, same value on every machine (e.g.
    `WAKATIME_API_KEY`; wakatime-cli reports each machine separately anyway).
- `scripts/sync-secrets.sh [--refresh]` resolves every manifest reference
  through the adapter and writes the encrypted cache (skipped when current;
  `--refresh` rebuilds). Never edit the cache by hand; never commit it.
- `scripts/vault-pass.sh` is the Ansible Vault password source (wired as
  `vault_password_file` in `src/ansible.cfg`): it prints the password at run
  time from `DOTFILES_VAULT_PASSWORD` (env) or the active provider; the
  password never sits in a file.
- Adding a secret: create the item in the provider, add a line to
  `secrets.list`, run `mise run refresh-secrets`, then consume `{{ VAR }}` in a
  template/task. Any task handling a secret gets `no_log: true`; any file that
  receives a secret gets `mode: "0600"`.
- Role consumption: host `vars.yml` maps cache vars to role-prefixed aliases
  (`zed_wakatime_api_key`, `mise_env_secrets`); roles
  never reference `HOST_`-prefixed names directly. Empty string = unset.
- CI needs no secrets: the cache stays local, and aliases degrade to empty.

## Adding a host

1. `src/inventory/hosts.yml` — add the host (plain or `ansible_connection: local`).
2. `src/inventory/host_vars/<host>/vars.yml` — every knob (theme_name/flavour/accent,
   wallpaper, fonts_install_list, ai_tools_extra, …) gets its documented lines;
   view brisingamen's file as the reference.
3. `secrets.list` — add the machine-scoped entries (`<HOST>_<NAME>`) with
   Proton Pass refs, create the matching item, then `mise run refresh-secrets`.
4. Theme assets — pick assets from `src/assets/themes/<name>/cosmic/` (per
   flavour + accent), or add a new theme via
   `src/assets/themes/<name>/accents.yml` (+ `theme_ron_template`) and cosmic
   .ron files; the Zed mapping then lives in `src/inventory/group_vars/editors.yml`
   (`zed_themes`).
5. Shell snapshot — `src/assets/cosmic-shell/<host>/` (capture from the
   machine; see that directory's README). `site.yml` asserts the snapshot
   exists; there is no per-host playbook to edit.

## Refresh cycle for themes and shell snapshots

- COSMIC UI changes: tweak in the UI for testing; the next playbook run
  restores the repo snapshot. Permanent changes: update the snapshot under
  `src/assets/cosmic-shell/<host>/` first (see its README), then run.
- Catppuccin palettes: re-fetch `.ron` files from the pinned upstream commit
  (see `src/assets/themes/catppuccin/cosmic/README.md`), then run the playbook.
