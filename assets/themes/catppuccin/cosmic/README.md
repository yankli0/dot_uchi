# COSMIC theme files — provenance

Fetched from the official Catppuccin port for COSMIC Desktop:
- **Source:** https://github.com/catppuccin/cosmic-desktop (path `themes/cosmic-settings/`)
- **Pinned commit:** `95e81098042d` (main @ 2026-10-28)
- **Files:** all four flavours (latte, frappe, macchiato, mocha) x 14 accents,
  56 files, each `catppuccin-<flavour>-<accent>+round.ron` (rounded corners).

## Local modifications (what changed vs upstream)

- `catppuccin-mocha-rosewater+round.ron`: `is_frosted: false` → `true`
  (frosted-glass surfaces explicitly on for the catppuccin client host;
  tracked here because every future re-fetch must re-apply it).
- No other files differ from upstream at this commit.
