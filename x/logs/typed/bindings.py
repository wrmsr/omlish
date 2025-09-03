# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - optimization of just using ChainMap when override?
 - TypedLoggerBindingsBuilder ?
"""
import typing as ta

from .types import DefaultTypedLoggerValue
from .types import TYPED_LOGGER_VALUE_OR_PROVIDER_OR_ABSENT_TYPES
from .types import TYPED_LOGGER_VALUE_OR_PROVIDER_TYPES
from .types import TypedLoggerConstFieldValue
from .types import TypedLoggerField
from .types import TypedLoggerFieldValue
from .types import TypedLoggerValue
from .types import TypedLoggerValueOrAbsent
from .types import TypedLoggerValueOrProvider
from .types import TypedLoggerValueOrProviderOrAbsent
from .types import TypedLoggerValueProvider


TypedLoggerBindingItem = ta.Union[TypedLoggerField, TypedLoggerValueOrProvider, 'TypedLoggerBindings']  # ta.TypeAlias


##


class TypedLoggerDuplicateBindingsError(Exception):
    def __init__(
            self,
            *,
            keys: ta.Optional[ta.Dict[str, ta.List[TypedLoggerFieldValue]]] = None,
            values: ta.Optional[ta.Dict[ta.Type[TypedLoggerValue], ta.List[TypedLoggerValueOrProviderOrAbsent]]] = None,
    ) -> None:
        super().__init__()

        self.keys = keys
        self.values = values

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(' +
            ', '.join([
                *([f'keys={self.keys!r}'] if self.keys is not None else []),
                *([f'values={self.values!r}'] if self.values is not None else []),
            ]) +
            f')'
        )


@ta.final
class TypedLoggerBindings:
    def __init__(
            self,
            *items: TypedLoggerBindingItem,
            override: bool = False,
    ) -> None:
        kd: ta.Dict[str, TypedLoggerFieldValue] = {}
        dup_kd: ta.Dict[str, ta.List[TypedLoggerFieldValue]] = {}

        vd: ta.Dict[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent] = {}
        dup_vd: ta.Dict[ta.Type[TypedLoggerValue], ta.List[TypedLoggerValueOrProviderOrAbsent]] = {}

        cvd: ta.Dict[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent] = {}

        vst: TypedLoggerBindings._Visitor

        if not override:
            def add_kds(it) -> None:  # noqa
                for kd_k, kd_v in it:
                    if kd_k in kd:
                        dup_kd.setdefault(kd_k, []).append(kd_v)
                    else:
                        kd[kd_k] = kd_v

            def add_vds(it) -> None:  # noqa
                for vd_k, vd_v in it:
                    if vd_k in vd:
                        dup_vd.setdefault(vd_k, []).append(vd_v)
                    else:
                        vd[vd_k] = vd_v

            vst = TypedLoggerBindings._Visitor(
                add_kds,
                add_vds,
                cvd.update,
            )

        else:
            vst = TypedLoggerBindings._Visitor(
                kd.update,
                vd.update,
                cvd.update,
            )

        for o in items:
            o._typed_logger_visit_bindings(vst)  # noqa

        if dup_kd or dup_vd:
            raise TypedLoggerDuplicateBindingsError(
                keys=dup_kd or None,
                values=dup_vd or None,
            )

        self._key_map: ta.Mapping[str, TypedLoggerFieldValue] = kd
        self._value_map: ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent] = vd
        self._const_value_map: ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent] = cvd

    @ta.final
    class _Visitor(ta.NamedTuple):
        accept_keys: ta.Callable[[ta.Iterable[ta.Tuple[str, TypedLoggerFieldValue]]], None]
        accept_values: ta.Callable[[ta.Iterable[ta.Tuple[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent]]], None]  # noqa
        accept_const_values: ta.Callable[[ta.Iterable[ta.Tuple[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent]]], None]  # noqa

    @property
    def key_map(self) -> ta.Mapping[str, TypedLoggerFieldValue]:
        return self._key_map

    @property
    def value_map(self) -> ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent]:
        return self._value_map

    @property
    def const_value_map(self) -> ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent]:
        return self._const_value_map

    #

    def _typed_logger_visit_bindings(self, vst: _Visitor) -> None:
        vst.accept_keys(self._key_map.items())
        vst.accept_values(self._value_map.items())
        vst.accept_const_values(self._const_value_map.items())


##


TYPED_LOGGER_BINDING_ITEM_TYPES: ta.Tuple[ta.Type[TypedLoggerBindingItem], ...] = (
    TypedLoggerField,
    *TYPED_LOGGER_VALUE_OR_PROVIDER_TYPES,
    TypedLoggerBindings,
)


##


CanTypedLoggerBinding = ta.Union[  # ta.TypeAlias  # omlish-amalg-typing-no-move'
    TypedLoggerBindingItem,
    ta.Type[TypedLoggerValue],
    ta.Tuple[
        str,
        ta.Union[
            TypedLoggerFieldValue,
            ta.Any,
        ],
    ],
    None,
]


_AS_TYPED_LOGGER_BINDINGS_DIRECT_TYPES: ta.Tuple[type, ...] = (
    TypedLoggerField,
    TypedLoggerBindings,
)

_AS_TYPED_LOGGER_BINDINGS_FIELD_VALUE_DIRECT_TYPES: ta.Tuple[type, ...] = (
    *TYPED_LOGGER_VALUE_OR_PROVIDER_OR_ABSENT_TYPES,
    TypedLoggerConstFieldValue,
)


def as_typed_logger_bindings(
        *objs: CanTypedLoggerBinding,

        add_default_keys: bool = False,
        default_key_filter: ta.Optional[ta.Callable[[str], bool]] = None,

        add_default_values: bool = False,
        default_value_filter: ta.Optional[ta.Callable[[ta.Type[DefaultTypedLoggerValue]], bool]] = None,
) -> ta.Sequence[TypedLoggerBindingItem]:
    """This functionality is combined to preserve final key ordering."""

    lst: ta.List[TypedLoggerBindingItem] = []

    for o in objs:
        if o is None:
            continue

        elif isinstance(o, _AS_TYPED_LOGGER_BINDINGS_DIRECT_TYPES):
            lst.append(o)  # type: ignore[arg-type]

        elif isinstance(o, TypedLoggerValue):
            lst.append(o)

            if add_default_keys:
                if (dk := o.default_key()) is not None:
                    if default_key_filter is None or default_key_filter(dk):
                        lst.append(TypedLoggerField(dk, o))

        elif isinstance(o, TypedLoggerValueProvider):
            lst.append(o)

            if add_default_keys:
                if (dk := o.cls.default_key()) is not None:
                    if default_key_filter is None or default_key_filter(dk):
                        lst.append(TypedLoggerField(dk, o))

        elif isinstance(o, type) and issubclass(o, TypedLoggerValue):
            b = False

            if add_default_values and issubclass(o, DefaultTypedLoggerValue):
                if (dp := o.default_provider()) is not None:
                    if default_value_filter is None or default_value_filter(o):
                        lst.append(dp)
                        b = True

            if add_default_keys:
                if (dk := o.default_key()) is not None:
                    if default_key_filter is None or default_key_filter(dk):
                        lst.append(TypedLoggerField(dk, o))
                        b = True

            if not b:
                raise TypeError(f'{o} was added as neither a default key nor a default value')

        elif isinstance(o, tuple):
            k, v = o
            if not isinstance(k, str):
                raise TypeError(k)

            if (
                    isinstance(v, _AS_TYPED_LOGGER_BINDINGS_FIELD_VALUE_DIRECT_TYPES) or
                    (isinstance(o, type) and issubclass(o, TypedLoggerValue))  # type: ignore[unreachable]
            ):
                lst.append(TypedLoggerField(k, v))  # type: ignore[arg-type]

            else:
                lst.append(TypedLoggerField(k, TypedLoggerConstFieldValue(v)))

        else:
            # ta.assert_never(o)
            raise TypeError(o)

    return lst
