# flatpak

- Installs chosen user apps from Flathub with package/remote prerequisites.
- Select app groups: `browser`, `communication`, `notes`, `3d-modeling`, or `apps`.
- The `flatpak` tool tag applies all four configured app groups.
- Lists live in `inventory/group_vars/client.yml`; `flatpak_packages` is the role input.
- Empty lists do nothing; existing apps are preserved.
- App account enrollment is explicit; no ports opened by this role.
