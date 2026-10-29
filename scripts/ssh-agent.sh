#!/usr/bin/env bash
# scripts/ssh-agent.sh — inspect the SSH agent user service(s).
#
# GNOME Keyring is the default agent (socket-activated by the desktop
# session); hosts that set `ssh_agent: <id>` in host vars use that provider's
# unit instead (e.g. pass-cli-ssh-agent.service). This script reports or
# drives one unit: DOTFILES_SSH_AGENT_UNIT selects it, defaulting to the
# keyring socket.
#
# Usage: scripts/ssh-agent.sh [start|stop|restart|status]

set -euo pipefail

UNIT="${DOTFILES_SSH_AGENT_UNIT:-gnome-keyring-daemon.socket}"
action="${1:-status}"

case "$action" in
    start)   systemctl --user start "$UNIT" ;;
    stop)    systemctl --user stop "$UNIT" ;;
    restart) systemctl --user restart "$UNIT" ;;
    status)  systemctl --user status "$UNIT" --no-pager; exit 0 ;;
    *) echo "usage: $0 [start|stop|restart|status]" >&2; exit 2 ;;
esac

systemctl --user status "$UNIT" --no-pager
