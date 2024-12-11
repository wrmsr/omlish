# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
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


class LocalManageTarget(abc.ABC):  # noqa
    pass


class DirectLocal(LocalManageTarget):
    pass


class SubprocessLocalManageTarget(LocalManageTarget):
    pass


class InProcessLocalManageTarget(LocalManageTarget):
    pass
