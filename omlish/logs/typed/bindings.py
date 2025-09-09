# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - optimization of just using ChainMap when override?
  - TypedLoggerBindings as Abstract, FullTLB and LimitedTLB subtypes, limited
 - TypedLoggerBindingsBuilder ?
"""
import abc
import collections
import functools
import itertools
import typing as ta

from ...lite.abstract import Abstract
from .types import TYPED_LOGGER_VALUE_OR_PROVIDER_OR_ABSENT_TYPES
from .types import TYPED_LOGGER_VALUE_OR_PROVIDER_TYPES
from .types import DefaultTypedLoggerValue
from .types import MultiTypedLoggerValue
from .types import TypedLoggerConstFieldValue
from .types import TypedLoggerField
from .types import TypedLoggerFieldValue
from .types import TypedLoggerValue
from .types import TypedLoggerValueOrAbsent
from .types import TypedLoggerValueOrProvider  # noqa
from .types import TypedLoggerValueOrProviderOrAbsent
from .types import TypedLoggerValueProvider


TypedLoggerBindingItem = ta.Union['TypedLoggerField', 'TypedLoggerValueOrProvider', 'TypedLoggerBindings', 'TypedLoggerValueWrapper']  # ta.TypeAlias  # noqa

ChainTypedLoggerBindingItem = ta.Union['TypedLoggerField', 'TypedLoggerValueOrProvider']  # ta.TypeAlias

TypedLoggerValueWrapperFn = ta.Callable[[ta.Any], 'TypedLoggerValue']  # ta.TypeAlias


##


class TypedLoggerDuplicateBindingsError(Exception):
    def __init__(
            self,
            *,
            keys: ta.Optional[ta.Dict[str, ta.List[TypedLoggerFieldValue]]] = None,
            values: ta.Optional[ta.Dict[ta.Type[TypedLoggerValue], ta.List[TypedLoggerValueOrProviderOrAbsent]]] = None,
            wrappers: ta.Optional[ta.Dict[type, ta.List[TypedLoggerValueWrapperFn]]] = None,
    ) -> None:
        super().__init__()

        self.keys = keys
        self.values = values
        self.wrappers = wrappers

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(' +
            ', '.join([
                *([f'keys={self.keys!r}'] if self.keys is not None else []),
                *([f'values={self.values!r}'] if self.values is not None else []),
                *([f'wrappers={self.wrappers!r}'] if self.wrappers is not None else []),
            ]) +
            f')'
        )


class TypedLoggerBindings(Abstract):
    @property
    @abc.abstractmethod
    def key_map(self) -> ta.Mapping[str, TypedLoggerFieldValue]:
        raise NotImplementedError

    @abc.abstractmethod
    def lookup_value(self, cls: ta.Type[TypedLoggerValue]) -> ta.Optional[TypedLoggerValueOrProviderOrAbsent]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def const_value_map(self) -> ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def value_wrapper_fn(self) -> ta.Optional[TypedLoggerValueWrapperFn]:
        raise NotImplementedError

    #

    @ta.final
    class _Visitor(ta.NamedTuple):
        accept_key: ta.Callable[[str, TypedLoggerFieldValue], None]
        accept_keys: ta.Callable[[ta.Iterable[ta.Tuple[str, TypedLoggerFieldValue]]], None]

        accept_value: ta.Callable[[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent], None]
        accept_values: ta.Callable[[ta.Iterable[ta.Tuple[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent]]], None]  # noqa

        accept_multi_value: ta.Callable[[ta.Type[MultiTypedLoggerValue], MultiTypedLoggerValue], None]  # noqa
        accept_multi_values: ta.Callable[[ta.Iterable[ta.Tuple[ta.Type[MultiTypedLoggerValue], MultiTypedLoggerValue]]], None]  # noqa

        accept_const_values: ta.Callable[[ta.Iterable[ta.Tuple[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent]]], None]  # noqa

        accept_value_wrapping: ta.Callable[[ta.Union['TypedLoggerValueWrapper', 'FullTypedLoggerBindings._ValueWrappingState']], None]  # noqa

    @abc.abstractmethod
    def _typed_logger_visit_bindings(self, vst: _Visitor) -> None:
        raise NotImplementedError


##


@ta.final
class FullTypedLoggerBindings(TypedLoggerBindings):
    def __init__(
            self,
            *items: TypedLoggerBindingItem,
            override: bool = False,
            override_multis: bool = False,
    ) -> None:
        kd: ta.Dict[str, TypedLoggerFieldValue] = {}
        dup_kd: ta.Dict[str, ta.List[TypedLoggerFieldValue]] = {}

        if not override:
            def add_kd(kd_k: str, kd_v: TypedLoggerFieldValue) -> None:  # noqa
                if kd_k in kd:
                    dup_kd.setdefault(kd_k, []).append(kd_v)
                else:
                    kd[kd_k] = kd_v

            def add_kds(it: 'ta.Iterable[ta.Tuple[str, TypedLoggerFieldValue]]') -> None:  # noqa
                collections.deque(itertools.starmap(add_kd, it), maxlen=0)

        else:
            add_kd = kd.__setitem__  # type: ignore[assignment]
            add_kds = kd.update  # type: ignore[assignment]

        #

        vd: ta.Dict[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent] = {}
        dup_vd: ta.Dict[ta.Type[TypedLoggerValue], ta.List[TypedLoggerValueOrProviderOrAbsent]] = {}

        if not override:
            def add_vd(vd_k: 'ta.Type[TypedLoggerValue]', vd_v: TypedLoggerValueOrProviderOrAbsent) -> None:  # noqa
                if vd_k in vd:
                    dup_vd.setdefault(vd_k, []).append(vd_v)
                else:
                    vd[vd_k] = vd_v

            def add_vds(it: 'ta.Iterable[ta.Tuple[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent]]') -> None:  # noqa
                collections.deque(itertools.starmap(add_vd, it), maxlen=0)

        else:
            add_vd = vd.__setitem__  # type: ignore[assignment]
            add_vds = vd.update  # type: ignore[assignment]

        #

        mvd: ta.Dict[ta.Type[MultiTypedLoggerValue], ta.List[MultiTypedLoggerValue]] = {}

        if override_multis:
            def add_mvd(mvd_k: 'ta.Type[MultiTypedLoggerValue]', mvd_v: MultiTypedLoggerValue) -> None:  # noqa
                try:
                    mvd_l = mvd[mvd_k]
                except KeyError:
                    mvd_l = mvd[mvd_k] = []
                mvd_l.append(mvd_v)

            def add_mvds(it: 'ta.Iterable[ta.Tuple[ta.Type[MultiTypedLoggerValue], MultiTypedLoggerValue]]') -> None:
                collections.deque(itertools.starmap(add_mvd, it), maxlen=0)

        else:
            add_mvd = mvd.__setitem__  # type: ignore[assignment]
            add_mvds = mvd.update  # type: ignore[assignment]

        #

        cvd: ta.Dict[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent] = {}

        vwl: ta.List[ta.Union[TypedLoggerValueWrapper, FullTypedLoggerBindings._ValueWrappingState]] = []

        vst = TypedLoggerBindings._Visitor(  # noqa
            add_kd,
            add_kds,

            add_vd,
            add_vds,

            add_mvd,
            add_mvds,

            cvd.update,

            vwl.append,
        )

        for o in items:
            o._typed_logger_visit_bindings(vst)  # noqa

        #

        dup_vwd: ta.Optional[ta.Dict[type, ta.List[TypedLoggerValueWrapperFn]]] = None

        vws: ta.Optional[FullTypedLoggerBindings._ValueWrappingState] = None
        vwf: ta.Optional[TypedLoggerValueWrapperFn] = None

        if vwl:
            if len(vwl) == 1 and isinstance((vwl0 := vwl[0]), FullTypedLoggerBindings._ValueWrappingState):
                vws = vwl0

            else:
                vwd: ta.Dict[type, TypedLoggerValueWrapperFn] = {}

                add_vwd: ta.Callable[[type, TypedLoggerValueWrapperFn], None]

                if not override:
                    dup_vwd = {}

                    def add_vwd(vw_ty: type, vw_fn: TypedLoggerValueWrapperFn) -> None:  # noqa
                        if vw_ty in vwd:
                            dup_vwd.setdefault(vw_ty, []).append(vw_fn)
                        else:
                            vwd[vw_ty] = vw_fn

                else:
                    add_vwd = vwd.__setitem__

                for vo in vwl:
                    vo._typed_logger_visit_value_wrappers(add_vwd)  # noqa

                if vwd and not dup_vwd:
                    vws = FullTypedLoggerBindings._ValueWrappingState(vwd)
                    vwf = vws.sdf

        #

        if dup_kd or dup_vd or dup_vwd:
            raise TypedLoggerDuplicateBindingsError(
                keys=dup_kd or None,
                values=dup_vd or None,
                wrappers=dup_vwd or None,
            )

        self._key_map: ta.Mapping[str, TypedLoggerFieldValue] = kd
        self._value_map: ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent] = vd

        self._const_value_map: ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent] = cvd

        self._value_wrapping = vws
        self._value_wrapper_fn = vwf

    #

    @property
    def key_map(self) -> ta.Mapping[str, TypedLoggerFieldValue]:
        return self._key_map

    def lookup_value(self, cls: ta.Type[TypedLoggerValue]) -> ta.Optional[TypedLoggerValueOrProviderOrAbsent]:
        return self._value_map.get(cls)

    @property
    def const_value_map(self) -> ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent]:
        return self._const_value_map

    @property
    def value_wrapper_fn(self) -> ta.Optional[TypedLoggerValueWrapperFn]:
        return self._value_wrapper_fn

    #

    @ta.final
    class _ValueWrappingState:
        def __init__(self, dct: ta.Mapping[type, TypedLoggerValueWrapperFn]) -> None:
            self.dct = dct

            @functools.singledispatch
            def wrap_value(o: ta.Any) -> TypedLoggerValue:
                raise UnhandledTypedValueWrapperTypeError(o)

            collections.deque(itertools.starmap(wrap_value.register, self.dct.items()), maxlen=0)

            self.sdf = wrap_value

        #

        def _typed_logger_visit_value_wrappers(self, fn: ta.Callable[[type, TypedLoggerValueWrapperFn], None]) -> None:  # noqa
            collections.deque(itertools.starmap(fn, self.dct.items()), maxlen=0)

    #

    def _typed_logger_visit_bindings(self, vst: TypedLoggerBindings._Visitor) -> None:
        vst.accept_keys(self._key_map.items())
        vst.accept_values(self._value_map.items())

        vst.accept_const_values(self._const_value_map.items())

        if (vws := self._value_wrapping) is not None:
            vst.accept_value_wrapping(vws)


##


class ChainTypedLoggerBindingsUnhandledItemError(Exception):
    pass


@ta.final
class ChainTypedLoggerBindings(TypedLoggerBindings):
    def __init__(
            self,
            parent: TypedLoggerBindings,
            *items: ChainTypedLoggerBindingItem,
    ) -> None:
        kd: ta.Dict[str, TypedLoggerFieldValue] = {}
        dup_kd: ta.Dict[str, ta.List[TypedLoggerFieldValue]] = {}

        def add_kd(kd_k: str, kd_v: TypedLoggerFieldValue) -> None:  # noqa
            if kd_k in kd:
                dup_kd.setdefault(kd_k, []).append(kd_v)
            else:
                kd[kd_k] = kd_v

        def add_kds(it: 'ta.Iterable[ta.Tuple[str, TypedLoggerFieldValue]]') -> None:  # noqa
            collections.deque(itertools.starmap(add_kd, it), maxlen=0)

        #

        vd: ta.Dict[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent] = {}
        dup_vd: ta.Dict[ta.Type[TypedLoggerValue], ta.List[TypedLoggerValueOrProviderOrAbsent]] = {}

        pcv = dict(parent.const_value_map)

        def add_vd(vd_k: 'ta.Type[TypedLoggerValue]', vd_v: TypedLoggerValueOrProviderOrAbsent) -> None:  # noqa
            if vd_k in vd:
                dup_vd.setdefault(vd_k, []).append(vd_v)
            else:
                vd[vd_k] = vd_v
                pcv.pop(vd_k, None)

        def add_vds(it: 'ta.Iterable[ta.Tuple[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent]]') -> None:  # noqa
            collections.deque(itertools.starmap(add_vd, it), maxlen=0)

        #

        mvd: ta.Dict[ta.Type[MultiTypedLoggerValue], ta.List[MultiTypedLoggerValue]] = {}

        def add_mvd(mvd_k: 'ta.Type[MultiTypedLoggerValue]', mvd_v: MultiTypedLoggerValue) -> None:  # noqa
            try:
                mvd_l = mvd[mvd_k]
            except KeyError:
                mvd_l = mvd[mvd_k] = []
            mvd_l.append(mvd_v)

        def add_mvds(it: 'ta.Iterable[ta.Tuple[ta.Type[MultiTypedLoggerValue], MultiTypedLoggerValue]]') -> None:
            collections.deque(itertools.starmap(add_mvd, it), maxlen=0)

        #

        cvd: ta.Dict[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent] = {}

        def bad_type(*args, **kwargs):  # noqa
            raise ChainTypedLoggerBindingsUnhandledItemError

        vst = TypedLoggerBindings._Visitor(  # noqa
            add_kd,
            add_kds,

            add_vd,
            add_vds,

            add_mvd,
            add_mvds,

            cvd.update,

            bad_type,
        )

        for o in items:
            try:
                o._typed_logger_visit_bindings(vst)  # noqa
            except ChainTypedLoggerBindingsUnhandledItemError:
                raise ChainTypedLoggerBindingsUnhandledItemError(o) from None

        #

        if dup_kd or dup_vd:
            raise TypedLoggerDuplicateBindingsError(
                keys=dup_kd or None,
                values=dup_vd or None,
            )

        self._parent = parent

        self._key_map = {**parent.key_map, **kd}
        self._self_value_map = vd
        self._const_value_map = {**pcv, **cvd}

    @property
    def key_map(self) -> ta.Mapping[str, TypedLoggerFieldValue]:
        return self._key_map

    def lookup_value(self, cls: ta.Type[TypedLoggerValue]) -> ta.Optional[TypedLoggerValueOrProviderOrAbsent]:
        try:
            return self._self_value_map[cls]
        except KeyError:
            pass
        return self._parent.lookup_value(cls)

    @property
    def const_value_map(self) -> ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent]:
        return self._const_value_map

    @property
    def value_wrapper_fn(self) -> ta.Optional[TypedLoggerValueWrapperFn]:
        return self._parent.value_wrapper_fn

    #

    def _typed_logger_visit_bindings(self, vst: 'TypedLoggerBindings._Visitor') -> None:
        self._parent._typed_logger_visit_bindings(vst)  # noqa


##


class UnhandledTypedValueWrapperTypeError(TypeError):
    pass


@ta.final
class TypedLoggerValueWrapper(ta.NamedTuple):
    tys: ta.AbstractSet[type]
    fn: TypedLoggerValueWrapperFn

    #

    def _typed_logger_visit_bindings(self, vst: TypedLoggerBindings._Visitor) -> None:  # noqa
        vst.accept_value_wrapping(self)

    def _typed_logger_visit_value_wrappers(self, fn: ta.Callable[[type, TypedLoggerValueWrapperFn], None]) -> None:  # noqa
        for ty in self.tys:
            fn(ty, self.fn)


##


TYPED_LOGGER_BINDING_ITEM_TYPES: ta.Tuple[ta.Type[TypedLoggerBindingItem], ...] = (
    TypedLoggerField,
    *TYPED_LOGGER_VALUE_OR_PROVIDER_TYPES,
    TypedLoggerBindings,
    TypedLoggerValueWrapper,
)


##


CanTypedLoggerBinding = ta.Union[  # ta.TypeAlias  # omlish-amalg-typing-no-move
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

CanChainTypedLoggerBinding = ta.Union[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    ChainTypedLoggerBindingItem,
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
    TypedLoggerValueWrapper,
)

_AS_TYPED_LOGGER_BINDINGS_FIELD_VALUE_DIRECT_TYPES: ta.Tuple[type, ...] = (
    *TYPED_LOGGER_VALUE_OR_PROVIDER_OR_ABSENT_TYPES,
    TypedLoggerConstFieldValue,
)


# @ta.final
# class TypedLoggerBindingsBuilder:
#     def __init__(
#             self,
#             *,
#             add_default_keys: bool = False,
#             default_key_filter: ta.Optional[ta.Callable[[str], bool]] = None,
#
#             add_default_values: bool = False,
#             default_value_filter: ta.Optional[ta.Callable[[ta.Type[DefaultTypedLoggerValue]], bool]] = None,
#
#             value_wrapper: ta.Optional[TypedLoggerValueWrapperFn] = None,
#     ) -> None:
#         self._add_default_keys = add_default_keys
#         self._default_key_filter = default_key_filter
#
#         self._add_default_values = add_default_values
#         self._default_value_filter = default_value_filter
#
#         self._value_wrapper = value_wrapper
#
#         self._lst: ta.List[TypedLoggerBindingItem] = []


def as_typed_logger_bindings(
        *objs: CanTypedLoggerBinding,

        add_default_keys: bool = False,
        default_key_filter: ta.Optional[ta.Callable[[str], bool]] = None,

        add_default_values: bool = False,
        default_value_filter: ta.Optional[ta.Callable[[ta.Type[DefaultTypedLoggerValue]], bool]] = None,

        value_wrapper: ta.Optional[TypedLoggerValueWrapperFn] = None,
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

        elif value_wrapper is not None:
            wv = value_wrapper(o)
            if not isinstance(wv, TypedLoggerValue):
                raise TypeError(wv)

            lst.append(wv)

            if add_default_keys:
                if (dk := wv.default_key()) is not None:
                    if default_key_filter is None or default_key_filter(dk):
                        lst.append(TypedLoggerField(dk, wv))

        else:
            # ta.assert_never(o)
            raise TypeError(o)

    return lst
