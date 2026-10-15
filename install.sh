#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if command -v mise >/dev/null 2>&1; then
  mise_command="$(command -v mise)"
else
  curl -fsSL https://mise.run | sh
  mise_command="$HOME/.local/bin/mise"
fi

# Keep the controller on a supported Python even when Fedora's system Python is newer.
"$mise_command" install python@3.13
"$mise_command" exec python@3.13 -- python -m venv "$repo_dir/.venv"
"$repo_dir/.venv/bin/python" -m pip install --upgrade pip
"$repo_dir/.venv/bin/python" -m pip install ansible ansible-lint yamllint
"$repo_dir/.venv/bin/ansible-galaxy" collection install -r "$repo_dir/requirements.yml"

printf 'Activate Ansible: source %s/.venv/bin/activate\n' "$repo_dir"
printf 'Set up client: ansible-playbook playbooks/client.yml -K\n'
printf 'Set up server: ansible-playbook playbooks/server.yml -K\n'
