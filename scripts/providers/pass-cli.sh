#!/usr/bin/env bash
# pass-cli adapter (Proton Pass backend) — see scripts/providers.sh contract.

PASS_CLI="${PASS_CLI:-pass-cli}"

pass-cli_check() {
    command -v "$PASS_CLI" >/dev/null 2>&1
}

pass-cli_resolve() {
    "$PASS_CLI" item view "pass://$1"
}
