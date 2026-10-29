#!/usr/bin/env bash
# scripts/vault-pass.sh — print the Ansible vault password (adaptive source).
#
# Resolution order (first match wins):
#   1. DOTFILES_VAULT_PASSWORD env var (CI, one-off runs)
#   2. the active secrets provider adapter (scripts/providers.sh; default
#      provider pass-cli → item "Dotfiles/ansible-vault", field "password")
# The provider is swappable without touching this script.
#
# Used as ansible.cfg vault_password_file (a script path is allowed there).

set -euo pipefail

if [[ -n "${DOTFILES_VAULT_PASSWORD:-}" ]]; then
    printf '%s\n' "$DOTFILES_VAULT_PASSWORD"
    exit 0
fi

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=providers.sh
source "$HERE/providers.sh"

REF="${DOTFILES_VAULT_PASS_REF:-Dotfiles/ansible-vault/password}"

secrets_resolve "$REF"
