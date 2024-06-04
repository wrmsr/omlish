import collections.abc
import dataclasses as dc
import keyword
import sys
import types
import typing as ta

from ... import check as check_
from .internals import PARAMS_ATTR
from .internals import Params
from .metadata import METADATA_ATTR
from .metadata import Metadata
from .params import FieldExtras
from .params import Params12
from .params import ParamsExtras
from .process import process_class


MISSING = dc.MISSING

IS_12 = sys.version_info[1] >= 12


def field(
        default=MISSING,
        *,
        default_factory=MISSING,
        init=True,
        repr=True,
        hash=None,
        compare=True,
        metadata=None,
        kw_only=MISSING,

        coerce: ta.Optional[ta.Callable[[ta.Any], ta.Any]] = None,
        check: ta.Optional[ta.Callable[[ta.Any], bool]] = None,
        check_type: ta.Optional[bool] = None,
        override: bool = False,
):  # -> dc.Field
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError('cannot specify both default and default_factory')

    fx = FieldExtras(
        coerce=coerce,
        check=check,
        check_type=check_type,
        override=override,
    )

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


def dataclass(
        cls=None,
        /,
        *,
        init=True,
        repr=True,
        eq=True,
        order=False,
        unsafe_hash=False,
        frozen=False,
        match_args=True,
        kw_only=False,
        slots=False,
        weakref_slot=False,

        metadata=None,

        reorder=False,
):
    def wrap(cls):
        pkw = dict(
            init=init,
            repr=repr,
            eq=eq,
            order=order,
            unsafe_hash=unsafe_hash,
            frozen=frozen,
        )
        p12kw = dict(
            match_args=match_args,
            kw_only=kw_only,
            slots=slots,
            weakref_slot=weakref_slot,
        )

        mmd: dict = {
            ParamsExtras: ParamsExtras(
                reorder=reorder,
            ),
        }

        if IS_12:
            pkw.update(p12kw)
        else:
            mmd[Params12] = Params12(**p12kw)

        md: Metadata = mmd
        cmds = []
        if metadata is not None:
            cmds.append(check_.isinstance(metadata, collections.abc.Mapping))
        if (dmd := cls.__dict__.get(METADATA_ATTR)) is not None:
            cmds.append(dmd)
        if cmds:
            md = collections.ChainMap(md, *cmds)  # type: ignore

        setattr(cls, PARAMS_ATTR, Params(**pkw))
        setattr(cls, METADATA_ATTR, types.MappingProxyType(md))

        return process_class(cls)

    if cls is None:
        return wrap

    return wrap(cls)


def make_dataclass(
        cls_name,
        fields,
        *,
        bases=(),
        namespace=None,
        init=True,
        repr=True,
        eq=True,
        order=False,
        unsafe_hash=False,
        frozen=False,
        match_args=True,
        kw_only=False,
        slots=False,
        weakref_slot=False,
        module=None,

        reorder=False,
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
            try:
                module = sys._getframe(1).f_globals.get('__name__', '__main__')  # noqa
            except (AttributeError, ValueError):
                pass
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
    )
