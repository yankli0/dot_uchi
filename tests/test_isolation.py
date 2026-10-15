"""Isolation checks: a tag should only pull in its own roles."""
import os
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _list_tasks(playbook: str, tag: str) -> str:
    env = os.environ.copy()
    env["ANSIBLE_LOCAL_TEMP"] = "/tmp/ansible-local"
    env["TMPDIR"] = "/tmp"
    result = subprocess.run(
        ["ansible-playbook", "--list-tasks", "--tags", tag, f"playbooks/{playbook}.yml"],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"--list-tasks --tags {tag} {playbook}.yml failed:\n"
            f"{result.stdout}\n{result.stderr}"
        )
    return result.stdout


class TestIsolation(unittest.TestCase):
    def test_git_only_pulls_base_roles(self):
        output = _list_tasks("site", "git")
        # base/git is the primary target; its prerequisite base/system also runs.
        self.assertIn("base/git", output)
        # Server/client-only roles should not appear.
        for role in ("server/hermes", "server/incus", "server/restic",
                     "client/neovim", "client/zed", "client/ai-tools", "client/ollama"):
            self.assertNotIn(role, output, f"unexpected role {role} for --tags git")

    def test_browser_only_pulls_client_app_roles(self):
        output = _list_tasks("site", "browser")
        # The browser task should run, and the system prerequisite with it.
        self.assertIn("browser", output.lower())
        # No server roles should appear.
        for role in ("server/hermes", "server/incus", "server/restic", "server/system"):
            self.assertNotIn(role, output, f"unexpected role {role} for --tags browser")

    def test_hermes_only_pulls_server_roles(self):
        output = _list_tasks("site", "hermes")
        self.assertIn("server/hermes", output)
        # Client-only roles should not appear.
        for role in ("client/neovim", "client/zed", "client/ai-tools", "client/ollama"):
            self.assertNotIn(role, output, f"unexpected role {role} for --tags hermes")


if __name__ == "__main__":
    unittest.main()
