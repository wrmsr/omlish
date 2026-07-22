import functools
import types
import typing as ta

from .descriptors import is_method_descriptor


##


def _get_override_not_needed_attrs() -> frozenset[str]:
    class Empty:
        pass

    class Annotated:
        x: int

    ks = {
        *Empty.__dict__,
        *Annotated.__dict__,
    }

    # Annotation machinery may materialize additional class-dict entries lazily (e.g. PEP 649's __annotations_cache__
    # on evaluation) - which can happen to a base class before a subclass is created - so capture those too.
    Annotated.__annotations__  # noqa
    ks.update(Annotated.__dict__)

    ks.discard('x')
    return frozenset(ks)


_OVERRIDE_NOT_NEEDED_ATTRS: ta.AbstractSet[str] = _get_override_not_needed_attrs()


def needs_override(attr: str, obj: ta.Any) -> bool:
    if attr in _OVERRIDE_NOT_NEEDED_ATTRS:
        return False

    return True


##


def is_override(obj: ta.Any) -> bool:
    """
    Checks for a `@typing.override`-set flag at every layer of a wrapper chain - the flag lands on whatever object the
    decorator was applied to, which need not be the innermost function (`@override` atop a wrapping decorator) nor a
    plain function at all (classmethods, staticmethods, properties).
    """

    if isinstance(obj, property):
        return any(
            a is not None and is_override(a)
            for a in (obj.fget, obj.fset, obj.fdel)
        )

    while True:
        if getattr(obj, '__override__', False):
            return True

        if is_method_descriptor(obj) or isinstance(obj, types.MethodType):
            obj = obj.__func__
        elif (nxt := getattr(obj, '__wrapped__', None)) is not None:
            if nxt is obj:
                return False
            obj = nxt
        elif isinstance(obj, functools.partial):
            obj = obj.func
        else:
            return False


##


class RequiresOverrideError(TypeError):
    def __init__(
            self,
            att: str | None = None,
            cls: type | None = None,
            mro_cls: type | None = None,
            owner_cls: type | None = None,
    ) -> None:
        super().__init__(' '.join([
            'Attribute',
            *([f'{att!r}'] if att is not None else []),
            *([f'on class {cls.__qualname__}'] if cls is not None else []),
            *([f'from mro class {mro_cls.__qualname__}'] if mro_cls is not None and mro_cls is not cls else []),
            f'is not marked as a @typing.override',
            *([f'from owning class {owner_cls.__qualname__}'] if owner_cls is not None else []),
        ]))

        self.att = att
        self.cls = cls
        self.mro_cls = mro_cls
        self.owner_cls = owner_cls


class RequiresOverride:
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        req_ovr_dct: dict[str, type] = {}
        for m_cls in reversed(cls.__mro__):
            for a, o in m_cls.__dict__.items():
                if a in req_ovr_dct and not is_override(o):
                    raise RequiresOverrideError(
                        a,
                        cls,
                        m_cls,
                        req_ovr_dct[a],
                    )

            if RequiresOverride in m_cls.__bases__:
                for a, o in m_cls.__dict__.items():
                    if needs_override(a, o):
                        req_ovr_dct.setdefault(a, m_cls)
