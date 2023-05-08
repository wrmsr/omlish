import functools
import typing as ta

from ... import nodes as no
from .... import check
from .... import dataclasses as dc
from .... import lang
from ..types import Args
from ..types import Macro
from ..types import Matcher
from ..types import Xlat
from .default import DEFAULT_MACROS


class DynamicMacro(dc.Frozen, allow_setattr=True):
    match: Matcher
    fn: Macro

    def __call__(self, xlat: Xlat, args: Args) -> no.Node:
        return self.fn(xlat, args)


def dynamic_macro(
        match: Matcher,
        *,
        default: bool = False,
        register_on: ta.Iterable[ta.MutableSequence[Macro]] = (),
) -> ta.Callable[..., Macro]:
    def inner(fn):
        m = DynamicMacro(match, fn)
        functools.update_wrapper(m, fn)
        for r in register_on:
            r.append(m)
        return m

    check.isinstance(match, (lang.Callable, bool))
    register_on = list(register_on)
    if default:
        register_on.append(DEFAULT_MACROS)
    for r in register_on:
        check.not_isinstance(r, ta.Mapping)
    return inner


def tag_matcher(fn: ta.Callable[[str], bool]) -> Matcher:
    def inner(args: Args) -> bool:
        return args and isinstance(args[0], str) and fn(args[0])
    return inner


@dynamic_macro(tag_matcher(lambda tag: tag[0] == '~'), default=True)
def tilde_const(xlat: Xlat, args: Args) -> no.Node:
    args = list(args)
    tag = args.pop(0)
    check.empty(args)
    return no.Const(tag[1:])


@dynamic_macro(tag_matcher(lambda tag: tag[0] == '.' and tag[-1] == '=' and no.is_ident(tag[1:-1])), default=True)
def set_attr(xlat: Xlat, args: Args) -> no.Node:
    args = list(args)
    tag = args.pop(0)
    att = no.Ident(tag[1:-1])
    obj = xlat(args.pop(0))
    value = xlat(check.single(args))
    return no.SetAttr(
        obj,
        att,
        value,
    )


@dynamic_macro(tag_matcher(lambda tag: tag[0] == '.' and no.is_ident(tag[1:])), default=True)
def get_attr(xlat: Xlat, args: Args) -> no.Node:
    args = list(args)
    tag = args.pop(0)
    att = no.Ident(tag[1:])
    value = xlat(check.single(args))
    return no.GetAttr(
        value,
        att,
    )


@dynamic_macro(tag_matcher(lambda tag: tag[-1] == '=' and no.is_ident(tag[:-1])), default=True)
def set_var(xlat: Xlat, args: Args) -> no.Node:
    args = list(args)
    tag = args.pop(0)
    name = no.Ident(tag[:-1])
    value = xlat(check.single(args))
    return no.SetVar(
        name,
        value,
    )


@dynamic_macro(True, default=True)
def call(xlat: Xlat, args: Args) -> no.Node:
    args = list(args)
    tag = args.pop(0)
    fn = xlat(tag)
    cargs = []
    for a in args:
        xa = xlat(a)
        if isinstance(xa, no.Expr):
            xe = xa
        else:
            raise TypeError(xa)
        cargs.append(xe)
    return no.Call(
        fn,
        cargs,
    )
