import abc
import enum
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True, eq=False, order=False)
class Permission(lang.Final):
    name: str

    def __post_init__(self) -> None:
        check.non_empty_str(self.name)
        check.equal(self.name, self.name.lower())


class PermissionNamespaceMeta(lang.GenericNamespaceMeta[Permission], check_values=Permission, case_insensitive=True):
    pass


class StandardPermissions(metaclass=PermissionNamespaceMeta):
    READ = Permission('read')
    WRITE = Permission('write')
    EXECUTE = Permission('execute')


@lang.static_init
def _check_standard_permission_names() -> None:
    for n, p in StandardPermissions:
        check.equal(n.lower(), p.name)


class PermissionState(enum.Enum):
    DENIED = enum.auto()
    CONFIRM = enum.auto()
    ALLOWED = enum.auto()


##


class Permissions(lang.Abstract):
    @abc.abstractmethod
    def get_permission_states(self) -> ta.Mapping[Permission, PermissionState]:
        raise NotImplementedError

    def get_permission_state(self, permission: Permission) -> PermissionState:
        return self.get_permission_states().get(permission, PermissionState.DENIED)

    @abc.abstractmethod
    def set_permission_state(self, permission: Permission, state: PermissionState) -> None:
        raise NotImplementedError


##


class DictPermissions(Permissions):
    def __init__(self) -> None:
        super().__init__()

        self._dct: dict[Permission, PermissionState] = {
            p: PermissionState.DENIED
            for _, p in StandardPermissions
        }

    def get_permission_states(self) -> ta.Mapping[Permission, PermissionState]:
        return self._dct

    def set_permission_state(self, permission: Permission, state: PermissionState) -> None:
        self._dct[permission] = state
