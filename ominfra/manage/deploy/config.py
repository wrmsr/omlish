# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class DeployConfig:
    deploy_home: ta.Optional[str] = None
