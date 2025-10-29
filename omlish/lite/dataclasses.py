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


def dataclass_cache_hash(
        *,
        cached_hash_attr: str = '__dataclass_hash__',
):
    def inner(cls):
        if not isinstance(cls, type) and dc.is_dataclass(cls):
            raise TypeError(cls)

        if (
                cls.__hash__ is object.__hash__ or
                '__hash__' not in cls.__dict__
        ):
            raise TypeError(cls)

        real_hash = cls.__hash__

        def cached_hash(self) -> int:
            try:
                return object.__getattribute__(self, cached_hash_attr)
            except AttributeError:
                object.__setattr__(self, cached_hash_attr, h := real_hash(self))  # type: ignore[call-arg]
            return h

        cls.__hash__ = cached_hash  # type: ignore[method-assign]

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


def dataclass_repr_filtered(
        obj: ta.Any,
        fn: ta.Callable[[ta.Any, dc.Field, ta.Any], bool],
) -> str:
    return (
        f'{obj.__class__.__qualname__}(' +
        ', '.join([
            f'{f.name}={v!r}'
            for f in dc.fields(obj)
            if fn(obj, f, v := getattr(obj, f.name))
        ]) +
        ')'
    )


def dataclass_repr_omit_none(obj: ta.Any) -> str:
    return dataclass_repr_filtered(obj, lambda o, f, v: v is not None)


def dataclass_repr_omit_falsey(obj: ta.Any) -> str:
    return dataclass_repr_filtered(obj, lambda o, f, v: bool(v))


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


def dataclass_kw_only_init():
    def inner(cls):
        if not isinstance(cls, type) and dc.is_dataclass(cls):
            raise TypeError(cls)

        real_init = cls.__init__  # type: ignore[misc]

        flds = dc.fields(cls)  # noqa

        if any(f.name == 'self' for f in flds):
            self_name = '__dataclass_self__'
        else:
            self_name = 'self'

        src = '\n'.join([
            'def __init__(',
            f'    {self_name},',
            '    *,',
            *[
                ''.join([
                    f'    {f.name}: __dataclass_type_{f.name}__',
                    f' = __dataclass_default_{f.name}__' if f.default is not dc.MISSING else '',
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
            ],
            '    )',
        ])

        ns: dict = {
            '__dataclass_None__': None,
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

        cls.__init__ = kw_only_init  # type: ignore[misc]

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
