import abc
import enum
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang


##


class ToolPermissionState(enum.Enum):
    DENIED = enum.auto()
    CONFIRM = enum.auto()
    ALLOWED = enum.auto()


##


@dc.dataclass(frozen=True, eq=False, order=False)
class ToolPermission(lang.Final):
    name: str

    def __post_init__(self) -> None:
        check.non_empty_str(self.name)
        check.equal(self.name, self.name.lower())

        for a in ('__hash__', '__eq__', '__ne__'):
            check.is_(getattr(type(self), a), getattr(object, a))


#


class ToolPermissionNamespaceMeta(
    lang.GenericNamespaceMeta[ToolPermission],
    check_values=ToolPermission,
    case_insensitive=True,
):
    pass


##


class StandardToolPermissions(metaclass=ToolPermissionNamespaceMeta):
    READ = ToolPermission('read')
    WRITE = ToolPermission('write')
    EXECUTE = ToolPermission('execute')


@lang.static_init
def _check_standard_tool_permission_names() -> None:
    for n, p in StandardToolPermissions:
        check.equal(n.lower(), p.name)


##


class ToolPermissions(lang.Abstract):
    @abc.abstractmethod
    def get_tool_permissions(self) -> ta.Mapping[str, ToolPermission]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_tool_permission_states(self) -> ta.Mapping[ToolPermission, ToolPermissionState]:
        raise NotImplementedError

    def get_tool_permission_state(self, tp: ToolPermission) -> ToolPermissionState:
        return self.get_tool_permission_states().get(tp, ToolPermissionState.DENIED)

    @abc.abstractmethod
    def set_tool_permission_state(self, tp: ToolPermission, state: ToolPermissionState) -> None:
        raise NotImplementedError


##


class DictToolPermissions(ToolPermissions):
    def __init__(self) -> None:
        super().__init__()

        self._by_name: dict[str, ToolPermission] = {
            p.name: p
            for _, p in StandardToolPermissions
        }

        self._states: dict[ToolPermission, ToolPermissionState] = {
            p: ToolPermissionState.DENIED
            for _, p in StandardToolPermissions
        }

    def get_tool_permissions(self) -> ta.Mapping[str, ToolPermission]:
        return self._by_name

    def get_tool_permission_states(self) -> ta.Mapping[ToolPermission, ToolPermissionState]:
        return self._states

    def set_tool_permission_state(self, tp: ToolPermission, state: ToolPermissionState) -> None:
        self._states[tp] = state
