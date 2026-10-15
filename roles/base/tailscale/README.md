# tailscale

- Installs Tailscale; select with `tailscale` or `network`, also required by Incus.
- Override `tailscale_install_url` if needed.
- Enrollment: run `sudo tailscale up` explicitly on each host.
- Tailscale manages its transport; firewalld trusts the enrolled `tailscale0` interface.
- Listening transport commonly uses 41641 UDP; direct connectivity is environment-dependent.
