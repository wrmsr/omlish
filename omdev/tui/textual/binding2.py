import typing as ta

from textual.binding import Binding
from textual.binding import BindingsMap
from textual.dom import DOMNode

from omlish import check


##


def merge_cls_bindings(cls: type) -> BindingsMap:
    bindings: list[BindingsMap] = []

    for base in reversed(cls.__mro__):
        if issubclass(base, DOMNode):
            if not base._inherit_bindings:  # noqa
                bindings.clear()

            bindings.append(
                BindingsMap(
                    base.__dict__.get('BINDINGS', []),
                ),
            )

    keys: dict[str, list[Binding]] = {
        key: key_bindings
        for bindings_ in bindings
        for key, key_bindings in bindings_.key_to_bindings.items()
    }

    new_bindings = BindingsMap.from_keys(keys)
    return new_bindings


def unbind_map_keys(bindings: BindingsMap, keys_to_unbind: ta.Container[str]) -> BindingsMap:
    check.not_isinstance(keys_to_unbind, str)

    new_keys: dict[str, list[Binding]] = {
        key: key_bindings
        for key, key_bindings in bindings.key_to_bindings.items()
        if key not in keys_to_unbind
    }

    return BindingsMap.from_keys(new_keys)
