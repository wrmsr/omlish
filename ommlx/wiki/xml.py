"""
TODO:
 - lxml? faster?
  - xml.etree ~60 MiB/s INITIALLY, slows to ~30 MiB/s
  - lxml ~110 MiB/s INITIALLY, slows to ~50 MiB/s
  - https://lxml.de/1.3/compatibility.html
  - https://lxml.de/performance.html
  - https://lxml.de/apidoc/lxml.etree.html#lxml.etree.iterparse
 - https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.XMLPullParser - sans-io
"""
import dataclasses as dc
import typing as ta
import xml.etree.ElementTree as ET

from omlish import check
from omlish import lang


if ta.TYPE_CHECKING:
    import lxml.etree as lxml_etree
else:
    lxml_etree = lang.proxy_import('lxml.etree')


T = ta.TypeVar('T')

Element: ta.TypeAlias = ta.Union[ET.Element, 'lxml_etree.Element']


##


def strip_ns(tag: str) -> str:
    # It really do just be like this:
    # https://github.com/python/cpython/blob/ff3bc82f7c9882c27aad597aac79355da7257186/Lib/xml/etree/ElementTree.py#L803-L804
    if tag[:1] == '{':
        _, tag = tag[1:].rsplit('}', 1)
    return tag


##


ITER_PARSE_EVENTS = ('start', 'end', 'comment', 'pi', 'start-ns', 'end-ns')


def yield_root_children(
        source: ta.Any,
        *,
        retain_on_root: bool = False,
        use_lxml: bool = False,
        **kwargs: ta.Any,
) -> ta.Iterator[Element]:
    if use_lxml:
        parser = lxml_etree.iterparse
    else:
        parser = ET.iterparse
    it = iter(parser(source, ('start', 'end'), **kwargs))

    ev, root = next(it)
    if ev != 'start':
        raise RuntimeError(ev)
    yield root

    depth = 0
    for ev, el in it:
        if ev == 'start':
            depth += 1

        elif ev == 'end':
            depth -= 1
            if not depth:
                if not retain_on_root:
                    root.remove(el)
                yield el


##


@dc.dataclass(frozen=True, kw_only=True)
class ElementToKwargs:
    attrs: ta.Mapping[str, tuple[str, ta.Callable[[str], ta.Any]] | str | None] = dc.field(default_factory=dict)
    scalars: ta.Mapping[str, tuple[str, ta.Callable[[str], ta.Any]] | str | None] = dc.field(default_factory=dict)
    single_children: ta.Mapping[str, tuple[str, ta.Callable[[Element], ta.Any]]] = dc.field(default_factory=dict)
    list_children: ta.Mapping[str, tuple[str, ta.Callable[[Element], ta.Any]]] = dc.field(default_factory=dict)
    text: str | None = None

    def __call__(self, el: Element) -> ta.Mapping[str, ta.Any]:
        kw: dict[str, ta.Any] = {}

        def set_kw(k: str, v: ta.Any) -> None:
            if k in kw:
                raise KeyError(k)
            kw[k] = v

        if el.attrib:
            for k, v in el.attrib.items():
                k = strip_ns(k)

                if k in self.attrs:
                    t = self.attrs[k]
                    if t is not None:
                        if isinstance(t, str):
                            set_kw(t, v)
                        else:
                            ak, fn = t
                            set_kw(ak, fn(v))

                else:
                    raise KeyError(k)

        for cel in el:
            k = strip_ns(cel.tag)

            if k in self.scalars:
                t = self.scalars[k]
                if t is not None:
                    if isinstance(t, str):
                        set_kw(t, cel.text)
                    else:
                        sk, fn = t
                        set_kw(sk, fn(check.not_none(cel.text)))

            elif k in self.single_children:
                ck, fn = self.single_children[k]
                set_kw(ck, fn(cel))

            elif k in self.list_children:
                lk, fn = self.list_children[k]
                kw.setdefault(lk, []).append(fn(cel))

            else:
                raise KeyError(k)

        if self.text is not None:
            set_kw(self.text, el.text)

        return kw


@dc.dataclass(frozen=True)
class ElementToObj(ta.Generic[T]):
    cls: type[T]
    kw: ElementToKwargs

    def __call__(self, el: Element) -> T:
        return self.cls(**self.kw(el))
