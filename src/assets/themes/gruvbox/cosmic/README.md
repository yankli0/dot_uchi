# COSMIC theme files — provenance

`dark-<accent>.ron` files are **hand-crafted locally** (not fetched): values
derived from the gruvbox hex palette (bg #282828, fg #fbf1c7, …), baked as:
- square corners: `radius_*: (0.0, 0.0, 0.0, 0.0)`
- `is_frosted: false`
- **new-format schema** (`CosmicPaletteInner`: `neutral_0..10`, `accent_*`,
  `ext_*` fields) — regenerated from the old-schema file that failed
  `cosmic-settings appearance import` with "missing field `neutral_0`".
- one file per entry in `../accents.yml` (`dark-orange`, `dark-green`, …):
  each variant differs from `dark-orange` only in the UI accent roles
  (`accent`, `window_hint`), set to the accent's hex; the palette roles
  (`bright_*`, `accent_*`, `ext_*`) stay identical across variants.

Rationale for not fetching an upstream theme:
- https://github.com/Fingel/cosmic-theme-collection → `gruvbox-dark.ron`
- https://cosmic-themes.org/5/ → "Gruvbox Dark" by Morhetz

both checked on 2026-10-28: each ships a **mislabeled generic palette**
(`name: "cosmic-dark"`, non-gruvbox colors), so none is a real gruvbox port.
Re-evaluate upstream candidates when a genuine one appears.
