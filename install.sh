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

echo -e "${BOLD}dotfiles installer${RESET}"
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
"$repo_dir/.venv/bin/ansible-galaxy" collection install -r "$repo_dir/ansible/requirements.yml" >/dev/null
success "Ansible collections installed"

# ── Proton Pass CLI (optional) ────────────────────────────────────────────────
# Secrets come from Proton Pass (single source of truth). Install pass-cli and
# log in, then build the encrypted cache with: mise run fetch-secrets
if command -v pass-cli >/dev/null 2>&1; then
  success "pass-cli found at $(command -v pass-cli)"
elif [[ "${1:-}" == "--with-pass-cli" ]]; then
  info "Installing Proton Pass CLI..."
  curl -fsSL https://proton.me/download/pass-cli/install.sh | bash
  success "pass-cli installed (log in with: pass-cli login)"
else
  echo -e "  ${YELLOW}--${RESET} skipping Proton Pass CLI (rerun with ${CYAN}--with-pass-cli${RESET} to install)"
fi

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
echo -e "  ${CYAN}2.${RESET} Run the playbook (from src/):"
echo -e "     mise run check        # dry run for this machine"
echo -e "     mise run apply-to     # apply to this machine"
echo
echo -e "${CYAN}Tip:${RESET} Per-host configuration lives in src/inventory/host_vars/;"
for host_vars in "$repo_dir"/src/inventory/host_vars/*/; do
  echo -e "     $(basename "$host_vars")/vars.yml"
done
echo
