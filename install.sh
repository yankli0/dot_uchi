#!/usr/bin/env bash
set -euo pipefail

# Colors
BOLD='\033[1m'
CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RESET='\033[0m'

info() { echo -e "${CYAN}[INFO]${RESET} $*"; }
success() { echo -e "${GREEN}[OK]${RESET} $*"; }
warn() { echo -e "${YELLOW}[WARN]${RESET} $*"; }

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_VERSION=3.13

echo -e "${BOLD}dot-uchi installer${RESET}"
echo "────────────────────────────────────────"
echo

# ── mise ──────────────────────────────────────────────────────────────────────
if command -v mise >/dev/null 2>&1; then
  mise_cmd="$(command -v mise)"
  success "mise found at ${mise_cmd}"
else
  info "Installing mise..."
  curl -fsSL https://mise.run | sh
  mise_cmd="$HOME/.local/bin/mise"
  success "mise installed"
fi

# ── Python environment ────────────────────────────────────────────────────────
info "Setting up Python ${PYTHON_VERSION} environment..."
"$mise_cmd" install "python@${PYTHON_VERSION}" >/dev/null
"$mise_cmd" exec "python@${PYTHON_VERSION}" -- python -m venv "$repo_dir/.venv"
"$repo_dir/.venv/bin/python" -m pip install --upgrade pip >/dev/null
"$repo_dir/.venv/bin/python" -m pip install ansible ansible-lint yamllint >/dev/null
success "Python venv and dependencies installed"

# ── Ansible collections ────────────────────────────────────────────────────────
info "Installing Ansible collections..."
"$repo_dir/.venv/bin/ansible-galaxy" collection install -r "$repo_dir/requirements.yml" >/dev/null
success "Ansible collections installed"

# ── Ansible fact cache ─────────────────────────────────────────────────────────
install -d -m 0700 "$repo_dir/.ansible/facts"
success "Fact cache prepared"

echo
echo -e "${BOLD}Installation complete!${RESET}"
echo "────────────────────────────────────────"
echo
echo -e "${BOLD}Next steps:${RESET}"
echo -e "  ${CYAN}1.${RESET} Activate the environment:"
echo -e "     source ${repo_dir}/.venv/bin/activate"
echo
echo -e "  ${CYAN}2.${RESET} Run the playbook for your host:"
for playbook in "$repo_dir"/playbooks/*.yml; do
  host="$(basename "$playbook" .yml)"
  echo -e "     ansible-playbook playbooks/$(basename "$playbook")   # host: ${host}"
done
echo
echo -e "${CYAN}Tip:${RESET} Per-host configuration lives in inventory/host_vars/;"
for host_vars in "$repo_dir"/inventory/host_vars/*.yml; do
  echo -e "     $(basename "$host_vars")"
done
echo
