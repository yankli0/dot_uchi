"""Syntax checks for the main playbooks."""
import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _run(args: list[str]) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["ANSIBLE_LOCAL_TEMP"] = "/tmp/ansible-local"
    env["TMPDIR"] = "/tmp"
    return subprocess.run(
        args,
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )


class TestSyntax(unittest.TestCase):
    def test_site_syntax(self):
        result = _run(["ansible-playbook", "--syntax-check", "playbooks/site.yml"])
        self.assertEqual(
            result.returncode,
            0,
            f"site.yml syntax check failed:\n{result.stdout}\n{result.stderr}",
        )

    def test_control_syntax(self):
        result = _run(["ansible-playbook", "--syntax-check", "playbooks/control.yml"])
        self.assertEqual(
            result.returncode,
            0,
            f"control.yml syntax check failed:\n{result.stdout}\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
