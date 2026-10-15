# Secrets and enrollment

Read this when changing credentials, account authorization or controller-side injection.

Proton Pass CLI is shared, but login/enrollment is explicit on each endpoint.
Deployment secrets may be injected into the Ansible controller session; validate
required credentials only when their consuming tool is selected.
Suppress secret-bearing task output and use private generated files.
Preserve stored credentials when replacement inputs are absent.

Syncthing device IDs and SSH public keys are shareable identifiers.
Private keys, API keys, GUI credentials and provider tokens are secrets.
Keep them out of tracked inventory, context files and synchronized terminal configuration.
SSH private keys are not automatically registered or synchronized.

Server unattended Restic jobs use separate private local password files.
Rclone authorization lives in a private local configuration file.
Document recovery copies of passwords, repository URIs and rclone credentials in
Proton Pass; unattended services must not depend on an interactive Pass login.

An installed CLI does not prove authentication or secret retrieval works.
Only claim live authenticated retrieval after testing an authorized session.
For exact injection examples and recovery guidance, read
[secrets](../docs/secrets.md) and [backups](../docs/backups.md).
