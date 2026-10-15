# client/apps

Catalog-driven optional app installation.

## Selection

Set `client_apps` in `inventory/group_vars/client.yml` to a list of app ids
from `vars/catalog.yml`:

```yaml
client_apps: [chrome, zen, discord, slack]
```

An empty list installs nothing. Unknown ids fail the run.

## Catalog

`vars/catalog.yml` maps app ids to install instructions:

- `type: flatpak` — installed via the `flatpak` role.
- `type: package` — installed via the system package manager.
- `type: role` — defers to another role (set `role:`).
- `group:` — used by the group dispatchers below.

Adding a new app is a one-line change in `vars/catalog.yml` plus adding the
id to `client_apps` if it should be selected by default.

## Group tags

The following group tags still work for installing only that category:

- `browser`
- `communication`
- `notes`
- `3d-modeling`

They are tagged with `never` so they run only when explicitly requested.
