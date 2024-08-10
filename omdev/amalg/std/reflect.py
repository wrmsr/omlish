import collections.abc
import functools
import typing as ta


def is_generic_alias(obj, *, origin: ta.Any = None) -> bool:
    return (
            isinstance(obj, (ta._GenericAlias, ta._SpecialGenericAlias)) and  # type: ignore  # noqa
            (origin is None or obj.__origin__ is origin)
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
            isinstance(spec, ta._GenericAlias) and  # type: ignore  # noqa
            spec.__origin__ is ta.Union and
            len(spec.__args__) == 2 and
            any(a in (None, type(None)) for a in spec.__args__)
    )


def get_optional_alias_arg(spec: ta.Any) -> ta.Any:
    [it] = [it for it in spec.__args__ if it not in (None, type(None))]
    return it
