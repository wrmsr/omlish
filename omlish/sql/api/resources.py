import traceback
import typing as ta
import warnings

from ... import lang


##


DEBUG = __debug__


def get_resource_debug() -> bool:
    return DEBUG


def set_resource_debug(debug: bool) -> None:
    global DEBUG
    DEBUG = debug


##


class UnclosedResourceWarning(Warning):
    pass


class Closer(lang.Abstract):
    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__(*args, **kwargs)

        self.__closed = False

        self.__debug = DEBUG
        if self.__debug:
            self.__repr = repr(self)
            self.__traceback = traceback.format_stack()[:-1]

    @property
    def _is_resourceless(self) -> bool:
        return False

    @ta.final
    def close(self) -> None:
        try:
            self._close()
        finally:
            self.__closed = True

    def _close(self) -> None:
        pass

    def __del__(self) -> None:
        if (
                not self._is_resourceless and
                self.__debug and
                not self.__closed
        ):
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


class ResourceNotEnteredError(Exception):
    pass


class ContextCloser(Closer):
    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__(*args, **kwargs)

        self.__entered = False

    @ta.final
    def __enter__(self) -> ta.Self:
        self.__entered = True
        self._enter()
        return self

    def _enter(self) -> None:
        pass

    def _is_entered(self) -> bool:
        return self.__entered

    def _check_entered(self) -> None:
        if not self.__entered:
            try:
                raise ResourceNotEnteredError(self)  # noqa
            except Exception:
                self.close()
                raise

    @ta.final
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
