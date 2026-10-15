# Base tools

Read this when changing shared shell configuration, development runtimes, Git or SSH.

Base applies to both machine profiles. Zsh, Starship and tmux share native
configuration; Zsh is the login shell. Shell history and credentials stay local.
Starship owns its prompt configuration separately from Zsh.

Node, Deno, Yarn, lazygit and GitHub CLI are managed by
[mise](../roles/base/mise/README.md), following `latest` without version pins.
An individual tool selection installs its runtime prerequisites without installing
all unrelated development tools. Preserve other native mise configuration.
The root [mise.toml](../mise.toml) declares those tools for repository-local use;
keep its tool list aligned with the base mise defaults.
OS packages remain appropriate for Git, system prerequisites and services.
Python 3.13 in bootstrap is the Ansible controller compatibility choice.

[Git](../roles/base/git/README.md) prefers supplied public inputs
`git_user_name`/`git_user_email`, then existing identity, then interactive prompts
for missing values only. Preserve unrelated Git settings. Unattended missing
identity must fail clearly; `git_editor` remains a public override.

[SSH](../roles/base/ssh/README.md) generation defaults off. Preserve existing
private keys, use Ed25519 for requested generation, hide interactive passphrases
and require explicit secrets for unattended generation. Empty passphrases are
an explicit choice. Display the public key for manual registration.

Networking, containers, sync and Proton Pass are shared capabilities too; their
role READMEs own installation and enrollment details. Restic/rclone are server-only.
