# incus

- Installs Incus, starts its service, and adds the user to `incus-admin`.
- Select with `incus` or `containers`; includes Tailscale and server firewall prerequisites.
- No common defaults; storage/network choices remain part of explicit enrollment.
- Adds the root subuid/subgid range from `server.md` only if existing mappings are compatible.
- HTTPS: 8443 TCP on the Tailscale address, configured after Tailscale login.
- An existing `incusbr0` is trusted through firewalld, with Incus bridge filtering disabled.

Choose storage/network settings interactively with `incus admin init`, then rerun
`ansible-playbook playbooks/server.yml --tags incus`. Log out/in for group membership.
Use `incus config trust add laptop` for client enrollment. Install `incus-client`
on the client if needed; tokens are not stored in this repository.
