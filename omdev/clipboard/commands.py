import abc
import subprocess
import typing as ta

from omlish import lang

from .types import Clipboard
from .types import ClipboardContents
from .types import TextClipboardContents


##


class TextCommandClipboard(Clipboard, lang.Abstract):
    @property
    @abc.abstractmethod
    def _get_cmd(self) -> ta.Sequence[str]:
        raise NotImplementedError

    def get(self) -> list[ClipboardContents]:
        s = subprocess.check_output(self._get_cmd).decode()
        return [TextClipboardContents(s)]

    @property
    @abc.abstractmethod
    def _put_cmd(self) -> ta.Sequence[str]:
        raise NotImplementedError

    def put(self, c: ClipboardContents) -> None:
        if isinstance(c, TextClipboardContents):
            subprocess.run(self._put_cmd, input=c.s.encode(), check=True)
        else:
            raise TypeError(c)


#


class XclipLinuxClipboard(TextCommandClipboard):
    _get_cmd = ('xclip', '-selection', 'clipboard', '-o')
    _put_cmd = ('xclip', '-selection', 'clipboard')


class PbcopyDarwinClipboard(TextCommandClipboard):
    _get_cmd = ('pbpaste',)
    _put_cmd = ('pbcopy',)
