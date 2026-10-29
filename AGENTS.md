# AGENTS.md — working conventions for this repository

Guidance for AI agents and humans editing dotfiles (Ansible-managed Fedora +
COSMIC client machines). Read `README.md` for what the repo is; this file is
how to work in it safely.

## Golden rules

1. **Never print, log, or commit secret values** — tokens, API keys, passwords
   in chat output, commit messages, test output, error reports, or files.
2. **The active secrets provider is the single source of truth for secrets**
   (Proton Pass via pass-cli today; swappable — see "How secrets flow"). Never
   invent a secret and never hand-edit a secret value anywhere in the repo. If
   a secret is missing or wrong, tell the user to fix it in the provider.
3. **`src/inventory/group_vars/all/vault.yml` is a generated cache.** Encrypted
   with Ansible Vault, gitignored. Never edit it by hand; rebuild with
   `mise run refresh-secrets` after `secrets.list` or the provider changed.
4. **Use `mise` tasks, not raw commands**, when a task exists (`mise run`…).
5. **Dry-run first.** `mise run check <host>` before `mise run apply[_to]`.
6. **Ask before touching anything shared.** `gleipnir` is the sandbox/test
   target; `brisingamen` is the daily machine.
7. **Never hardcode a specific secrets provider** into roles, scripts or docs.
   Value flow goes through the adapter layer (`scripts/providers/`); provider
   names appear only in the adapter file itself, in `ssh_agent_provider`
   (host opt-in), and in docs as "the active provider (X today)".

## How secrets flow

```
provider (pass-cli today) ──(scripts/providers/<name>.sh adapter)──▶ scripts/sync-secrets.sh
                                                                        │
                                                                        ▼
                                              src/inventory/group_vars/all/vault.yml
                                              (encrypted cache, gitignored, generated)
                                                                        │
                                                        roles consume role-prefixed aliases
                                                                        ▼
                                                      templates/tasks use {{ zed_* }} etc.
```

- The provider is an **adapter** (`scripts/providers/<name>.sh`, selected by
  `DOTFILES_SECRETS_PROVIDER`, default `pass-cli`): `<name>_check` verifies the
  backend, `<name>_resolve <ref>` prints one value. Adding a provider = one
  file; consumers never call a provider tool directly. `ssh_agent`
  (empty = GNOME Keyring default, else a provider id) picks a *template*,
  not the secrets source — SSH keys stay where each provider keeps them.
- `secrets.list` (`<VAR>  <vault>/<item>/<field>`) holds no values and is
  committed. `<HOST>_<NAME>` = machine-scoped; bare `<NAME>` = account-wide
  (e.g. `WAKATIME_API_KEY` — one wakatime key for all machines, each reports
  its machine identity automatically).
- The Ansible Vault password is resolved at run time by
  `scripts/vault-pass.sh` (wired in `src/ansible.cfg`): first
  `DOTFILES_VAULT_PASSWORD` (env, CI), then the active provider; it never sits
  in a file. Never place a `.vault-pass` file anywhere.
- Roles consume aliases declared in `host_vars/<host>/vars.yml`
  (`zed_wakatime_api_key`, `mise_env_secrets`); they must never reference
  `HOST_`-prefixed cache names or provider refs directly.
- Tasks handling secret values get `no_log: true`; files receiving them get
  `mode: "0600"`. CI never needs the cache: aliases degrade to empty.

### Adding a secret

1. Ask the user to create the item/field in the provider (vault `Dotfiles`).
2. Add a line to `secrets.list`: `MY_NEW_TOKEN  Dotfiles/my-service/token`.
3. Run `mise run refresh-secrets`; verify with `--check --diff`.
4. Consume `{{ MY_NEW_TOKEN }}` in the role via a role-prefixed alias; keep
   `no_log: true` on the consuming task.

### Switching the provider later

1. Write `scripts/providers/<new>.sh` implementing `<new>_check` and
   `<new>_resolve` (translate the `<vault>/<item>/<field>` refs).
2. `DOTFILES_SECRETS_PROVIDER=<new> mise run refresh-secrets`.
3. If the new provider has an SSH agent: add
   `roles/base/ssh_agent/templates/<new>.service.j2` and set
   `ssh_agent: <new>` in host vars. Nothing else changes.

## Working rules

1. **Everything applied lives under `src/`; user dotfiles live in `chezmoi/`;**
   machinery lives under `ansible/` and `scripts/`; `tests/` stay out of the
   applied tree. Ansible owns system provisioning, chezmoi owns `$HOME` files.
2. **One `site.yml` serves every host.** Per-host config lives in
   `host_vars/<host>/vars.yml`; shared data in `group_vars/` per area
   (packages, tools, editors). Selective runs via `--tags`.
3. **Explicit opt-in everywhere.** Selection lists (`client_apps`,
   `ai_tools_extra`, `zed_extensions`) default empty;
   empty means install nothing. `ssh_agent` defaults empty (GNOME Keyring);
   setting a provider id switches the agent. Never fall back to default sets.
4. **Idempotency is a hard requirement.** Tasks must report changed only on
   real change (`changed_when`, marker files, `creates:`). A task that flips
   "changed" on a clean second run is a bug — gate it, don't tolerate it.
5. **Pinned + checksummed downloads** in role catalogs (fonts, zed, ai-tools).
   Deliberate exceptions live with an explanatory comment (e.g. pass-cli
   installs current via Proton's installer by user decision).
6. **One concern per role; prerequisites in `meta/main.yml`**, not ad-hoc
   imports or tag chains.
7. **Roles and templates depend only on declared vars** — never on naming
   inference or hardcoded paths (`user_home`, `user_config_dir`, `user_bin_dir`,
   `assets_dir` come from `inventory/group_vars/all/vars.yml`).

## Common edits

- **New host knob:** group var in `src/inventory/group_vars/<area>.yml`
  (commented) → set per-host in `src/inventory/host_vars/<host>/vars.yml` →
  consumed in role tasks/templates.
- **New secret:** see "Adding a secret" above.
- **New host:** README "Adding a host" (inventory → vars.yml → secrets.list →
  site.yml tags → theme assets → shell snapshot).
- **COSMIC UI change:** refresh the snapshot under
  `src/assets/cosmic-shell/<host>/` first, then run the playbook.

## SSH

- Private keys live with their owner: GNOME Keyring holds local keys by
  default; hosts with keys in the provider set `ssh_agent: pass-cli` and the
  `ssh_agent` role deploys that unit instead. The role writes an
  `environment.d` drop-in pointing the session at the active agent socket
  (keyring: `$XDG_RUNTIME_DIR/keyring/ssh`; pass-cli:
  `~/.ssh/pass-cli-agent.sock`).
  Verify with `ssh-add -L`; `mise run ssh-agent` inspects the unit.
- Do not add `ansible_ssh_private_key_file` settings; Ansible uses the agent.
- The public key is safe to commit and gets installed on hosts idempotently
  (`authorized_key`). Reinstall "host key changed" fixes with
  `ssh-keygen -R <host>` — tell the user before running it.
- If the provider CLI reports an auth error, ask the user to log in
  (`pass-cli login` for the current provider).

## Validation gates (run before claiming done)

From repo root with the repo venv on PATH (mise provides it automatically):

```sh
cd src && yamllint assets inventory roles site.yml ../ansible ../chezmoi
cd src && ansible-lint
cd src && ansible-playbook site.yml --syntax-check
pytest -q tests/
```

When touching config-deploying roles, also run
`mise run check <host> --tags <area>` and read the diff. A run is only done
when all gates pass — no lint skips in lieu of real fixes; per-line
`# noqa` only when no Ansible idiom can satisfy the rule.

## Callback output

`ansible/callback_plugins/role_tree.py` renders PLAYS/roles, one plain ASCII
marker per task (`[=]` ok, `[+]` changed, `[-]` skipped, `[!]` failed,
`[?]` unreachable), per-task timers `[x.xs]`, and a plain per-host RECAP. No
numbering, no colors; add markers via `_MARKERS` if adding a status. Keep it
dependency-free (stdlib only).

## Context maintenance

When a change alters structure or conventions (layout, secrets, roles, task
runner, output), update `README.md` (what + how) and this file (how to work)
in the same change.
