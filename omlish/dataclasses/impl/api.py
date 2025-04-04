"""
TODO:
 - fix code redundancy
"""
import collections.abc
import contextlib
import dataclasses as dc
import keyword
import sys
import types
import typing as ta

from ... import check as check_
from ... import lang
from .internals import PARAMS_ATTR
from .internals import Params
from .main import process_class
from .metadata import METADATA_ATTR
from .metadata import Metadata
from .params import FieldExtras
from .params import ParamsExtras


MISSING = dc.MISSING


def field(  # noqa
        default=MISSING,
        *,
        default_factory=MISSING,
        init=True,
        repr=True,  # noqa
        hash=None,  # noqa
        compare=True,
        metadata=None,
        kw_only=MISSING,

        derive: ta.Callable[..., ta.Any] | None = None,
        coerce: bool | ta.Callable[[ta.Any], ta.Any] | None = None,
        validate: ta.Callable[[ta.Any], bool] | None = None,
        check_type: bool | type | tuple[type | None, ...] | None = None,
        override: bool = False,
        repr_fn: ta.Callable[[ta.Any], str | None] | None = None,
        repr_priority: int | None = None,
        frozen: bool | None = None,
):  # -> dc.Field
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError('cannot specify both default and default_factory')

    fx = FieldExtras()
    if metadata is not None:
        fx = metadata.get(FieldExtras, fx)

    fx = dc.replace(fx, **lang.opt_kw(
        derive=derive,
        coerce=coerce,
        validate=validate,
        check_type=check_type,
        override=override,
        repr_fn=repr_fn,
        repr_priority=repr_priority,
        frozen=frozen,
    ))

    md: ta.Mapping = {FieldExtras: fx}
    if metadata is not None:
        md = collections.ChainMap(md, check_.isinstance(metadata, collections.abc.Mapping))  # type: ignore

    return dc.Field(
        default,
        default_factory,  # noqa
        init,
        repr,
        hash,
        compare,
        types.MappingProxyType(md),
        kw_only,  # noqa
    )


def _strip_missing_values(d):
    return {k: v for k, v in d.items() if v is not MISSING}


def dataclass(  # noqa
        cls=None,
        /,
        *,
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

        metadata=None,

        reorder=MISSING,
        cache_hash=MISSING,
        generic_init=MISSING,
        override=MISSING,
        repr_id=MISSING,
):
    def wrap(cls):
        pkw = dict(
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
        )

        dmd = cls.__dict__.get(METADATA_ATTR)

        epk = dict(dmd.get(_ExtraParamsKwargs, ()) if dmd is not None else ())
        epk.update(_strip_missing_values(dict(
            reorder=reorder,
            cache_hash=cache_hash,
            generic_init=generic_init,
            override=override,
            repr_id=repr_id,
        )))
        pex = ParamsExtras(**epk)

        mmd: dict = {
            ParamsExtras: pex,
        }

        md: Metadata = mmd
        cmds = []
        if metadata is not None:
            cmds.append(check_.isinstance(metadata, collections.abc.Mapping))
        if dmd is not None:
            cmds.append(dmd)
        if cmds:
            md = collections.ChainMap(md, *cmds)  # type: ignore

        setattr(cls, PARAMS_ATTR, Params(**pkw))
        setattr(cls, METADATA_ATTR, types.MappingProxyType(md))

        return process_class(cls)

    if cls is None:
        return wrap

    return wrap(cls)


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

        reorder=MISSING,
        cache_hash=MISSING,
        generic_init=MISSING,
        override=MISSING,
        repr_id=MISSING,
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

        reorder=reorder,
        cache_hash=cache_hash,
        generic_init=generic_init,
        override=override,
        repr_id=repr_id,
    )


class _ExtraParamsKwargs:
    pass


def extra_params(  # noqa
        *,
        reorder=MISSING,
        cache_hash=MISSING,
        generic_init=MISSING,
        override=MISSING,
        repr_id=MISSING,
):
    def inner(cls):
        if PARAMS_ATTR in cls.__dict__:
            raise TypeError(cls)
        try:
            md = cls.__dict__[METADATA_ATTR]
        except KeyError:
            md = {}
            setattr(cls, METADATA_ATTR, md)
        if _ExtraParamsKwargs in md:
            raise TypeError(cls)

        md[_ExtraParamsKwargs] = _strip_missing_values(dict(
            reorder=reorder,
            cache_hash=cache_hash,
            generic_init=generic_init,
            override=override,
            repr_id=repr_id,
        ))

        return cls
    return inner
