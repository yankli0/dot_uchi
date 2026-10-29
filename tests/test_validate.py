"""Structural validation of the dot_uchi repository.

Pure-file checks, no Ansible execution: they guard the systematic invariants
that the roles rely on and run in CI.
"""

from __future__ import annotations

import re
import subprocess
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PLAYBOOKS = SRC / "playbooks"
SITE = SRC / "site.yml"
ROLES = SRC / "roles"
GROUP_VARS = SRC / "inventory" / "group_vars"
ALL_VARS = GROUP_VARS / "all"
LEAF_DIRS = (
    ROLES / "base",
    ROLES / "client",
    ROLES / "cosmic",
    ROLES / "dev",
    ROLES / "generic",
)
ASSETS = SRC / "assets"
HOST_VARS = SRC / "inventory" / "host_vars"

ROLE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def _load_yaml(path: Path):
    return yaml.safe_load(path.read_text())


def _referenced_roles() -> set[str]:
    roles = set()
    for playbook in list(PLAYBOOKS.glob("*.yml")) + ([SITE] if SITE.is_file() else []):
        text = playbook.read_text()
        for match in re.finditer(r"name:\s*([a-z_0-9]+)\s*$", text, re.MULTILINE):
            roles.add(match.group(1))
    return roles


def _existing_role_names() -> set[str]:
    roles = set()
    for leaf in LEAF_DIRS:
        if not leaf.is_dir():
            continue
        for child in leaf.iterdir():
            if child.is_dir():
                roles.add(child.name)
    return roles


def _host_vars(name: str) -> dict:
    return _load_yaml(HOST_VARS / name / "vars.yml")


def _host_dir() -> list[Path]:
    """Per-host subdirectories of inventory/host_vars/."""
    return sorted(d for d in HOST_VARS.iterdir() if d.is_dir())


def test_secrets_manifest_and_cache_setup():
    """Proton Pass flow: secrets.list drives the generated encrypted cache."""
    manifest = ROOT / "secrets.list"
    assert manifest.is_file(), "secrets.list (the secrets manifest) must exist"
    refs = 0
    for line in manifest.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        var, _, ref = line.partition(" ")
        ref = ref.strip()
        assert var.isupper(), f"secret var must be UPPER_SNAKE_CASE: {var}"
        # Ref names may contain spaces (e.g. field "API Key"); separate by '/'.
        assert len(ref.split("/")) == 3 and all(ref.split("/")), (
            f"ref must be <vault>/<item>/<field>: {ref!r}"
        )
        refs += 1
    assert refs > 0, "secrets.list defines no secrets"

    cache = SRC / "inventory/group_vars/all/vault.yml"
    if cache.is_file():
        assert cache.read_text().startswith("$ANSIBLE_VAULT;"), (
            "cache must be ansible-vault encrypted ($ANSIBLE_VAULT header)"
        )
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", str(cache)], cwd=ROOT
        )
        assert ignored.returncode == 0, "the secrets cache must be gitignored"


def test_roles_use_valid_names():
    for role in _existing_role_names():
        assert ROLE_NAME_PATTERN.match(role), f"Invalid role name: {role}"


def test_playbooks_import_existing_roles():
    known = _existing_role_names()
    missing = _referenced_roles() - known
    assert not missing, f"Playbooks reference unknown roles: {sorted(missing)}"


def test_group_vars_selection_lists_are_known_subsets():
    apps_catalog = _load_yaml(ALL_VARS / "ai.yml")["apps_catalog"]
    client_apps = _load_yaml(SRC / "inventory/group_vars/client.yml")["client_apps"]
    unknown = set(client_apps) - set(apps_catalog)
    assert not unknown, f"client_apps references unknown ids: {unknown}"

    font_catalog = _load_yaml(ALL_VARS / "ai.yml")["fonts_catalog"]
    zed_catalog = _load_yaml(ALL_VARS / "editors.yml")["zed_extension_catalog"]

    for host_dir in _host_dir():
        data = _host_vars(host_dir.name)
        assert set(data.get("fonts_install_list", [])) <= set(font_catalog), (
            f"{host_dir.name}: fonts_install_list references unknown fonts"
        )
        assert set(data.get("zed_extensions", [])) <= set(zed_catalog), (
            f"{host_dir.name}: zed_extensions references unknown extensions"
        )
        assert set(data.get("ai_tools_extra", [])) <= {
            "command_code_cli",
            "command_code_desktop",
        }, f"{host_dir.name}: ai_tools_extra has unknown entries"
        assert data.get("ssh_agent", "") in {
            "",
            "pass-cli",
        }, f"{host_dir.name}: ssh_agent must be empty (Keyring) or a provider id"


def _theme_file_pattern(theme: str) -> str:
    """Compiled-theme file-name template from the theme's own metadata."""
    return _load_yaml(ASSETS / "themes" / theme / "accents.yml")["theme_ron_template"]


def test_host_theme_files_exist():
    for host_dir in _host_dir():
        data = _host_vars(host_dir.name)
        template = _theme_file_pattern(data["theme_name"])
        ron = ASSETS / "themes" / data["theme_name"] / "cosmic" / template.format(
            flavour=data["theme_flavour"], accent=data["theme_accent"]
        )
        assert ron.is_file(), f"{host.name} theme missing: {ron}"


def test_every_theme_accent_has_a_ron_file():
    for theme_dir in (ASSETS / "themes").iterdir():
        if not theme_dir.is_dir():
            continue
        pattern = _theme_file_pattern(theme_dir.name)
        if "{flavour}" in pattern:
            # Pattern like "<name>-{flavour}-<...>": flavours visible on disk.
            prefix = pattern.split("{")[0]
            flavours = {
                p.name[len(prefix) :].split("-")[0] for p in theme_dir.glob("cosmic/*.ron")
            }
        else:
            flavours = [""]
        for accent in _load_yaml(theme_dir / "accents.yml")["accents"]:
            for flavour in flavours:
                ron = theme_dir / "cosmic" / pattern.format(flavour=flavour, accent=accent)
                assert ron.is_file(), f"missing ron for {flavour or '-'}/{accent}"


def test_theme_ron_core_fields_present():
    for host_dir in _host_dir():
        data = _host_vars(host_dir.name)
        template = _theme_file_pattern(data["theme_name"])
        ron = ASSETS / "themes" / data["theme_name"] / "cosmic" / template.format(
            flavour=data["theme_flavour"], accent=data["theme_accent"]
        )
        text = ron.read_text()
        for field in ("corner_radii", "is_frosted", "window_hint", "active_hint", "palette:"):
            assert field in text, f"{ron} missing required field: {field}"


def test_every_provisioned_url_catalog_has_https_entries():
    # Fonts and AI tool installers must reference real URLs for the checksummed
    # download pipeline.
    tools = _load_yaml(ALL_VARS / "ai.yml")
    fonts = tools["fonts_catalog"]
    for _font_key, spec in fonts.items():
        assert spec["url"].startswith("https://")
        assert spec["checksum"].startswith("sha256:")

    ai_tools = tools["ai_tools_catalog"]
    for _tool_key, spec in ai_tools.items():
        assert spec["url"].startswith("https://")
        assert spec["bin"]

    zed_meta = _load_yaml(ALL_VARS / "editors.yml")
    catalog = zed_meta["zed_extension_catalog"]
    for _key, spec in catalog.items():
        assert spec["url"].startswith("https://")
        assert spec["checksum"].startswith("sha256:")
        assert spec["dir"]

    for theme, mapping in zed_meta["zed_themes"].items():
        assert mapping["modes"]
        names = mapping["names"] if "names" in mapping else (
            mapping["asset"] and mapping["asset"]["flavour_names"])
        assert names and set(mapping["modes"]) == set(names), (
            f"zed_themes[{theme}]: modes/names keys must match (per flavour)"
        )
        assert set(mapping["extensions"]) <= set(catalog), (
            f"zed_themes[{theme}]: unknown extension ids"
        )
        if "catppuccin-icons" in mapping["extensions"]:
            assert set(mapping.get("icon_names", {})) == set(mapping["modes"]), (
                f"zed_themes[{theme}]: icon_names must cover every flavour"
            )
        asset = mapping.get("asset")
        if asset is not None:
            assert "{accent}" in asset["url"] and set(asset["checksums"])
            accents = _load_yaml(ASSETS / "themes" / theme / "accents.yml")["accents"]
            missing = set(accents) - set(asset["checksums"])
            assert not missing, f"zed_themes[{theme}].asset unpinned accents: {missing}"


def test_provenance_docs_exist_for_theme_assets():
    for theme_dir in (ASSETS / "themes").iterdir():
        cosmic = theme_dir / "cosmic"
        if cosmic.is_dir():
            assert (cosmic / "README.md").is_file(), (
                f"{cosmic} needs a provenance README (source + local changes)"
            )
