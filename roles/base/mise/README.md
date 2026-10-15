# mise

- Installs user mise and current development tools; system Python stays unchanged.
- Select all with `mise`/`dev`, or individual `node`, `deno`, `yarn`, `lazygit`, `gh`.
  Yarn and client AI/editor setup include Node as a prerequisite.
- `mise_tools` uses `latest` for each tool; managed configuration lives in
  `~/.config/mise/conf.d/dot-uchi.toml`, preserving other native files.
- Zsh activates mise; unattended commands may use `mise exec -- <command>`.
- Enrollment: `gh auth login` explicitly. No listening ports.
