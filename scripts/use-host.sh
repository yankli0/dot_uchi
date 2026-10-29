#!/usr/bin/env bash
# scripts/use-host.sh — remember which machine this repo manages.
#
# Resolution order for the target host:
#   1. explicit argument (mise run apply-to <host>) — validated, remembered;
#   2. previously remembered host (~/.local/state/dotfiles-host);
#   3. current machine name (hostname), when it matches a managed host.
#
# Usage: scripts/use-host.sh resolve [host|auto]
#        scripts/use-host.sh forget

set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}"
STATE="$STATE_DIR/dotfiles-host"

known_hosts() {
    for p in "$ROOT"/src/inventory/host_vars/*/; do basename "$p"; done | sort -u
}

valid() {
    known_hosts | grep -qx "$1"
}

current_machine() {
    hostname -s 2>/dev/null || hostname
}

remember() {
    mkdir -p "$STATE_DIR"
    printf '%s\n' "$1" > "$STATE"
    echo "[use-host] target host: $1" >&2
}

cmd="${1:-resolve}"
arg="${2:-}"

case "$cmd" in
    resolve)
        if [[ -n "$arg" && "$arg" != auto ]]; then
            valid "$arg" || {
                echo "error: unknown host '$arg' (known: $(known_hosts | tr '\n' ' '))" >&2
                exit 1
            }
            remember "$arg"
            printf '%s\n' "$arg"
            exit 0
        fi
        if [[ -s "$STATE" ]] && valid "$(cat "$STATE")"; then
            cat "$STATE"
            exit 0
        fi
        me="$(current_machine)"
        if valid "$me"; then
            remember "$me"
            printf '%s\n' "$me"
            exit 0
        fi
        echo "error: cannot determine host — '$me' is not managed and no host remembered" >&2
        echo "run: mise run apply-to <host> (known: $(known_hosts | tr '\n' ' '))" >&2
        exit 1
        ;;
    forget)
        rm -f "$STATE"
        echo "[use-host] forgot remembered host" >&2
        ;;
    *)
        echo "usage: $0 [resolve [host|auto]|forget]" >&2
        exit 2
        ;;
esac
