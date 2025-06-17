# ruff: noqa: UP006 UP007 UP045
import typing as ta

from .base import Command
from .base import CommandExecutor


CommandExecutorMap = ta.NewType('CommandExecutorMap', ta.Mapping[ta.Type[Command], CommandExecutor])
