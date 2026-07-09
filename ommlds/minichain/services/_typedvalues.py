import abc
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish import reflect2 as rfl
from omlish import typedvalues as tv

from ._origclasses import _OrigClassCapture


TypedValueT = ta.TypeVar('TypedValueT', bound=tv.TypedValue)


##


@dc.dataclass(frozen=True, kw_only=True)
class _TypedValuesInfo:
    orig_class: ta.Any
    rty: rfl.Type

    tv_types: tuple[type[tv.TypedValue], ...]
    tv_types_set: frozenset[type[tv.TypedValue]]


_TYPED_VALUES_INFO_CACHE: ta.MutableMapping[ta.Any, _TypedValuesInfo] = col.IdentityWeakKeyDictionary()


def _get_typed_values_type_arg(rty: rfl.Type) -> rfl.Type:
    def env_filter(owner: rfl.Type, param: rfl.TypeVarLikeType, arg: rfl.Type) -> rfl.Type:
        if isinstance(arg, rfl.AnyType) and arg.type_of_any is rfl.TypeOfAny.FROM_OMITTED_GENERICS:
            return param
        return arg

    mro = rfl.Mro([
        rfl.MroEntry(mi)
        for mi in rfl.get_mro_instances(
            check.isinstance(rty, rfl.Instance),
            env_filter=env_filter,
        )
    ])

    tve = check.single(e for e in mro if e.info.runtime_object is _TypedValues)
    return check.single(tve.args)


@dc.dataclass()
class _TypedValuesTypeError(TypeError):
    tv: tv.TypedValue


class _TypedValues(
    _OrigClassCapture,
    lang.Abstract,
    ta.Generic[TypedValueT],
):
    """
    The reason this is so complicated compared to any other TypedValues field (like metadata) is that the real set of
    TypedValue types it accepts is known only via __orig_class__.
    """

    __typed_values_base__: ta.ClassVar[type[tv.TypedValue]]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        rty = rfl.reflect_type(cls)
        tvt = _get_typed_values_type_arg(rty)
        if isinstance(tvt, rfl.TypeVarLikeType):
            tvt = tvt.upper_bound
        tvct = tvt.runtime_type_or_raise()
        cls.__typed_values_base__ = check.issubclass(check.isinstance(tvct, type), tv.TypedValue)

    #

    @property
    @abc.abstractmethod
    def _typed_values(self) -> tv.TypedValues[TypedValueT]:
        raise NotImplementedError

    #

    @lang.cached_function(transient=True)
    def _typed_values_info(self) -> _TypedValuesInfo:
        orig_class = self.__captured_orig_class__

        try:
            return _TYPED_VALUES_INFO_CACHE[orig_class]
        except KeyError:
            pass

        rty = rfl.reflect_type(orig_class)
        tvt = _get_typed_values_type_arg(rty)

        tv_types_set = frozenset(tv.reflect2_typed_values_impls(tvt))
        tv_types = tuple(sorted(
            [check.issubclass(c, self.__typed_values_base__) for c in tv_types_set],
            key=lambda c: c.__qualname__,
        ))

        tvi = _TypedValuesInfo(
            orig_class=orig_class,
            rty=rty,

            tv_types=tv_types,
            tv_types_set=tv_types_set,
        )

        _TYPED_VALUES_INFO_CACHE[orig_class] = tvi
        return tvi

    @lang.cached_function(transient=True, cache_exceptions=_TypedValuesTypeError)
    def _check_typed_values(self) -> None:
        tvi = self._typed_values_info()
        for o in self._typed_values:
            if (
                    type(o) not in tvi.tv_types_set and  # Faster
                    not isinstance(o, tvi.tv_types)
            ):
                raise _TypedValuesTypeError(o)
