# ruff: noqa: UP006 UP007 UP045
import dataclasses as dc
import functools
import typing as ta


##


def dataclass_shallow_astuple(o: ta.Any) -> ta.Tuple[ta.Any, ...]:
    return tuple(getattr(o, f.name) for f in dc.fields(o))


def dataclass_shallow_asdict(o: ta.Any) -> ta.Dict[str, ta.Any]:
    return {f.name: getattr(o, f.name) for f in dc.fields(o)}


##


def is_immediate_dataclass(cls: type) -> bool:
    if not isinstance(cls, type):
        raise TypeError(cls)
    return dc._FIELDS in cls.__dict__  # type: ignore[attr-defined]  # noqa


##


def _install_dataclass_fn(cls: type, fn: ta.Any, fn_name: ta.Optional[str] = None) -> None:
    if fn_name is None:
        fn_name = fn.__name__
    setattr(cls, fn_name, fn)
    fn.__qualname__ = f'{cls.__qualname__}.{fn_name}'


##


def install_dataclass_cache_hash(
        *,
        cached_hash_attr: str = '__dataclass_hash__',
):
    def inner(cls):
        if not (isinstance(cls, type) and dc.is_dataclass(cls)):
            raise TypeError(cls)

        # dict lookup, not attribute - an eq=True/frozen=False dataclass sets __hash__ to None in the class dict, which
        # is just as unusable here as an absent or inherited one.
        if (
                (real_hash := cls.__dict__.get('__hash__')) is None or
                real_hash is object.__hash__
        ):
            raise TypeError(cls)

        def cached_hash(self) -> int:
            try:
                return object.__getattribute__(self, cached_hash_attr)
            except AttributeError:
                object.__setattr__(self, cached_hash_attr, h := real_hash(self))
            return h

        _install_dataclass_fn(cls, cached_hash, '__hash__')

        return cls

    return inner


##


def dataclass_maybe_post_init(sup: ta.Any) -> bool:
    if not isinstance(sup, super):
        raise TypeError(sup)
    try:
        fn = sup.__post_init__  # type: ignore
    except AttributeError:
        return False
    fn()
    return True


##


def dataclass_repr(
        obj: ta.Any,
        *,
        terse: bool = False,
        filter: ta.Union[  # noqa
            ta.Callable[[ta.Any, dc.Field, ta.Any], bool],
            ta.Literal['omit_none', 'omit_falsey'],
            None,
        ] = None,
) -> str:
    if filter == 'omit_none':
        filter = lambda o, f, v: v is not None  # noqa
    elif filter == 'omit_falsey':
        filter = lambda o, f, v: bool(v)  # noqa

    lst: ta.List[str] = [
        f'{obj.__class__.__qualname__}(',
    ]

    i = 0
    for f in dc.fields(obj):
        if not f.repr:
            continue

        v = getattr(obj, f.name)

        if filter is not None and not filter(obj, f, v):
            continue

        if i:
            lst.append(', ')
        i += 1

        if not terse:
            lst.append(f.name)
            lst.append('=')

        lst.append(repr(v))

    lst.append(')')

    return ''.join(lst)


def dataclass_repr_omit_none(obj: ta.Any) -> str:
    return dataclass_repr(obj, filter='omit_none')


def dataclass_repr_omit_falsey(obj: ta.Any) -> str:
    return dataclass_repr(obj, filter='omit_falsey')


def install_dataclass_repr(
        *,
        terse: bool = False,
        filter: ta.Union[  # noqa
            ta.Callable[[ta.Any, dc.Field, ta.Any], bool],
            ta.Literal['omit_none', 'omit_falsey'],
            None,
        ] = None,
):
    def inner(cls):
        if not (isinstance(cls, type) and dc.is_dataclass(cls)):
            raise TypeError(cls)

        def repr_impl(self) -> str:
            return dataclass_repr(
                self,
                terse=terse,
                filter=filter,
            )

        _install_dataclass_fn(cls, repr_impl, '__repr__')

        return cls

    return inner


##


def dataclass_descriptor_method(*bind_attrs: str, bind_owner: bool = False) -> ta.Callable:
    if not bind_attrs:
        def __get__(self, instance, owner=None):  # noqa
            return self

    elif bind_owner:
        def __get__(self, instance, owner=None):  # noqa
            # Guaranteed to return a new instance even with no attrs
            return dc.replace(self, **{
                a: v.__get__(instance, owner) if (v := getattr(self, a)) is not None else None
                for a in bind_attrs
            })

    else:
        def __get__(self, instance, owner=None):  # noqa
            if instance is None:
                return self

            # Guaranteed to return a new instance even with no attrs
            return dc.replace(self, **{
                a: v.__get__(instance, owner) if (v := getattr(self, a)) is not None else None
                for a in bind_attrs
            })

    return __get__


##


def install_dataclass_kw_only_init():
    def inner(cls):
        if not (isinstance(cls, type) and dc.is_dataclass(cls)):
            raise TypeError(cls)

        real_init = cls.__init__

        # The real __init__'s params are the init=True fields plus InitVar pseudo-fields (which dc.fields omits), in
        # field order - init=False fields must be excluded or the generated call will not match its signature.
        flds = [
            f
            for f in getattr(cls, dc._FIELDS).values()  # type: ignore[attr-defined]  # noqa
            if f._field_type is dc._FIELD_INITVAR or (f._field_type is dc._FIELD and f.init)  # type: ignore[attr-defined]  # noqa
        ]

        if any(f.name == 'self' for f in flds):
            self_name = '__dataclass_self__'
        else:
            self_name = 'self'

        # default_factory fields cannot have their default baked into the signature - a MISSING sentinel default is
        # filtered out of the forwarded kwargs so the real init invokes the factory per-call.
        src = '\n'.join([
            'def __init__(',
            f'    {self_name},',
            '    *,',
            *[
                ''.join([
                    f'    {f.name}: __dataclass_type_{f.name}__',
                    (
                        f' = __dataclass_default_{f.name}__' if f.default is not dc.MISSING else
                        ' = __dataclass_MISSING__' if f.default_factory is not dc.MISSING else  # noqa
                        ''
                    ),
                    ',',
                ])
                for f in flds
            ],
            ') -> __dataclass_None__:',
            '    __dataclass_real_init__(',
            f'        {self_name},',
            *[
                f'        {f.name}={f.name},'
                for f in flds
                if f.default_factory is dc.MISSING  # noqa
            ],
            '        **{',
            '            k: v',
            '            for k, v in [',
            *[
                f'                ({f.name!r}, {f.name}),'
                for f in flds
                if f.default_factory is not dc.MISSING  # noqa
            ],
            '            ]',
            '            if v is not __dataclass_MISSING__',
            '        },',
            '    )',
        ])

        ns: dict = {
            '__dataclass_None__': None,
            '__dataclass_MISSING__': dc.MISSING,
            '__dataclass_real_init__': real_init,
            **{
                f'__dataclass_type_{f.name}__': f.type
                for f in flds
            },
            **{
                f'__dataclass_default_{f.name}__': f.default
                for f in flds
                if f.default is not dc.MISSING
            },
        }

        exec(src, ns)

        kw_only_init = ns['__init__']

        functools.update_wrapper(kw_only_init, real_init)

        _install_dataclass_fn(cls, kw_only_init, '__init__')

        return cls

    return inner


##


@dc.dataclass()
class DataclassFieldRequiredError(Exception):
    name: str


def dataclass_field_required(name: str) -> ta.Callable[[], ta.Any]:
    def inner() -> ta.NoReturn:
        raise DataclassFieldRequiredError(name)
    return inner
