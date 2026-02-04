import dataclasses as dc
import typing as ta

from ... import check
from ... import lang
from ..base.configs import Config
from ..naming import Naming
from ..naming import translate_name


##


class TypeTagging(Config, lang.Abstract, lang.Sealed):
    pass


class WrapperTypeTagging(TypeTagging, lang.Final):
    pass


@dc.dataclass(frozen=True)
class FieldTypeTagging(TypeTagging, lang.Final):
    field: str


##


@dc.dataclass(frozen=True)
class Impl(lang.Final):
    ty: type
    tag: str
    alts: ta.AbstractSet[str] = frozenset()

    def __post_init__(self) -> None:
        check.state(not lang.is_abstract(self.ty))


@dc.dataclass(frozen=True)
class ImplBase(lang.Final):
    ty: type
    impls: ta.AbstractSet[str]

    def __post_init__(self) -> None:
        check.state(lang.is_abstract(self.ty))


class Impls(ta.Sequence[Impl], lang.Final):
    def __init__(
            self,
            impls: ta.Iterable[Impl],
            bases: ta.Iterable[ImplBase] | None = None,
    ) -> None:
        super().__init__()

        self._impls = list(impls)

        by_ty: dict[type, Impl] = {}
        by_tag: dict[str, Impl] = {}
        for i in self._impls:
            if i.ty in by_ty:
                raise TypeError(i.ty)
            if i.tag in by_tag:
                raise NameError(i.tag)
            for a in i.alts:
                if a in by_tag:
                    raise NameError(a)
            by_ty[i.ty] = i
            by_tag[i.tag] = i
            for a in i.alts:
                by_tag[a] = i
        self._by_ty = by_ty
        self._by_tag = by_tag

        for b in bases or []:
            raise NotImplementedError

    def __iter__(self) -> ta.Iterator[Impl]:
        return iter(self._impls)

    def __len__(self) -> int:
        return len(self._impls)

    @ta.overload
    def __getitem__(self, index: int) -> Impl: ...

    @ta.overload
    def __getitem__(self, index: slice) -> ta.Sequence[Impl]: ...

    def __getitem__(self, index):
        return self._impls[index]

    @property
    def by_ty(self) -> ta.Mapping[type, Impl]:
        return self._by_ty

    @property
    def by_tag(self) -> ta.Mapping[str, Impl]:
        return self._by_tag


class Polymorphism:
    def __init__(
            self,
            ty: type,
            impls: ta.Iterable[Impl],
    ) -> None:
        super().__init__()

        self._ty = ty
        self._impls = Impls(impls)

        for i in self._impls:
            check.issubclass(i.ty, ty)  # noqa

    @property
    def ty(self) -> type:
        return self._ty

    @property
    def impls(self) -> Impls:
        return self._impls


class AutoStripSuffix(lang.Marker):
    pass


def polymorphism_from_impls(
        ty: type,
        impl_tys: ta.Iterable[type],
        *,
        naming: Naming | None = None,
        strip_suffix: bool | type[AutoStripSuffix] | str = False,
) -> Polymorphism:
    impl_tys = set(impl_tys)

    ssx: str | None
    if strip_suffix is AutoStripSuffix:
        strip_suffix = all(c.__name__.endswith(ty.__name__) for c in impl_tys)
    if isinstance(strip_suffix, bool):
        ssx = ty.__name__ if strip_suffix else None
    elif isinstance(strip_suffix, str):
        ssx = strip_suffix
    else:
        raise TypeError(strip_suffix)

    dct: dict[str, Impl] = {}
    for cur in impl_tys:
        name = cur.__name__
        if ssx is not None:
            name = lang.strip_suffix(name, ssx)
        if naming is not None:
            name = translate_name(name, naming)
        if name in dct:
            raise KeyError(f'Duplicate name: {name}')

        dct[name] = Impl(
            cur,
            name,
        )

    return Polymorphism(ty, dct.values())


def polymorphism_from_subclasses(
        ty: type,
        *,
        naming: Naming | None = None,
        strip_suffix: bool | type[AutoStripSuffix] | str = False,
        include_bases: bool = False,
) -> Polymorphism:
    impl_tys: ta.Iterable[type]
    if include_bases:
        raise NotImplementedError
    else:
        impl_tys = lang.deep_subclasses(ty, concrete_only=True)

    return polymorphism_from_impls(
        ty,
        impl_tys,
        naming=naming,
        strip_suffix=strip_suffix,
    )
