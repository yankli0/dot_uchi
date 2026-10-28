# Guidelines: Structuring New Dotfiles in Ansible

Guidelines for adding new configuration files, tools, and applications to the
dot_uchi repository. Current clients: brisingamen and gleipnir (Fedora COSMIC
laptops, identical role set, per-host theming).

---

## 1. Repository layout

```text
inventory/
  hosts.yml            # host list (client group)
  group_vars/all.yml   # connection, derived paths, git identity, assets_dir
  group_vars/client.yml# shared app selection (client_apps)
  host_vars/<host>.yml # per-host config — CANONICAL documentation of all knobs
playbooks/
  <host>.yml           # per-host entry point; same task body per client
roles/
  base/                # host-agnostic foundations (system, zsh, mise, git, fonts, starship, tailscale, syncthing)
  client/              # generic client apps (apps, flatpak)
  cosmic/              # COSMIC desktop (cosmic_de, cosmic_term, cosmic_shell)
  dev/                 # development workspace (env, ai_tools, zed)
assets/
  themes/<name>/       # palettes (accents.yml) + cosmic .ron files
  wallpapers/<host>/   # per-host wallpapers
```

Import roles by leaf name (`import_role: name: fonts`) — `ansible.cfg`
roles_path points at each groups' directory. Role directories use
underscores (`cosmic_de`, `ai_tools`).

---

## 2. Where do new files go?

* **Universal base config** (e.g. shell) — `roles/base/<role>/files/` or
  `templates/` when variable-driven.
* **Client-app config** — its own role under `roles/client/` (or extend an
  existing one); theming of each app lives in that app's role and consumes
  `theme_*` / app-specific host vars.
* **Dev tooling** — `roles/dev/`.
* **Reference data / palettes / wallpapers** — `assets/`, never deployed
  directly; roles reference them via `{{ assets_dir }}`.

---

## 3. Step-by-step workflow for adding a new dotfile

1. Create or extend a role (new role: `roles/<group>/<name>/{tasks,defaults,…}`).
2. Place static files in `files/`, variable-driven ones in `templates/*.j2`.
3. Add tasks using `ansible.builtin.{copy,template,file}` targeting
   `{{ user_home }}` / `{{ user_config_dir }}` (never absolute user paths).
4. If the tool is optional, expose an explicit selection list in role defaults
   (`<name>_selected` default `[]` — empty means install nothing) and list it
   in the host_vars of the hosts that want it.
5. Import the role in both `playbooks/brisingamen.yml` and
   `playbooks/gleipnir.yml` with appropriate tags.

---

## 4. Core design rules

1. **No hardcoded paths** — use `user_home`, `user_config_dir`, `user_bin_dir`,
   `assets_dir` from `inventory/group_vars/all.yml`.
2. **Idempotency** — every module must report changes only when the source
   actually differs (`changed_when`, marker files, `creates:`).
3. **Explicit opt-in** — selection lists live in `inventory/host_vars/`;
   empty list = nothing installed. Never fall back to installing a defaults set.
4. **Config is documented where it is set** — every knob a host can set is
   commented in `inventory/host_vars/<host>.yml` / `group_vars/*.yml`; role
   defaults carry short comments instead of `| default(...)` shims in tasks.
5. **Keep roles atomic** — one tool/concern per role; declare actual
   prerequisites in `meta/main.yml` (see `roles/client/apps`), not ad-hoc
   imports.
