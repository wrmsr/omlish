"""
TODO:
 - ```
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
   ```
"""
import traceback

from .. import lang


##


DEBUG = __debug__


def get_resource_debug() -> bool:
    return DEBUG


def set_resource_debug(debug: bool) -> None:
    global DEBUG
    DEBUG = debug


##


class _ResourcesDebug(lang.Abstract):
    def __init__(self) -> None:
        super().__init__()

        self.__debug = DEBUG
        if self.__debug:
            self.__traceback = traceback.format_stack()[:-1]

    def _init_debug(self) -> None:
        if self.__debug:
            self.__repr = repr(self)
