"""
TODO:
 - auto-gen from __subclasses__ if abstract
  - cfg: unless prefixed with _ or abstract
 - auto-name
"""
import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class Impl:
    ty: type
    tag: str
    alts: ta.AbstractSet[str] = frozenset()


class Polymorphism:
    def __init__(self, ty: type, impls: ta.Iterable[Impl]) -> None:
        super().__init__()
        self._ty = ty
        self._impls = list(impls)

        by_ty: dict[type, Impl] = {}
        by_tag: dict[str, Impl] = {}
        for i in self._impls:
            if not issubclass(i.ty, ty) or i.ty in by_ty:
                raise TypeError(i.ty, ty)
            if i.tag in by_tag:
                raise NameError(i.tag)
            for a in i.alts:
                if a in by_tag:
                    raise NameError(a)
            by_ty[i.ty] = i
            by_tag[i.tag] = i
            for a in i.alts:
                by_tag[a] = i
