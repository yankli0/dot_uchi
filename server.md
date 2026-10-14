# E: fix subuid and subgid

```sh
echo 'root:1000000:1000000000' | sudo tee -a /etc/subuid
echo 'root:1000000:1000000000' | sudo tee -a /etc/subgid
```

# E: fix time

```sh
sudo timedatectl set-timezone Europe/Warsaw

sudo systemctl enable --now chronyd
sudo timedatectl set-ntp true
sudo chronyc makestep
```

# Base packages & cli's

```sh
sudo dnf -y install nano vim git curl wget
```

## Github CLI

```sh
sudo dnf install dnf5-plugins
sudo dnf config-manager addrepo --from-repofile=https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install gh

gh auth login
```

## Taiscale

```sh
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

sudo firewall-cmd --permanent --zone=trusted --add-interface=tailscale0
sudo firewall-cmd --reload
```

## Pass CLI

```sh
curl -fsSL https://proton.me/download/pass-cli/install.sh | bash
pass-cli login
```

# Apps

```bash
sudo dnf install -y podman-compose
mkdir storage
```

## Incus

```sh
sudo dnf -y install incus
sudo systemctl enable --now incus.service
sudo usermod -aG incus-admin "$USER"
newgrp incus-admin

incus admin init

incus config set core.https_address "$(tailscale ip -4):8443"
```

### Client

```
sudo dnf -y install incus-client
```

```
incus config trust add laptop

incus remote add server https://100.x.x.x (tailscale ip -4) \
  --token '<TOKEN>' \
  --accept-certificate

incus network set incusbr0 ipv4.firewall false
incus network set incusbr0 ipv6.firewall false

sudo firewall-cmd --zone=trusted --change-interface=incusbr0 --permanent

sudo firewall-cmd --reload
```

# Toolbx

```bash
sudo dnf install toolbox
```

# Drive setup

```
mkdir core

sudo dnf install syncthing
systemctl --user enable --now syncthing
sudo loginctl enable-linger $USER

sudo firewall-cmd --permanent --add-port=22000/tcp
sudo firewall-cmd --permanent --add-port=22000/udp
sudo firewall-cmd --reload

syncthing cli config devices add \
  --device-id <CLIENT_DEVICE_ID> \
  --name laptop

syncthing cli config folders add \
  --id wekzg-5dp7t \
  --label core \
  --path ~/core

syncthing cli config folders <SYNC_FOLDER_ID> devices add \
  --device-id <CLIENT_DEVICE_ID>
```2

# Hermes setup

```bash
mkdir storage/hermes

podman compose \
  -f "$HOME/containers/hermes/docker-compose.yml" \
  up -d

podman compose \
  -f "$HOME/containers/hermes/docker-compose.yml" \
  exec hermes hermes setup

sudo firewall-cmd \
  --zone=FedoraServer \
  --permanent \
  --add-port=9119/tcp

sudo firewall-cmd --reload
```

# Cocpit setup



## Cockipt apps

```sh
sudo dnf -y install cockpit-podman
sudo dnf -y install cockpit-files
```

# Google Drive backups with rclone and restic (Fedora Server)

Run these commands in Bash on the server over SSH, as the same normal user throughout. This example backs up `~/core`; change the source path if needed. Restic creates encrypted, versioned backups and uses rclone to store them in Google Drive.

## Install

```bash
sudo dnf install -y rclone restic
sudo dnf upgrade -y rclone restic
rclone version
restic version
```

## Connect Google Drive over SSH

On the server:

```bash
rclone config
```

Choose the following (select options by their labels; menu numbers can change):

- New remote: `n`; name: `gdrive`.
- Storage: `drive` (Google Drive).
- Client ID and secret: leave blank to use rclone's defaults.
- Scope: `drive.file` (files created by rclone), sufficient for a new backup repository. Use full `drive` scope only if you also need access to existing Drive files.
- Service account file: leave blank.
- Advanced configuration: `n`.
- Use a web browser to authenticate automatically: `n`, because this is an SSH session.

Leave that prompt open. On your own computer, install rclone using the [official installation instructions](https://rclone.org/install/), preferably the same version as the server. Run the exact `rclone authorize ...` command printed by the server in a local terminal. Complete Google login in your local browser, then paste the returned authorization token into the server's `config_token` prompt. Treat this token as a password; do not paste it into notes or chat.

For an ordinary personal Drive, answer `n` to Shared Drive and confirm/save the remote. Exit configuration with `q`.

```bash
rclone lsd gdrive:
rclone config file
```

The first command should finish without an authentication error; an empty listing is normal with `drive.file` scope. The second shows where rclone keeps its credentials. Keep this configuration private. Do not add a configuration encryption password for the unattended setup below unless you also configure automatic unlocking.

See [rclone headless authorization](https://rclone.org/remote_setup/) and [Google Drive configuration](https://rclone.org/drive/).

## Create the encrypted backup repository

Use a unique Drive folder per server. Replace `fedora-server` below if appropriate, and keep that repository name stable.

```bash
install -d -m 700 "$HOME/.config/restic"
nano "$HOME/.config/restic/password"
```

Enter a strong, unique password on one line, save and exit. Keep another copy in your password manager: losing it makes the backups unrecoverable. For an existing repository, use its existing password instead.

```bash
chmod 600 "$HOME/.config/restic/password"
cat > "$HOME/.config/restic/env" <<'EOF'
export RESTIC_REPOSITORY='rclone:gdrive:Backups/fedora-server'
export RESTIC_PASSWORD_FILE="$HOME/.config/restic/password"
EOF
chmod 600 "$HOME/.config/restic/env"
source "$HOME/.config/restic/env"
restic init
```

Run `restic init` only once for a new repository. Restic connects directly through rclone; no Drive mount is required. See [restic repository configuration](https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html#other-services-via-rclone).

## First backup and restore test

```bash
source "$HOME/.config/restic/env"
restic backup "$HOME/core"
restic snapshots
restic check
```

Confirm the backup finishes successfully. Permission errors mean some files were not backed up; select paths readable by this account or configure a separate privileged backup. For databases and running containers, create application-consistent dumps or exports first and include those in the backup.

Test recovery into a fresh temporary directory (allow enough disk space for the restored snapshot):

```bash
restore_dir=$(mktemp -d "$HOME/restic-restore-test.XXXXXX")
restic restore latest --target "$restore_dir"
printf 'Restored files: %s\n' "$restore_dir"
```

Open restored files and compare them with the originals before relying on this backup. The restored directory contains the original path hierarchy. Remove the test copy manually when finished.

## Daily automatic backup

Create a user service using the same credentials and source as the manual backup:

```bash
mkdir -p "$HOME/.local/bin" "$HOME/.config/systemd/user"
cat > "$HOME/.local/bin/restic-backup" <<'EOF'
#!/usr/bin/bash
set -euo pipefail
source "$HOME/.config/restic/env"
/usr/bin/restic backup "$HOME/core"
EOF
chmod 700 "$HOME/.local/bin/restic-backup"

cat > "$HOME/.config/systemd/user/restic-backup.service" <<'EOF'
[Unit]
Description=Back up core to Google Drive with restic

[Service]
Type=oneshot
ExecStart=%h/.local/bin/restic-backup
UMask=0077
EOF

cat > "$HOME/.config/systemd/user/restic-backup.timer" <<'EOF'
[Unit]
Description=Daily restic backup

[Timer]
OnCalendar=*-*-* 03:00:00
RandomizedDelaySec=15m
Persistent=true

[Install]
WantedBy=timers.target
EOF

sudo loginctl enable-linger "$USER"
systemctl --user daemon-reload
systemctl --user start restic-backup.service
systemctl --user enable --now restic-backup.timer
systemctl --user list-timers restic-backup.timer
journalctl --user -u restic-backup.service -n 50 --no-pager
```

The timer runs daily around 03:00 in the server's configured timezone, including after SSH logout. `Persistent=true` catches a missed run when the timer next starts. Inspect the service log for failures; this setup does not send failure notifications or retry failed uploads immediately.

## Maintenance and retention

Periodically check the repository, including a sample of uploaded data:

```bash
source "$HOME/.config/restic/env"
restic check --read-data-subset=5%
```

All snapshots are kept by default. If you want to keep 7 daily, 4 weekly and 12 monthly snapshots, first preview the policy:

```bash
restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --dry-run
```

Only after reviewing that output, apply it and remove unreferenced backup data:

```bash
restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --prune
```

Run maintenance while the backup service is idle. Rclone normally moves deleted Google Drive files to Trash, which may continue consuming quota until permanently deleted. Review the relevant files in Drive before emptying Trash. Check available Drive storage regularly.

To stop scheduled backups:

```bash
systemctl --user disable --now restic-backup.timer
```
