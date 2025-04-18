import copy
import dataclasses as dc
import typing as ta

from ..internals import STD_ATOMIC_TYPES
from ..internals import std_is_dataclass_instance


##


def asdict(obj, *, dict_factory=dict):  # noqa
    if not std_is_dataclass_instance(obj):  # noqa
        raise TypeError('asdict() should be called on dataclass instances')
    return _asdict_inner(obj, dict_factory)


def _asdict_inner(obj, dict_factory):
    if type(obj) in STD_ATOMIC_TYPES:
        return obj

    elif std_is_dataclass_instance(obj):
        l = []
        for f in dc.fields(obj):
            value = _asdict_inner(getattr(obj, f.name), dict_factory)
            l.append((f.name, value))
        return dict_factory(l)

    elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
        return type(obj)(*[_asdict_inner(v, dict_factory) for v in obj])

    elif isinstance(obj, (list, tuple)):
        return type(obj)(_asdict_inner(v, dict_factory) for v in obj)

    elif isinstance(obj, dict):
        if hasattr(type(obj), 'default_factory'):
            d = type(obj)(getattr(obj, 'default_factory'))
            for k, v in obj.items():
                d[_asdict_inner(k, dict_factory)] = _asdict_inner(v, dict_factory)
            return d
        return type(obj)((_asdict_inner(k, dict_factory), _asdict_inner(v, dict_factory)) for k, v in obj.items())

    else:
        return copy.deepcopy(obj)


def astuple(obj, *, tuple_factory=tuple):  # noqa
    if not std_is_dataclass_instance(obj):
        raise TypeError('astuple() should be called on dataclass instances')
    return _astuple_inner(obj, tuple_factory)


def _astuple_inner(obj, tuple_factory):
    if type(obj) in STD_ATOMIC_TYPES:
        return obj

    elif std_is_dataclass_instance(obj):
        l = []
        for f in dc.fields(obj):
            value = _astuple_inner(getattr(obj, f.name), tuple_factory)
            l.append(value)
        return tuple_factory(l)

    elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
        return type(obj)(*[_astuple_inner(v, tuple_factory) for v in obj])

    elif isinstance(obj, (list, tuple)):
        return type(obj)(_astuple_inner(v, tuple_factory) for v in obj)

    elif isinstance(obj, dict):
        obj_type = type(obj)
        if hasattr(obj_type, 'default_factory'):
            d = obj_type(getattr(obj, 'default_factory'))
            for k, v in obj.items():
                d[_astuple_inner(k, tuple_factory)] = _astuple_inner(v, tuple_factory)
            return d
        return obj_type((_astuple_inner(k, tuple_factory), _astuple_inner(v, tuple_factory)) for k, v in obj.items())

    else:
        return copy.deepcopy(obj)


##


def shallow_astuple(o: ta.Any) -> tuple[ta.Any, ...]:
    return tuple(getattr(o, f.name) for f in dc.fields(o))


def shallow_asdict(o: ta.Any) -> dict[str, ta.Any]:
    return {f.name: getattr(o, f.name) for f in dc.fields(o)}
