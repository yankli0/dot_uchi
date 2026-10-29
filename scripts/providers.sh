#!/usr/bin/env bash
# scripts/providers.sh — dispatch layer (Adapter pattern) for secret sources.
#
# The repo never calls the password manager directly. Every consumer sources
# this file and uses:
#     secrets_check          exit 0 when the active backend is usable
#     secrets_resolve <ref>  prints the value for "<vault>/<item>/<field>"
#
# The active adapter selects itself via DOTFILES_SECRETS_PROVIDER (default:
# pass-cli) and lives in scripts/providers/<name>.sh, defining:
#     <name>_check                       exit 0 when the backend is usable
#     <name>_resolve <pass-ref>          resolve one ref, print the value
# Swapping the source of secrets later = adding a new adapter file and flipping
# the env var. Refs (and secrets.list) never mention the backend.

set -euo pipefail

DOTFILES_SECRETS_PROVIDER="${DOTFILES_SECRETS_PROVIDER:-pass-cli}"

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ADAPTER="$HERE/providers/${DOTFILES_SECRETS_PROVIDER}.sh"
if [[ ! -f "$ADAPTER" ]]; then
    echo "error: unknown secrets provider '${DOTFILES_SECRETS_PROVIDER}' (missing ${ADAPTER})" >&2
    exit 1
fi

# Guard against double-source (idempotent).
[[ -n "${DOTFILES_SECRETS_PROVIDER_ACTIVE:-}" && "$DOTFILES_SECRETS_PROVIDER_ACTIVE" == "$DOTFILES_SECRETS_PROVIDER" ]] && return 0 2>/dev/null || true

# shellcheck source=/dev/null
source "$ADAPTER"
DOTFILES_SECRETS_PROVIDER_ACTIVE="$DOTFILES_SECRETS_PROVIDER"

_check_name="${DOTFILES_SECRETS_PROVIDER}_check"
_resolve_name="${DOTFILES_SECRETS_PROVIDER}_resolve"

secrets_check() { "$_check_name"; }
secrets_resolve() { "$_resolve_name" "$1"; }
