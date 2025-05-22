import types
import typing as ta

from .descriptors import unwrap_func


##


class _EmptyClass:
    pass


_OVERRIDE_NOT_NEEDED_ATTRS: ta.AbstractSet[str] = {
    *_EmptyClass.__dict__,
}


def needs_override(attr: str, obj: ta.Any) -> bool:
    if attr in _OVERRIDE_NOT_NEEDED_ATTRS:
        return False

    return True


##


def is_override(obj: ta.Any) -> bool:
    if isinstance(obj, types.FunctionType):
        fn = unwrap_func(obj)
        if getattr(fn, '__override__', False):
            return True

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
