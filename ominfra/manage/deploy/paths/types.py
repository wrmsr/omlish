# ruff: noqa: UP006 UP007
import typing as ta


DeployPathKind = ta.Literal['dir', 'file']  # ta.TypeAlias

DeployPathPlaceholderMap = ta.Mapping['DeployPathPlaceholder', str]  # ta.TypeAlias


##


DeployPathPlaceholder = ta.NewType('DeployPathPlaceholder', str)
