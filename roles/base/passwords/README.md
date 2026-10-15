# passwords

- Installs Proton Pass CLI for both profiles.
- Select with `passwords` or `pass-cli`; includes curl/jq prerequisites.
- Enrollment stays explicit: run `pass-cli login` as the normal user.
- [Controller injection and recovery copies](../../../docs/secrets.md).
- No common overrides or listening ports. Authenticated retrieval requires a live session.
- Uses Proton's [documented user installation directory](https://protonpass.github.io/pass-cli/get-started/installation/#custom-installation-directory).
