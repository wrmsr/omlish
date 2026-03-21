import abc

from omlish import lang

from ..content import Content


##


class UnsupportedMarkdownError(Exception):
    def __init__(self, token_type: str, message: str | None = None) -> None:
        if message is not None:
            full = f'Unsupported markdown token: {token_type!r}: {message}'
        else:
            full = f'Unsupported markdown token: {token_type!r}'
        super().__init__(full)

        self.token_type = token_type


##


class ContentParser(lang.Abstract):
    @abc.abstractmethod
    def parse(self, src: str) -> Content:
        raise NotImplementedError
