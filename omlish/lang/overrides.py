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
    pass


class RequiresOverride:
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        req_ovr_dct: dict[str, type] = {}
        for m_cls in reversed(cls.__mro__):
            for a, o in m_cls.__dict__.items():
                if a in req_ovr_dct and not is_override(o):
                    raise RequiresOverrideError(
                        f'Attribute {a!r} on class {cls} (from base class {m_cls} is not marked as a @typing.override '
                        f'from base class {req_ovr_dct[a]}',
                    )

            if RequiresOverride in m_cls.__bases__:
                for a, o in m_cls.__dict__.items():
                    if needs_override(a, o):
                        req_ovr_dct.setdefault(a, m_cls)
