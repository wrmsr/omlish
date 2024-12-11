# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta


##


class ManageTarget(abc.ABC):  # noqa
    pass


#


class RemoteManageTarget(ManageTarget, abc.ABC):
    pass


class PhysicallyRemoteManageTarget(RemoteManageTarget, abc.ABC):
    pass


##


@dc.dataclass(frozen=True)
class SshManageTarget(PhysicallyRemoteManageTarget):
    host: str
    username: ta.Optional[str] = None
    key_file: ta.Optional[str] = None


##


class DockerManageTarget(RemoteManageTarget, abc.ABC):  # noqa
    pass


@dc.dataclass(frozen=True)
class DockerRunManageTarget(DockerManageTarget):
    image: ta.Optional[str] = None


@dc.dataclass(frozen=True)
class DockerExecManageTarget(DockerManageTarget):
    container_id: ta.Optional[str] = None


##


class DirectManageTarget(ManageTarget):
    pass


class SubprocessManageTarget(ManageTarget):
    pass


class FakeRemoteManageTarget(ManageTarget):
    pass
