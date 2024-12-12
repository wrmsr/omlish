# ruff: noqa: UP006 UP007
import typing as ta

from .base import Command
from .base import CommandExecutor


CommandExecutorMap = ta.NewType('CommandExecutorMap', ta.Mapping[ta.Type[Command], CommandExecutor])
