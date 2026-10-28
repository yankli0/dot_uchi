# Copyright (c) 2026
# Minimal role-tree callback

from __future__ import annotations

DOCUMENTATION = r"""
name: role_tree
type: stdout
short_description: Role-grouped task list output
description:
  - Groups tasks under their role name and shows task names as a list.
requirements:
  - set as stdout in configuration
"""

from ansible.plugins.callback import CallbackBase
from ansible.utils.color import stringc

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'role_tree'
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self):
        super(CallbackModule, self).__init__()
        self._play = None
        self._task_count = 0
        self._last_role = None

    def v2_playbook_on_play_start(self, play):
        self._play = play
        self._task_count = 0
        self._last_role = None
        name = play.get_name()
        self._display.display(stringc('PLAY', 'bright gray') + ': ' + name)
        self._display.display('')

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._task_count += 1
        # Try to get role name from task
        role_name = None
        try:
            if hasattr(task, '_role') and task._role is not None:
                role_name = getattr(task._role, 'get_name', lambda: None)()
            if not role_name and hasattr(task, 'get_path'):
                path = task.get_path()
                if '/roles/' in path:
                    parts = path.split('/roles/')[1].split('/')
                    if parts:
                        role_name = parts[0]
            if not role_name:
                role_name = 'standalone'
        except Exception:
            role_name = 'standalone'
        
        if role_name != self._last_role:
            self._display.display(stringc(role_name, 'cyan'))
            self._last_role = role_name
        
        task_name = task.get_name()
        self._display.display(f'  {self._task_count}. {task_name}')

    def v2_playbook_on_handler_task_start(self, task):
        self.v2_playbook_on_task_start(task, False)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if ignore_errors:
            return
        host = result._host.get_name()
        self._display.display(stringc(f'    ✗ [{host}] FAILED', 'red'))
        if result._result.get('msg'):
            msg = result._result.get('msg')
            self._display.display(f'      {msg}')

    def v2_runner_on_unreachable(self, result):
        host = result._host.get_name()
        self._display.display(stringc(f'    ⚠ [{host}] UNREACHABLE', 'bright red'))

    def v2_playbook_on_stats(self, stats):
        self._display.display('')
        self._display.display(stringc('RECAP', 'bright gray'))
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            s = stats.summarize(h)
            self._display.display(f'  {h}: ok={s["ok"]} changed={s["changed"]} failed={s["failures"]} skipped={s["skipped"]}')
