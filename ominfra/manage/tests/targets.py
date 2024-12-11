# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import enum
import typing as ta


##


class ManageTarget(abc.ABC):  # noqa
    pass


##


@dc.dataclass(frozen=True)
class SshManageTarget(ManageTarget):
    host: str
    username: ta.Optional[str] = None
    key_file: ta.Optional[str] = None


##


class DockerManageTarget(ManageTarget, abc.ABC):  # noqa
    pass


@dc.dataclass(frozen=True)
class DockerRunManageTarget(DockerManageTarget):
    image: ta.Optional[str] = None


@dc.dataclass(frozen=True)
class DockerExecManageTarget(DockerManageTarget):
    container_id: ta.Optional[str] = None


##


@dc.dataclass(frozen=True)
class LocalManageTarget:
    class Mode(enum.Enum):
        DIRECT = enum.auto()
        SUBPROCESS = enum.auto()
        IN_PROCESS = enum.auto()

    mode: Mode = Mode.DIRECT


##


ManageTargetConnector = ta.Callable[[ManageTarget], ta.AsyncContextManager[CommandExecutor]]  # ta.TypeAlias
