from omnibus import lang

from .base import Expr
from .select import Relation


class Jinja(lang.Abstract):
    pass


class JinjaExpr(Expr, Jinja):
    text: str


class JinjaRelation(Relation, Jinja):
    text: str


class InJinja(Expr, Jinja):
    needle: Expr
    text: str
    not_: bool = False
