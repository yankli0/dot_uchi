# ssh

- Select with `ssh`. Generation defaults off: `ssh_generate_key: false`.
- Override `ssh_key_path` and `ssh_key_comment`; generates Ed25519 only if absent.
- Interactive generation hides the passphrase. Unattended generation must supply
  `ssh_key_passphrase` using a private vars file or controller secret injection.
  An empty passphrase must be explicitly supplied as `ssh_key_passphrase: ""`.
- Existing private keys are preserved. Public keys are displayed for manual
  registration at GitHub or another SSH service; private keys stay local.
- No SSH server is installed; no listening ports.
