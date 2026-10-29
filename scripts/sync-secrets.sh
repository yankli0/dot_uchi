#!/usr/bin/env bash
# scripts/sync-secrets.sh — build the encrypted Ansible secrets cache.
#
# Usage: scripts/sync-secrets.sh [--refresh]
#
# Reads secrets.list (<VAR> <vault>/<item>/<field>), resolves every reference
# through the secrets provider adapter (scripts/providers.sh; default:
# pass-cli), and encrypts the result into
# src/inventory/group_vars/all/vault.yml. The cache is a generated artifact:
# never edit, never commit.
#
# Requires: the active provider backend usable (pass-cli + `pass-cli login`
# by default) and the cache password item in Proton Pass.

set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/secrets.list"
CACHE="$ROOT/src/inventory/group_vars/all/vault.yml"

# shellcheck source=providers.sh
source "$ROOT/scripts/providers.sh"

refresh=0
for arg in "$@"; do
    case "$arg" in
        --refresh) refresh=1 ;;
        *) echo "unknown argument: $arg" >&2; exit 2 ;;
    esac
done

if (( !refresh )) && [[ -s "$CACHE" ]]; then
    echo "[sync-secrets] encrypted cache already present; use --refresh to rebuild"
    exit 0
fi

secrets_check || {
    echo "error: secrets provider '${DOTFILES_SECRETS_PROVIDER}' not usable (install/login missing?)" >&2
    exit 1
}
[[ -r "$MANIFEST" ]] || { echo "error: secrets.list missing" >&2; exit 1; }
command -v ansible-vault >/dev/null || { echo "error: ansible-vault not found" >&2; exit 1; }

mkdir -p "$(dirname "$CACHE")"
tmp="$(mktemp "${CACHE%.yml}.XXXXXX")"
trap 'rm -f "$tmp"' EXIT
plain="$tmp"
chmod 600 "$plain"

count=0
while IFS=' ' read -r var ref; do
    [[ -n "$var" && "$var" != \#* ]] || continue
    # Ref syntax: <vault>/<item>/<field>; names may contain spaces (e.g.
    # the field "API Key"), '/' separates the three components.
    ifs="$IFS"; IFS=/; parts=($ref); IFS="$ifs"
    if (( ${#parts[@]} != 3 )); then
        echo "error: secrets.list entry '$var' must have <vault>/<item>/<field>" >&2
        exit 1
    fi
    value="$(secrets_resolve "$ref")"
    if [[ -z "$value" ]]; then
        echo "error: '$ref' resolved empty for \$${var}" >&2
        exit 1
    fi
    printf '%s: %s\n' "$var" "$value" >> "$plain"
    count=$((count + 1))
done < "$MANIFEST"

if (( count == 0 )); then
    echo "error: secrets.list defines no secrets" >&2
    exit 1
fi

# The cache password comes from the provider too (scripts/vault-pass.sh, wired
# in src/ansible.cfg).
ansible-vault encrypt --vault-password-file "$ROOT/scripts/vault-pass.sh" "$plain" >/dev/null
mv "$plain" "$CACHE"
chmod 600 "$CACHE"
echo "[sync-secrets] cached ${count} secrets into ${CACHE#"$ROOT"/}"
