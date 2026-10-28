# Per-host COSMIC shell layout snapshots

Panel and Dock configuration captured per machine and deployed by the
`cosmic_shell` role (so panel position, size, applet set, gaps and margins
survive machine-independent role logic).

## Layout

    assets/cosmic-shell/<host>/com.system76.CosmicPanel.Panel/v1/...
    assets/cosmic-shell/<host>/com.system76.CosmicPanel.Dock/v1/...

## Provenance / refresh procedure

1. On the machine, change the panel/dock in the COSMIC UI (or edit
   `~/.config/cosmic/com.system76.CosmicPanel*/v1/*`).
2. Copy the namespaces back into this repo:
   cp -r ~/.config/cosmic/com.system76.CosmicPanel.Panel assets/cosmic-shell/<host>/
   cp -r ~/.config/cosmic/com.system76.CosmicPanel.Dock assets/cosmic-shell/<host>/
3. Commit; the next playbook run converges every machine of that host.

## Current snapshots

- `brisingamen`: bottom panel (anchor `Bottom`, anchored with gap, expands to
  edges) + bottom dock — captured from the live system.
- `gleipnir`: vertical panel docked on the **left** edge (anchor `Left`) with
  **no gap to the screen edge** (`anchor_gap: false`), `margin: 0`,
  `border_radius: 0` (flush, square — no rounding), autohide `Never`
  (panel and dock never hide); bottom dock as on brisingamen. Captured from
  gleipnir's targeted state (engine-validated on a test machine); confirm/refresh
  from gleipnir's live config when you next touch the panel UI.
