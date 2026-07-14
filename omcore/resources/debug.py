import traceback
import typing as ta

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

        self._resources_debug = DEBUG
        if self._resources_debug:
            self._resources_debug_traceback = traceback.format_stack()[:-1]

    _resources_debug_traceback: ta.Sequence[str]

    _resources_debug_repr: str | None = None

    def _init_debug(self) -> None:
        if self._resources_debug:
            self._resources_debug_repr = repr(self)
