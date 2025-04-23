import traceback
import typing as ta
import warnings

from ... import lang


##


DEBUG = __debug__


def set_resource_debug(debug: bool) -> None:
    global DEBUG
    DEBUG = debug


##


class UnclosedResourceWarning(Warning):
    pass


class Closer(lang.Abstract):
    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__()

        self.__closed = False

        self.__debug = DEBUG
        if self.__debug:
            self.__repr = repr(self)
            self.__traceback = traceback.format_stack()[:-1]

    @ta.final
    def close(self) -> None:
        self.__closed = True
        self._close()

    def _close(self) -> None:
        pass

    def __del__(self) -> None:
        if self.__debug and not self.__closed:
            warnings.warn(
                f'\n\n{(sep := ("=" * 40))}\n'
                f'{self.__class__.__name__} object {self.__repr} '
                f'was not properly closed before deletion. Please ensure that `close()` is called before the object is '
                f'deleted.'
                f'\n\n'
                f'{"".join(self.__traceback).rstrip()}'
                f'\n{sep}\n',
                UnclosedResourceWarning,
            )


##


class ContextCloser(Closer):
    def __enter__(self) -> ta.Self:
        return self

    @ta.final
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
