import traceback
import typing as ta
import warnings

from ... import check
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

    #

    @property
    def _closed(self) -> bool:
        return self.__closed

    def _close(self, reason: BaseException | None) -> None:
        pass

    @ta.final
    def _close_internal(self, reason: BaseException | None) -> None:
        try:
            self._close(reason)
        finally:
            self.__closed = True

    @ta.final
    def close(self) -> None:
        self._close_internal(None)

    #

    @property
    def _is_resourceless(self) -> bool:
        return False

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
    """
    IMPORTANT: Subclasses must not raise exceptions in constructors or resources will be leaked (given the intended
               usage ergonomics). Do any validation in `_enter`.
    """

    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__(*args, **kwargs)

        self.__entered = False

    @ta.final
    def __enter__(self) -> ta.Self:
        check.state(not self.__entered)
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
            except Exception as e:  # noqa
                self.close()
                raise

    @ta.final
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_internal(exc_val)
