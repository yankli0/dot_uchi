# syncthing

- Select with `syncthing` or `sync`; validates core before installing/configuring.
- Folder `wekzg-5dp7t` uses each host's `core_path`.
- First run with `syncthing_peers: []` reports the local ID for enrollment.
- Define IDs once in `inventory/group_vars/all.yml` as `syncthing_device_ids`,
  keyed by inventory host name. `syncthing_folder_members` declares core membership.
- In host vars, set `syncthing_peers` to the other enrolled host names.
  Missing/duplicate IDs are rejected. Pair both endpoints for mutual sharing.
- `syncthing_folder_type` defaults to `sendreceive`; each endpoint can explicitly
  choose `sendonly` or `receiveonly`.
- Preserves unmanaged peers/folders/shares. Configuration success does not prove
  connectivity or completed synchronization; inspect the GUI when peers are online.
- Transfer ports: 22000 TCP/UDP. GUI: localhost 8384 TCP.
  Local discovery may use 21027 UDP; no public GUI firewall rule is created.
- Client external-drive mount is checked before any replacement directory can be created.

Example host variables after both IDs have been recorded:

```yaml
# xs-ea
syncthing_peers: [gmk-de]
syncthing_folder_type: sendreceive
# gmk-de uses syncthing_peers: [xs-ea]
```
