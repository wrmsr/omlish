import collections.abc
import functools
import typing as ta


_GENERIC_ALIAS_TYPES = (
    ta._GenericAlias,  # type: ignore  # noqa
    *([ta._SpecialGenericAlias] if hasattr(ta, '_SpecialGenericAlias') else []),  # noqa
)


def is_generic_alias(obj, *, origin: ta.Any = None) -> bool:
    return (
        isinstance(obj, _GENERIC_ALIAS_TYPES) and
        (origin is None or ta.get_origin(obj) is origin)
    )


is_list_alias = functools.partial(is_generic_alias, origin=list)
is_set_alias = functools.partial(is_generic_alias, origin=set)
is_frozenset_alias = functools.partial(is_generic_alias, origin=frozenset)
is_dict_alias = functools.partial(is_generic_alias, origin=dict)

is_union_alias = functools.partial(is_generic_alias, origin=ta.Union)
is_callable_alias = functools.partial(is_generic_alias, origin=ta.Callable)

is_abstractset_alias = functools.partial(is_generic_alias, origin=collections.abc.Set)
is_mutable_set_alias = functools.partial(is_generic_alias, origin=collections.abc.MutableSet)
is_mapping_alias = functools.partial(is_generic_alias, origin=collections.abc.Mapping)
is_mutable_mapping_alias = functools.partial(is_generic_alias, origin=collections.abc.MutableMapping)
is_sequence_alias = functools.partial(is_generic_alias, origin=collections.abc.Sequence)
is_mutable_sequence_alias = functools.partial(is_generic_alias, origin=collections.abc.MutableSequence)


def is_optional_alias(spec: ta.Any) -> bool:
    return (
        isinstance(spec, _GENERIC_ALIAS_TYPES) and  # noqa
        ta.get_origin(spec) is ta.Union and
        len(ta.get_args(spec)) == 2 and
        any(a in (None, type(None)) for a in ta.get_args(spec))
    )


def get_optional_alias_arg(spec: ta.Any) -> ta.Any:
    [it] = [it for it in ta.get_args(spec) if it not in (None, type(None))]
    return it
