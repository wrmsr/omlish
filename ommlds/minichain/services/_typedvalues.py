import abc
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish import reflect as rfl
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


def _get_typed_values_type_arg(cls: ta.Any) -> rfl.Type:
    g_mro = rfl.ALIAS_UPDATING_GENERIC_SUBSTITUTION.generic_mro(cls)
    g_tvg = check.single(gb for gb in g_mro if isinstance(gb, rfl.Generic) and gb.cls is _TypedValues)
    return check.single(g_tvg.args)


@dc.dataclass()
class _TypedValuesTypeError(TypeError):
    tv: tv.TypedValue


class _TypedValues(
    _OrigClassCapture,
    lang.Abstract,
    ta.Generic[TypedValueT],
):
    __typed_values_class__: ta.ClassVar[type[tv.TypedValue]]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        tvt = _get_typed_values_type_arg(cls)
        tvct = rfl.get_concrete_type(tvt, use_type_var_bound=True)
        cls.__typed_values_class__ = check.issubclass(check.isinstance(tvct, type), tv.TypedValue)

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

        rty = rfl.type_(orig_class)
        tvt = _get_typed_values_type_arg(rty)

        tv_types_set = frozenset(tv.reflect_typed_values_impls(tvt))
        tv_types = tuple(sorted(
            [check.issubclass(c, self.__typed_values_class__) for c in tv_types_set],
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
