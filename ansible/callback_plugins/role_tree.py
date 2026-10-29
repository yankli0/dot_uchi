# Role-tree callback: role-grouped output with status markers and timers
# Copyright (c) 2026

from __future__ import annotations

import time

DOCUMENTATION = r"""
name: role_tree
type: stdout
short_description: Role-grouped task list with status markers, per-task timers
description:
  - Groups tasks under their role name.
  - Each task renders one line with a plain ASCII status marker (ok / changed /
    skipped / failed / unreachable), the task name, and its duration.
  - Ends with a per-host recap.
requirements:
  - set as stdout in configuration (stdout_callback = role_tree)
"""

from ansible.plugins.callback import CallbackBase

_MARKERS = {
    "ok": "=",
    "changed": "+",
    "skipped": "-",
    "failed": "!",
    "unreachable": "?",
}


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "stdout"
    CALLBACK_NAME = "role_tree"
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._play = None
        self._last_role = None
        self._task_started = {}  # task uuid -> monotonic start time
        self._task_names = {}    # task uuid -> display name

    # ── play lifecycle ───────────────────────────────────────────────────────

    def v2_playbook_on_play_start(self, play):
        self._play = play
        self._last_role = None
        self._display.display("PLAY: " + str(play.get_name() or ""))
        self._display.display("")

    # ── task start: remember timing, open role group ─────────────────────────

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._track_task(task)

    def v2_playbook_on_handler_task_start(self, task):
        self._track_task(task)

    def _group(self, role):
        if role != self._last_role:
            if self._last_role is not None:
                self._display.display("")
            self._display.display(role)
            self._last_role = role

    def _track_task(self, task):
        uuid = task._uuid
        self._task_started[uuid] = time.monotonic()
        self._task_names[uuid] = task.get_name()
        self._group(self._role_of(task))

    # ── results: render the task line for real ───────────────────────────────

    def v2_runner_on_ok(self, result):
        self._emit(result, "changed" if result._result.get("changed") else "ok")

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if ignore_errors:
            self._emit(result, "ok")
        else:
            self._emit(result, "failed", result._result.get("msg"))

    def v2_runner_on_unreachable(self, result):
        self._emit(result, "unreachable", result._result.get("msg"))

    def v2_runner_on_skipped(self, result):
        self._emit(result, "skipped")

    def _emit(self, result, status: str, error: str | None = None):
        uuid = result._task._uuid
        if uuid not in self._task_started:
            # Result for a task whose start event we did not see (e.g. include
            # short-circuits): open the role group first, duration unknown.
            self._group(self._role_of(result._task))
        started = self._task_started.pop(uuid, None)
        duration = time.monotonic() - started if started is not None else None
        name = self._task_names.pop(uuid, result._task.get_name())
        line = f"  [{_MARKERS[status]}] {name}"
        if duration is not None:
            line += f"  [{duration:.1f}s]"
        self._display.display(line)
        if error:
            first_line = str(error).splitlines()[0]
            self._display.display("      " + first_line)

    # ── recap ─────────────────────────────────────────────────────────────────

    def v2_playbook_on_stats(self, stats):
        self._display.display("")
        self._display.display("RECAP")
        for host in sorted(stats.processed.keys()):
            s = stats.summarize(host)
            self._display.display(
                f"  {host}: "
                f"ok={s['ok']} changed={s['changed']} "
                f"failed={s['failures']} unreachable={s['unreachable']} "
                f"skipped={s['skipped']}"
            )

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _role_of(task) -> str:
        try:
            role = getattr(task, "_role", None)
            if role is not None and role.get_name():
                return role.get_name()
            path = task.get_path()
            if "/roles/" in path:
                return path.split("/roles/")[1].split("/")[0]
        except Exception:
            pass
        return "standalone"
