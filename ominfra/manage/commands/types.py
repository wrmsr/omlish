# ruff: noqa: UP006 UP007
import typing as ta


CommandExecutorMap = ta.NewType('CommandExecutorMap', ta.Mapping[ta.Type[Command], CommandExecutor])

