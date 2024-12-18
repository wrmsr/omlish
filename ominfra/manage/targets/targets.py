# ruff: noqa: UP006 UP007
"""
It's desugaring. Subprocess and locals are only leafs. Retain an origin?
** TWO LAYERS ** - ManageTarget is user-facing, ConnectorTarget is bound, internal
"""
import abc
import dataclasses as dc
import enum
import typing as ta

from omlish.lite.check import check


##


class ManageTarget(abc.ABC):  # noqa
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.state(cls.__name__.endswith('ManageTarget'))


#


@dc.dataclass(frozen=True)
class PythonRemoteManageTarget:
    DEFAULT_PYTHON: ta.ClassVar[ta.Optional[ta.Sequence[str]]] = None
    python: ta.Optional[ta.Sequence[str]] = DEFAULT_PYTHON

    def __post_init__(self) -> None:
        check.not_isinstance(self.python, str)


#


class RemoteManageTarget(ManageTarget, abc.ABC):
    pass


class PhysicallyRemoteManageTarget(RemoteManageTarget, abc.ABC):
    pass


class LocalManageTarget(ManageTarget, abc.ABC):
    pass


##


@dc.dataclass(frozen=True)
class SshManageTarget(PhysicallyRemoteManageTarget, PythonRemoteManageTarget):
    host: ta.Optional[str] = None
    username: ta.Optional[str] = None
    key_file: ta.Optional[str] = None

    def __post_init__(self) -> None:
        check.non_empty_str(self.host)


##


@dc.dataclass(frozen=True)
class DockerManageTarget(RemoteManageTarget, PythonRemoteManageTarget):  # noqa
    image: ta.Optional[str] = None
    container_id: ta.Optional[str] = None

    def __post_init__(self) -> None:
        check.arg(bool(self.image) ^ bool(self.container_id))


##


@dc.dataclass(frozen=True)
class InProcessManageTarget(LocalManageTarget):
    class Mode(enum.Enum):
        DIRECT = enum.auto()
        FAKE_REMOTE = enum.auto()

    mode: Mode = Mode.DIRECT


@dc.dataclass(frozen=True)
class SubprocessManageTarget(LocalManageTarget, PythonRemoteManageTarget):
    pass
