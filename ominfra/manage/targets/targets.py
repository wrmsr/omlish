# ruff: noqa: UP006 UP007
"""
It's desugaring. Subprocess and locals are only leafs. Retain an origin?
** TWO LAYERS ** - ManageTarget is user-facing, ConnectorTarget is bound, internal
"""
import abc
import dataclasses as dc
import enum
import typing as ta


##


class ManageTarget(abc.ABC):  # noqa
    pass


#


@dc.dataclass(frozen=True)
class PythonRemoteManageTarget:
    DEFAULT_PYTHON: ta.ClassVar[str] = 'python3'
    python: str = DEFAULT_PYTHON


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


##


@dc.dataclass(frozen=True)
class DockerManageTarget(RemoteManageTarget, PythonRemoteManageTarget, abc.ABC):  # noqa
    image: ta.Optional[str] = None
    container_id: ta.Optional[str] = None


##


class InProcessConnectorTarget(LocalManageTarget):
    class Mode(enum.Enum):
        DIRECT = enum.auto()
        FAKE_REMOTE = enum.auto()

    mode: Mode = Mode.DIRECT


@dc.dataclass(frozen=True)
class SubprocessManageTarget(LocalManageTarget, PythonRemoteManageTarget):
    pass
