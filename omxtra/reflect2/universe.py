# ruff: noqa: SLF001
import enum
import threading
import typing as ta

from .core.symbols import TypeInfo
from .core.symbols import VarianceKind
from .core.types import _ANY_TYPES
from .core.types import Instance
from .core.types import Type
from .core.types import TypeOfAny
from .core.types import TypeVarId
from .core.types import TypeVarLikeType
from .core.types import TypeVarType
from .errors import ReflectionValueError
from .known import _KNOWN_BASE_SPECS
from .known import _KNOWN_FULLNAMES_BY_TYPE
from .known import _KNOWN_GENERIC_ARITIES
from .known import _KNOWN_GENERIC_VARIANCES
from .known import _KNOWN_MRO_TAILS
from .known import _KnownBaseArg


DynamicTypeNameSuffix: ta.TypeAlias = ta.Literal['id', 'counter']


##


_DYNAMIC_TYPE_NAME_SEPARATOR: ta.Final = '@'


##


@ta.final
class RuntimeTypeUniverse:
    def __init__(
            self,
            *,
            dynamic_type_name_suffix: DynamicTypeNameSuffix = 'id',
    ) -> None:
        super().__init__()

        if dynamic_type_name_suffix not in ('id', 'counter'):
            raise ReflectionValueError(f'Unsupported dynamic type name suffix mode: {dynamic_type_name_suffix!r}')

        self._dynamic_type_name_suffix = dynamic_type_name_suffix

        # Explicitly not an `RLock` - we're very conservative about our public api surface. `Reflector` has a much
        # larger surface area, but it's also not necessarily shared globally - whereas this usually will be. The locking
        # discipline here is simply: all underscore methods expect to have the lock, and all public methods will
        # optionally first try a fast unlocked cached path, and otherwise immediately grab the lock and jump to a
        # private method.
        self._lock = threading.Lock()

        self._next_dynamic_type_index = 1

        self._infos_by_fullname: dict[str, TypeInfo] = {}
        self._fullnames_by_type: dict[object, str] = dict(_KNOWN_FULLNAMES_BY_TYPE)
        self._types_by_fullname: dict[str, object] = {
            fullname: obj
            for obj, fullname in self._fullnames_by_type.items()
        }

    #

    @property
    def dynamic_type_name_suffix(self) -> DynamicTypeNameSuffix:
        return self._dynamic_type_name_suffix

    def _make_dynamic_type_name_hint(self, obj: type) -> str:
        module = getattr(obj, '__module__', None)
        qualname = getattr(obj, '__qualname__', None)
        if isinstance(module, str) and module and isinstance(qualname, str) and qualname:
            return qualname if module == 'builtins' else f'{module}.{qualname}'

        name = getattr(obj, '__name__', None)
        if isinstance(name, str) and name:
            return name

        return 'type'

    def _make_dynamic_type_fullname(self, obj: type) -> str:
        hint = self._make_dynamic_type_name_hint(obj)
        if self.dynamic_type_name_suffix == 'counter':
            suffix = str(self._next_dynamic_type_index)
            self._next_dynamic_type_index += 1
        else:
            suffix = f'{id(obj):x}'
        return f'{hint}{_DYNAMIC_TYPE_NAME_SEPARATOR}{suffix}'

    def _make_new_type_fullname(self, obj: object) -> str:
        module = getattr(obj, '__module__', None)
        qualname = getattr(obj, '__qualname__', None)
        if isinstance(module, str) and module and isinstance(qualname, str) and qualname:
            return qualname if module == 'builtins' else f'{module}.{qualname}'

        name = getattr(obj, '__name__', None)
        if isinstance(name, str) and name:
            return name

        return f'NewType@{id(obj):x}'

    def _make_type_var(self, fullname: str, index: int, variance: VarianceKind) -> TypeVarType:
        object_info = self._get_type_info('builtins.object')
        object_type = Instance(object_info, [])
        default = _ANY_TYPES[TypeOfAny.FROM_OMITTED_GENERICS]
        name = f'T{index}'
        return TypeVarType(
            name,
            f'{fullname}.{name}',
            TypeVarId(index + 1),
            [],
            object_type,
            default,
            variance,
        )

    def _make_type_info(self, fullname: str) -> TypeInfo:
        name = fullname.rsplit('.', 1)[-1]
        arity = _KNOWN_GENERIC_ARITIES.get(fullname, 0)
        variances = list(_KNOWN_GENERIC_VARIANCES.get(fullname, (VarianceKind.IN,) * arity))
        type_vars: list[TypeVarLikeType] = [
            self._make_type_var(fullname, index, variance)
            for index, variance in enumerate(variances)
        ]
        return TypeInfo(
            name,
            fullname,
            type_vars=type_vars,
            variances=variances,
        )

    def _make_known_bases(self, info: TypeInfo) -> list[Type]:
        specs = _KNOWN_BASE_SPECS.get(info._fullname, ())
        bases: list[Type] = []
        for target_fullname, arg_specs in specs:
            bases.append(Instance(
                self._get_type_info(target_fullname),
                [
                    self._make_known_base_arg(info, arg_spec)
                    for arg_spec in arg_specs
                ],
            ))
        return bases

    def _make_known_base_arg(self, info: TypeInfo, arg_spec: _KnownBaseArg) -> Type:
        if isinstance(arg_spec, int):
            return info.type_vars[arg_spec]
        return Instance(self._get_type_info(arg_spec), [])

    def _make_known_mro(self, info: TypeInfo) -> list[TypeInfo] | None:
        tail = _KNOWN_MRO_TAILS.get(info._fullname)
        if tail is None:
            return None
        return [info, *[self._get_type_info(fullname) for fullname in tail]]

    #

    def _configure_known_type_info(self, info: TypeInfo) -> None:
        info._bases = self._make_known_bases(info)
        if (mro := self._make_known_mro(info)) is not None:
            info._mro = mro

    def _get_type_info(self, obj: type | str) -> TypeInfo:
        if isinstance(obj, str):
            fullname = obj
            runtime_type = None
        else:
            runtime_type = obj
            try:
                fullname = self._fullnames_by_type[obj]
            except KeyError:
                fullname = self._make_dynamic_type_fullname(obj)
                self._fullnames_by_type[obj] = fullname
                self._types_by_fullname[fullname] = obj

        try:
            return self._infos_by_fullname[fullname]
        except KeyError:
            pass

        info = self._make_type_info(fullname)
        self._infos_by_fullname[fullname] = info
        self._configure_known_type_info(info)
        if runtime_type is not None and issubclass(runtime_type, enum.Enum):
            info._is_enum = True
            info._enum_members = [
                member.name
                for member in runtime_type
            ]
        return info

    def get_type_info(self, obj: type | str) -> TypeInfo:
        if isinstance(obj, str):
            try:
                return self._infos_by_fullname[obj]
            except KeyError:
                pass
        else:
            try:
                fullname = self._fullnames_by_type[obj]
            except KeyError:
                pass
            else:
                try:
                    return self._infos_by_fullname[fullname]
                except KeyError:
                    pass

        with self._lock:
            return self._get_type_info(obj)

    def _get_new_type_info(self, obj: object) -> TypeInfo:
        try:
            fullname = self._fullnames_by_type[obj]
        except KeyError:
            fullname = self._make_new_type_fullname(obj)
            if fullname in self._types_by_fullname:
                fullname = f'{fullname}@{id(obj):x}'
            self._fullnames_by_type[obj] = fullname
            self._types_by_fullname[fullname] = obj

        try:
            return self._infos_by_fullname[fullname]
        except KeyError:
            pass

        name = fullname.rsplit('.', 1)[-1]
        info = TypeInfo(name, fullname)
        self._infos_by_fullname[fullname] = info

        supertype = getattr(obj, '__supertype__')
        if isinstance(supertype, type):
            base_type = self._get_type_info(supertype)
            info._new_type_supertype = Instance(base_type, [])
        else:
            base_type = self._get_type_info('builtins.object')
        info._bases = [Instance(base_type, [])]
        info._mro = [info, *base_type._mro]

        return info

    def get_new_type_info(self, obj: object) -> TypeInfo:
        if not isinstance(obj, ta.NewType):  # noqa
            raise TypeError('get_new_type_info only accepts `typing.NewType` objects')

        try:
            fullname = self._fullnames_by_type[obj]
        except KeyError:
            pass
        else:
            try:
                return self._infos_by_fullname[fullname]
            except KeyError:
                pass

        with self._lock:
            return self._get_new_type_info(obj)

    def get_runtime_type(self, info: TypeInfo) -> object | None:
        return self._types_by_fullname.get(info._fullname)


DEFAULT_UNIVERSE = RuntimeTypeUniverse()


def get_type_info(obj: type | str) -> TypeInfo:
    return DEFAULT_UNIVERSE.get_type_info(obj)
