import traceback

from omlish import lang


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
