# git

- Applies the global Git identity for the login user (`~/.gitconfig`).
- Values come from inventory: `git_user_name`, `git_user_email`, and optional
  `git_default_branch` (default `main`).
- Set them in `inventory/group_vars/all/vars.yml`, or override per machine in
  `inventory/host_vars/<host>/vars.yml`.
- Requires `git` from `base/system`; no services or ports.
