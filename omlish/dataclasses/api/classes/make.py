import contextlib
import keyword
import sys
import types
import typing as ta

from .decorator import dataclass


##


def make_dataclass(  # noqa
        cls_name,
        fields,
        *,
        bases=(),
        namespace=None,

        init=True,
        repr=True,  # noqa
        eq=True,
        order=False,
        unsafe_hash=False,
        frozen=False,

        match_args=True,
        kw_only=False,
        slots=False,
        weakref_slot=False,

        module=None,

        #

        metadata: ta.Sequence[ta.Any] | None = None,

        reorder: bool | None = None,
        cache_hash: bool | None = None,
        generic_init: bool | None = None,
        override: bool | None = None,
        allow_dynamic_dunder_attrs: bool | None = None,

        repr_id: bool | None = None,
        terse_repr: bool | None = None,

        allow_redundant_decorator: bool | None = None,
):
    if namespace is None:
        namespace = {}

    seen = set()
    annotations = {}
    defaults = {}
    for item in fields:
        if isinstance(item, str):
            name = item
            tp = 'typing.Any'
        elif len(item) == 2:
            name, tp, = item
        elif len(item) == 3:
            name, tp, spec = item
            defaults[name] = spec
        else:
            raise TypeError(f'Invalid field: {item!r}')
        if not isinstance(name, str) or not name.isidentifier():
            raise TypeError(f'Field names must be valid identifiers: {name!r}')
        if keyword.iskeyword(name):
            raise TypeError(f'Field names must not be keywords: {name!r}')
        if name in seen:
            raise TypeError(f'Field name duplicated: {name!r}')

        seen.add(name)
        annotations[name] = tp

    def exec_body_callback(ns):
        ns.update(namespace)
        ns.update(defaults)
        ns['__annotations__'] = annotations

    cls = types.new_class(cls_name, bases, {}, exec_body_callback)

    if module is None:
        try:
            module = sys._getframemodulename(1) or '__main__'  # type: ignore  # noqa
        except AttributeError:
            with contextlib.suppress(AttributeError, ValueError):
                module = sys._getframe(1).f_globals.get('__name__', '__main__')  # noqa
    if module is not None:
        cls.__module__ = module

    return dataclass(
        cls,
        init=init,
        repr=repr,
        eq=eq,
        order=order,
        unsafe_hash=unsafe_hash,
        frozen=frozen,
        match_args=match_args,
        kw_only=kw_only,
        slots=slots,
        weakref_slot=weakref_slot,

        #

        metadata=metadata,

        reorder=reorder,
        cache_hash=cache_hash,
        generic_init=generic_init,
        override=override,
        allow_dynamic_dunder_attrs=allow_dynamic_dunder_attrs,

        repr_id=repr_id,
        terse_repr=terse_repr,

        allow_redundant_decorator=allow_redundant_decorator,
    )
