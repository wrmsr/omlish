import sys
import typing as ta

from omlish import check
from omlish import lang


with lang.auto_proxy_import(globals()):
    from omlish.subprocesses import editor
    from omlish.subprocesses import sync as sync_subprocesses


##


class SyncStringInput(ta.Protocol):
    def __call__(self) -> str: ...


class InputSyncStringInput:
    DEFAULT_PROMPT: ta.ClassVar[str] = '> '

    def __init__(
            self,
            prompt: str | None = None,
            *,
            use_readline: bool | ta.Literal['auto'] = False,
    ) -> None:
        super().__init__()

        if prompt is None:
            prompt = self.DEFAULT_PROMPT
        self._prompt = prompt
        self._use_readline = use_readline

        self._handled_readline = False

    def _handle_readline(self) -> None:
        if self._handled_readline:
            return
        self._handled_readline = True

        if not self._use_readline:
            return

        if self._use_readline == 'auto':
            if not sys.stdin.isatty():
                return

        try:
            import readline  # noqa
        except ImportError:
            pass

    def __call__(self) -> str:
        self._handle_readline()
        return input(self._prompt)


class FileSyncStringInput(InputSyncStringInput):
    def __init__(self, path: str) -> None:
        super().__init__()

        self._path = check.non_empty_str(path)

    def __call__(self) -> str:
        with open(self._path) as f:
            return f.read()


class UserEditorSyncStringInput(InputSyncStringInput):
    def __call__(self) -> str:
        if (ec := editor.edit_text_with_user_editor('', sync_subprocesses.subprocesses)) is None:
            raise EOFError
        return ec
