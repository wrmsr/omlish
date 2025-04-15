# ruff: noqa: UP006
import dataclasses as dc
import typing as ta


##


@dc.dataclass(frozen=True)
class AttrRepr:
    attrs: ta.Sequence[str]

    _: dc.KW_ONLY

    with_module: bool = False
    use_qualname: bool = False
    with_id: bool = False
    value_filter: ta.Optional[ta.Callable[[ta.Any], bool]] = None

    @classmethod
    def of(cls, *attrs: str, **kwargs: ta.Any) -> 'AttrRepr':
        return cls(attrs, **kwargs)

    def __call__(self, obj: ta.Any) -> str:
        vs = ', '.join(
            f'{attr}={v!r}'
            for attr in self.attrs
            for v in [getattr(obj, attr)]
            if self.value_filter is None or self.value_filter(v)
        )
        return (
            f'{obj.__class__.__module__ + "." if self.with_module else ""}'
            f'{obj.__class__.__qualname__ if self.use_qualname else obj.__class__.__name__}'
            f'{("@" + hex(id(obj))[2:]) if self.with_id else ""}'
            f'({vs})'
        )

    def __get__(self, instance, owner):
        if instance is None:
            return self
        def __repr__(other):  # noqa
            return self(other)
        return __repr__.__get__(instance, owner)


def attr_repr(obj: ta.Any, *attrs: str, **kwargs: ta.Any) -> str:
    return AttrRepr(attrs, **kwargs)(obj)
