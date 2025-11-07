# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
  - git var GIT_EDITOR ?
"""
import dataclasses as dc
import os
import tempfile
import typing as ta

from ..lite.cached import cached_nullary
from ..lite.contextmanagers import ExitStacked
from ..lite.contextmanagers import defer
from .run import SubprocessRun
from .run import SubprocessRunnable
from .run import SubprocessRunOutput


##


DEFAULT_USER_TEXT_EDITOR = 'vi'


def get_user_text_editor(default: ta.Optional[str] = None) -> str:
    if default is None:
        default = DEFAULT_USER_TEXT_EDITOR
    return os.environ.get('EDITOR', default)


##


class EditTextWithUserEditor(SubprocessRunnable[ta.Optional[str]], ExitStacked):
    def __init__(self, initial_text: str = '') -> None:
        super().__init__()

        self._initial_text = initial_text

    @dc.dataclass(frozen=True)
    class _TempFile:
        path: str
        before_mtime: float

    @cached_nullary
    def _temp_file(self) -> _TempFile:
        with tempfile.NamedTemporaryFile(
                mode='r+',
                delete=False,
        ) as ntf:
            ntf.write(self._initial_text)
            ntf.flush()
            before_mtime = os.stat(ntf.name).st_mtime

        self._enter_context(defer(os.unlink, ntf.name))  # noqa

        return EditTextWithUserEditor._TempFile(
            ntf.name,
            before_mtime,
        )

    def make_run(self) -> SubprocessRun:
        tf = self._temp_file()
        ed = get_user_text_editor()

        return SubprocessRun.of(
            ed,
            tf.path,
        )

    def handle_run_output(self, output: SubprocessRunOutput) -> ta.Optional[str]:
        tf = self._temp_file()

        if output.returncode != 0:
            return None

        after_mtime = os.stat(tf.path).st_mtime

        if after_mtime == tf.before_mtime:
            # No changes made; assuming cancel.
            return None

        with open(tf.path) as f:
            content = f.read().strip()
            if not content:
                # Empty file; assuming cancel.
                return None

        return content


def edit_text_with_user_editor(
        initial_text: str = '',
        subprocesses: ta.Optional[ta.Any] = None,  # AbstractSubprocesses
) -> ta.Optional[str]:
    with EditTextWithUserEditor(initial_text) as cmd:
        return cmd.run(subprocesses)


##


if __name__ == '__main__':
    def _main() -> None:
        text = edit_text_with_user_editor('# Write your message here.\n')
        if text is not None:
            print('User submitted:\n', text)
        else:
            print('Operation canceled.')

    _main()
