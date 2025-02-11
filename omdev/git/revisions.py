# ruff: noqa: UP006 UP007
# @omlish-lite
import os.path
import subprocess
import typing as ta

from omlish.subprocesses.sync import subprocesses
from omlish.subprocesses.wrap import subprocess_maybe_shell_wrap_exec


def get_git_revision(
        *,
        cwd: ta.Optional[str] = None,
) -> ta.Optional[str]:
    subprocesses.check_output('git', '--version')

    if cwd is None:
        cwd = os.getcwd()

    if subprocess.run(  # noqa
            subprocess_maybe_shell_wrap_exec(
                'git',
                'rev-parse',
                '--is-inside-work-tree',
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
    ).returncode:
        return None

    has_untracked = bool(subprocesses.check_output(
        'git',
        'ls-files',
        '.',
        '--exclude-standard',
        '--others',
        cwd=cwd,
    ).decode().strip())

    dirty_rev = subprocesses.check_output(
        'git',
        'describe',
        '--match=NeVeRmAtCh',
        '--always',
        '--abbrev=40',
        '--dirty',
        cwd=cwd,
    ).decode().strip()

    return dirty_rev + ('-untracked' if has_untracked else '')
