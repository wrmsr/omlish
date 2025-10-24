import contextlib
import keyword
import sys
import types
import typing as ta

from ....specs import ReprFn
from .decorator import dataclass


##


_IS_PY_3_14 = sys.version_info >= (3, 14)

if _IS_PY_3_14:
    import annotationlib  # noqa

    _ANY_MARKER = object()


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

        decorator=dataclass,

        #

        metadata: ta.Sequence[ta.Any] | None = None,

        reorder: bool | None = None,
        cache_hash: bool | None = None,
        generic_init: bool | None = None,
        override: bool | None = None,
        allow_dynamic_dunder_attrs: bool | None = None,

        repr_id: bool | None = None,
        terse_repr: bool | None = None,
        default_repr_fn: ReprFn | None = None,

        allow_redundant_decorator: bool | None = None,

        _frame_offset: int = 1,
):
    if decorator is not dataclass:
        raise TypeError(
            f'The `decorator` kwarg, as added in https://github.com/python/cpython/pull/122723, is not supported. '
            f'{decorator=}',
        )

    if namespace is None:
        namespace = {}

    seen = set()
    annotations = {}
    defaults = {}
    for item in fields:
        if isinstance(item, str):
            name = item
            if _IS_PY_3_14:
                tp = _ANY_MARKER
            else:
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

    if _IS_PY_3_14:
        # We initially block the VALUE format, because inside dataclass() we'll call get_annotations(), which will try
        # the VALUE format first. If we don't block, that means we'd always end up eagerly importing typing here, which
        # is what we're trying to avoid.
        value_blocked = True

        def annotate_method(format):  # noqa
            def get_any():
                match format:
                    case annotationlib.Format.STRING:
                        return 'typing.Any'
                    case annotationlib.Format.FORWARDREF:
                        typing = sys.modules.get('typing')
                        if typing is None:
                            return annotationlib.ForwardRef('Any', module='typing')
                        else:
                            return typing.Any
                    case annotationlib.Format.VALUE:
                        if value_blocked:
                            raise NotImplementedError
                        from typing import Any
                        return Any
                    case _:
                        raise NotImplementedError

            annos = {
                ann: get_any() if t is _ANY_MARKER else t
                for ann, t in annotations.items()
            }
            if format == annotationlib.Format.STRING:
                return annotationlib.annotations_to_string(annos)
            else:
                return annos

    def exec_body_callback(ns):
        ns.update(namespace)
        ns.update(defaults)
        if not _IS_PY_3_14:
            ns['__annotations__'] = annotations

    cls = types.new_class(cls_name, bases, {}, exec_body_callback)

    if _IS_PY_3_14:
        # For now, set annotations including the _ANY_MARKER.
        cls.__annotate__ = annotate_method  # type: ignore  # noqa

    if module is None:
        try:
            module = sys._getframemodulename(_frame_offset) or '__main__'  # noqa
        except AttributeError:
            with contextlib.suppress(AttributeError, ValueError):
                module = sys._getframe(_frame_offset).f_globals.get('__name__', '__main__')  # noqa
    if module is not None:
        cls.__module__ = module

    cls = decorator(
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
        default_repr_fn=default_repr_fn,

        allow_redundant_decorator=allow_redundant_decorator,
    )

    if _IS_PY_3_14:
        # Now that the class is ready, allow the VALUE format.
        value_blocked = False

    return cls
