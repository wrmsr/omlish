import typing as ta

from textual.dom import DOMNode


T = ta.TypeVar('T')


##


@ta.overload
def find_ancestor(flt: ta.Callable[[DOMNode], bool], no: DOMNode) -> DOMNode | None: ...


@ta.overload
def find_ancestor(flt: type[T], no: DOMNode) -> T | None: ...


def find_ancestor(flt, no):
    if isinstance(flt, type):
        flt = (lambda ty: lambda x: isinstance(x, ty))(flt)  # noqa

    while (no := no.parent) is not None:
        if flt(no):
            return no

    return None
