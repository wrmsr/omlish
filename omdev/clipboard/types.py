"""
https://askubuntu.com/questions/11925/a-command-line-clipboard-copy-and-paste-utility
"""
import abc
import dataclasses as dc

from omlish import lang


##


@dc.dataclass(frozen=True)
class ClipboardContents(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class TextClipboardContents(ClipboardContents):
    s: str


@dc.dataclass(frozen=True)
class ImageClipboardContents(ClipboardContents):
    b: bytes


##


class Clipboard(lang.Abstract):
    @abc.abstractmethod
    def get(self) -> list[ClipboardContents]:
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, c: ClipboardContents) -> None:
        raise NotImplementedError
