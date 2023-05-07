"""
TODO:
 - terse serde likc iw
 - coercion
"""
import string
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import nodal


class NodeAnnotation(nodal.Annotation):
    pass


class Node(nodal.Nodal['Node', NodeAnnotation]):
    pass


_IDENT_START_CHARS: ta.AbstractSet[str] = {*string.ascii_letters, '_'}
_IDENT_CHARS: ta.AbstractSet[str] = {*_IDENT_START_CHARS, *map(str, range(10))}


def is_ident(s: str) -> bool:
    return (
            s and
            isinstance(s, str) and
            s[0] in _IDENT_START_CHARS and
            not (set(s) - _IDENT_CHARS)
    )


def check_ident(s: str) -> str:
    check.arg(is_ident(s))
    return s


class Ident(Node):
    s: str = dc.field(check=check_ident)


class Annotated(dc.Data, frozen=True, abstract=True, reorder=True):
    annotation: ta.Optional['Expr'] = None


class Expr(Node, abstract=True):
    pass


class Stmt(Node, abstract=True):
    pass


class Def(Node, abstract=True):
    pass


class Module(Node):
    defs: ta.Sequence[Def]
