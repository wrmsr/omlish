import typing as ta

from ... import check
from ... import dataclasses as dc
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


class Impls(ta.Sequence[Impl], lang.Final):
    def __init__(self, impls: ta.Iterable[Impl]) -> None:
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


@dc.dataclass(frozen=True)
class ImplBase(lang.Final):
    ty: type
    impl_tys: ta.AbstractSet[type]

    def __post_init__(self) -> None:
        check.not_empty(self.impl_tys)
        for i in self.impl_tys:
            check.issubclass(i, self.ty)
            check.state(not lang.is_abstract(i))


class ImplBases(ta.Sequence[ImplBase], lang.Final):
    def __init__(self, bases: ta.Iterable[ImplBase]) -> None:
        super().__init__()

        self._bases = list(bases)

        by_ty: dict[type, ImplBase] = {}
        for i in self._bases:
            if i.ty in by_ty:
                raise TypeError(i.ty)
            by_ty[i.ty] = i
        self._by_ty = by_ty

    def __iter__(self) -> ta.Iterator[ImplBase]:
        return iter(self._bases)

    def __len__(self) -> int:
        return len(self._bases)

    @ta.overload
    def __getitem__(self, index: int) -> ImplBase: ...

    @ta.overload
    def __getitem__(self, index: slice) -> ta.Sequence[ImplBase]: ...

    def __getitem__(self, index):
        return self._bases[index]

    @property
    def by_ty(self) -> ta.Mapping[type, ImplBase]:
        return self._by_ty


class Polymorphism:
    def __init__(
            self,
            ty: type,
            impls: Impls | ta.Iterable[Impl],
            *,
            bases: ImplBases | ta.Iterable[ImplBase] | None = None,
    ) -> None:
        super().__init__()

        self._ty = ty
        self._impls = impls if isinstance(impls, Impls) else Impls(impls)
        self._bases = bases if isinstance(bases, ImplBases) else ImplBases(bases) if bases is not None else None

        for i in self._impls:
            check.issubclass(i.ty, ty)  # noqa

        if self._bases is not None:
            for b in self._bases:
                check.issubclass(b.ty, ty)

    @property
    def ty(self) -> type:
        return self._ty

    @property
    def impls(self) -> Impls:
        return self._impls

    @property
    def bases(self) -> ImplBases | None:
        return self._bases


class AutoStripSuffix(lang.Marker):
    pass


def polymorphism_from_impls(
        ty: type,
        impl_tys: ta.Iterable[type],
        *,
        base_tys: ta.Mapping[type, ta.Iterable[type]] | None = None,
        naming: Naming | None = None,
        strip_suffix: bool | type[AutoStripSuffix] | str = False,
) -> Polymorphism:
    impl_tys = set(impl_tys)

    bases: ta.Sequence[ImplBase] | None = None
    if base_tys is not None:
        bases = [
            ImplBase(
                b_ty,
                frozenset(b_sub_tys),
            )
            for b_ty, b_sub_tys in base_tys.items()
        ]

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

    return Polymorphism(
        ty,
        dct.values(),
        bases=bases,
    )


def polymorphism_from_subclasses(
        ty: type,
        *,
        include_bases: bool = False,
        naming: Naming | None = None,
        strip_suffix: bool | type[AutoStripSuffix] | str = False,
) -> Polymorphism:
    impl_tys: set[type]
    base_tys: dict[type, set[type]] | None
    if include_bases:
        dct: dict = lang.deep_subclass_tree(ty, total=True, concrete_only=True)
        base_tys = {bt: bts for bt, bts in dct.items() if bts}
        impl_tys = {sub_ty for sub_ty in dct if not lang.is_abstract(sub_ty)}
    else:
        impl_tys = set(lang.deep_subclasses(ty, concrete_only=True))
        base_tys = None

    return polymorphism_from_impls(
        ty,
        impl_tys,
        base_tys=base_tys,
        naming=naming,
        strip_suffix=strip_suffix,
    )
