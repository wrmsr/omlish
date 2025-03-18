# ruff: noqa: UP006 UP007
# @omlish-lite
"""
This bypasses debuggers attaching to spawned subprocess children that look like python processes. See:

  https://github.com/JetBrains/intellij-community/blob/e9d8f126c286acf9df3ff272f440b305bf2ff585/python/helpers/pydev/_pydev_bundle/pydev_monkey.py
"""
import shlex
import typing as ta

from ..lite.runtime import is_debugger_attached


##


_SUBPROCESS_SHELL_WRAP_EXECS = False


def subprocess_shell_wrap_exec(*cmd: str) -> ta.Tuple[str, ...]:
    return ('sh', '-c', ' '.join(map(shlex.quote, cmd)))


def subprocess_maybe_shell_wrap_exec(*cmd: str) -> ta.Tuple[str, ...]:
    if _SUBPROCESS_SHELL_WRAP_EXECS or is_debugger_attached():
        return subprocess_shell_wrap_exec(*cmd)
    else:
        return cmd
