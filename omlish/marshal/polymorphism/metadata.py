import dataclasses as dc
import typing as ta

from ... import lang
from ..naming import Naming
from ..naming import translate_name
from ..registries import RegistryItem


##


class TypeTagging(RegistryItem, lang.Abstract, lang.Sealed):
    pass


class WrapperTypeTagging(TypeTagging, lang.Final):
    pass


@dc.dataclass(frozen=True)
class FieldTypeTagging(TypeTagging, lang.Final):
    field: str


##


@dc.dataclass(frozen=True)
class Impl:
    ty: type
    tag: str
    alts: ta.AbstractSet[str] = frozenset()


class Impls(ta.Sequence[Impl]):
    def __init__(
            self,
            lst: ta.Iterable[Impl],
    ) -> None:
        super().__init__()
        self._lst = list(lst)

        by_ty: dict[type, Impl] = {}
        by_tag: dict[str, Impl] = {}
        for i in self._lst:
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
        return iter(self._lst)

    def __len__(self) -> int:
        return len(self._lst)

    @ta.overload
    def __getitem__(self, index: int) -> Impl: ...

    @ta.overload
    def __getitem__(self, index: slice) -> ta.Sequence[Impl]: ...

    def __getitem__(self, index):
        return self._lst[index]

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
            if not issubclass(i.ty, ty):
                raise TypeError(i.ty, ty)

    @property
    def ty(self) -> type:
        return self._ty

    @property
    def impls(self) -> Impls:
        return self._impls


def polymorphism_from_subclasses(
        ty: type,
        *,
        naming: Naming | None = None,
        strip_suffix: bool | ta.Literal['auto'] = False,
) -> Polymorphism:
    seen: set[type] = set()
    todo: list[type] = [ty]
    impls: set[type] = set()
    while todo:
        cur = todo.pop()
        seen.add(cur)

        todo.extend(nxt for nxt in cur.__subclasses__() if nxt not in seen)

        if lang.is_abstract_class(cur):
            continue

        impls.add(cur)

    if strip_suffix == 'auto':
        strip_suffix = all(c.__name__.endswith(ty.__name__) for c in impls)

    dct: dict[str, Impl] = {}
    for cur in impls:
        name = cur.__name__
        if strip_suffix:
            name = lang.strip_suffix(name, ty.__name__)
        if naming is not None:
            name = translate_name(name, naming)
        if name in dct:
            raise KeyError(f'Duplicate name: {name}')

        dct[name] = Impl(
            cur,
            name,
        )

    return Polymorphism(ty, dct.values())
