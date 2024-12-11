# ruff: noqa: UP006 UP007
import typing as ta

from ..commands.base import CommandExecutor
from .targets import ManageTarget


##


ManageTargetConnector = ta.Callable[[ManageTarget], ta.AsyncContextManager[CommandExecutor]]  # ta.TypeAlias
