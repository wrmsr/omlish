# ruff: noqa: UP007
import dataclasses as dc
import typing as ta


##


@dc.dataclass(frozen=True)
class AttrRepr:
    attrs: ta.Sequence[str]

    # _: dc.KW_ONLY

    with_module: bool = False
    use_qualname: bool = False
    with_id: bool = False
    value_filter: ta.Optional[ta.Callable[[ta.Any], bool]] = None
    recursive: bool = False

    @classmethod
    def of(cls, *attrs: str, **kwargs: ta.Any) -> 'AttrRepr':
        return cls(attrs, **kwargs)

    #

    def _build_(self, obj: ta.Any) -> str:
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

    _build: ta.ClassVar[ta.Callable[[ta.Any], str]]

    def __call__(self, obj: ta.Any) -> str:
        try:
            build: ta.Any = self._build

        except AttributeError:
            build = self._build_
            if self.recursive:
                build = self._reprlib().recursive_repr()(build)
            object.__setattr__(self, '_build', build)

        return build(obj)

    #

    def __get__(self, instance, owner):
        if instance is None:
            return self

        def __repr__(other):  # noqa
            return self(other)

        return __repr__.__get__(instance, owner)

    #

    _reprlib_: ta.ClassVar[ta.Any]

    @classmethod
    def _reprlib(cls) -> ta.Any:
        try:
            return cls._reprlib_
        except AttributeError:
            pass

        reprlib = __import__('reprlib')
        cls._reprlib_ = reprlib
        return reprlib


def attr_repr(obj: ta.Any, *attrs: str, **kwargs: ta.Any) -> str:
    return AttrRepr(attrs, **kwargs)(obj)
