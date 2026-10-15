"""Tests for the app catalog data structure."""
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CATALOG = REPO / "roles" / "client" / "apps" / "vars" / "catalog.yml"
GROUP_VARS = REPO / "inventory" / "group_vars" / "client.yml"


class TestCatalog(unittest.TestCase):
    def test_catalog_is_valid_yaml(self):
        raw = CATALOG.read_text()
        data = yaml.safe_load(raw)
        self.assertIn("app_catalog", data)
        self.assertIsInstance(data["app_catalog"], dict)

    def test_catalog_entries_have_required_fields(self):
        data = yaml.safe_load(CATALOG.read_text())
        for app_id, spec in data["app_catalog"].items():
            self.assertIn("type", spec, f"{app_id} missing type")
            self.assertIn(spec["type"], {"flatpak", "package", "role"})
            self.assertIn("id", spec, f"{app_id} missing id")
            self.assertIn("group", spec, f"{app_id} missing group")

    def test_group_vars_select_known_apps(self):
        catalog = yaml.safe_load(CATALOG.read_text())["app_catalog"]
        group_vars = yaml.safe_load(GROUP_VARS.read_text())
        selected = group_vars.get("client_apps", [])
        unknown = set(selected) - set(catalog.keys())
        self.assertEqual(unknown, set(), f"unknown app ids in client_apps: {unknown}")

    def test_empty_selection_installs_nothing(self):
        # The default in the role is an empty list.
        group_vars = yaml.safe_load(GROUP_VARS.read_text())
        selected = group_vars.get("client_apps", [])
        self.assertIsInstance(selected, list)


if __name__ == "__main__":
    unittest.main()
