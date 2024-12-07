# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta

from omlish.lite import marshal as msh
from omlish.lite.json import json_dumps_pretty


##


@dc.dataclass(frozen=True)
class DeployPathPart(abc.ABC):  # noqa
    pass


@dc.dataclass(frozen=True)
class ConstDeployPathPart(DeployPathPart, abc.ABC):
    n: str


class DeployConstDir(ConstDeployPathPart):
    pass


class DeployConstFile(ConstDeployPathPart):
    pass


class DeploySpecDir(DeployPathPart):
    pass


class DeploySpecFile(DeployPathPart):
    pass


@dc.dataclass(frozen=True)
class DeployPath:
    ps: ta.Sequence[DeployPathPart]


##


def test_marshal():
    dp = DeployPath([
        DeployConstDir('logs'),
        DeploySpecDir(),
    ])

    print(json_dumps_pretty(msh.marshal_obj(dp)))
