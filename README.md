# dot_uchi — Ansible-managed client machines

Declarative config for the personal clients (Fedora + COSMIC): system base,
shell, apps, editor, per-host themes and shell layout. Old-archived flavor
lives under `archive/` (not maintained).

## Machines

| Host | Theme | Shell layout |
| --- | --- | --- |
| `brisingamen` | catppuccin mocha/rosewater + wallpaper | bottom panel, autohide, glass on |
| `gleipnir` | gruvbox dark/green + wallpaper | left edge-flush square panel, no autohide |

Per-host config lives entirely in `inventory/host_vars/<host>.yml` (the canonical
knob doc); group defaults in `inventory/group_vars/all.yml` + `client.yml`. Each machine gets its own independent playbook — no shared profile.

## Commands

Run your host's playbook (system packages need sudo on first run or after
changes):

```sh
ansible-playbook playbooks/<host>.yml --ask-become-pass
```

Only theme/shell/editor (no sudo needed):

```sh
ansible-playbook playbooks/<host>.yml --tags cosmic,editors
```

Everything else:

```sh
yamllint ... ; ansible-lint              # repo style gates
ansible-playbook playbooks/<host>.yml --syntax-check
pytest -q tests/                          # structural validation
```

## Adding a host

1. `inventory/hosts.yml` — add the host (plain or `ansible_connection: local`).
2. `inventory/host_vars/<host>.yml` — every knob (theme_name/flavour/accent,
   wallpaper, fonts_install_list, ai_tools_extra, …) gets its documented lines;
   view brisingamen's file as the reference.
3. `playbooks/<host>.yml` — copy the existing playbook body, change `hosts:`.
4. Theme assets — pick assets from `assets/themes/<name>/cosmic/` (per
   flavour + accent), or add a new theme via
   `assets/themes/<name>/accents.yml` (+ `theme_ron_template`) and cosmic .ron
   files; the Zed mapping then lives in `roles/dev/zed/defaults` (`zed_themes`).
5. Shell snapshot — `assets/cosmic-shell/<host>/` (capture from the machine;
   see that directory's README) or remove the cosmic_shell import until you do.

## Refresh cycle for themes and shell snapshots

- COSMIC UI changes: tweak in the UI for testing; the next playbook run
  restores the repo snapshot. Permanent changes: update the snapshot under
  `assets/cosmic-shell/<host>/` first (see its README), then run.
- Catppuccin palettes: re-fetch `.ron` files from the pinned upstream commit
  (see `assets/themes/catppuccin/cosmic/README.md`), then run the playbook.
