# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from ..core import IoPipelineMetadata


##


@dc.dataclass(frozen=True)
class DriverIoPipelineMetadata(IoPipelineMetadata):
    driver: ta.Any
