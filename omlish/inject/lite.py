"""
TODO:
 - explicit blacklisted key element - blacklist lite Injector
"""
import dataclasses as dc
import typing as ta

from .. import check
from .. import reflect as rfl
from ..lite import inject as lij
from .bindings import Binding
from .elements import Elements
from .keys import Key
from .providers import ConstProvider
from .providers import CtorProvider
from .providers import FnProvider
from .providers import LinkProvider
from .providers import Provider
from .scopes import Singleton
from .types import Scope
from .types import Unscoped


##


@dc.dataclass(frozen=True)
class BoxedLiteProvider:
    p: Provider
    sc: Scope | None = None


##


@ta.overload
def convert_from_lite(o: lij.InjectorBindings) -> Elements:
    ...


@ta.overload
def convert_from_lite(o: lij.InjectorKey) -> Key:
    ...


@ta.overload
def convert_from_lite(o: lij.InjectorBinding) -> Binding:
    ...


@ta.overload
def convert_from_lite(o: lij.InjectorProvider) -> BoxedLiteProvider:
    ...


def convert_from_lite(o):
    if isinstance(o, lij.InjectorBindings):
        return Elements([
            convert_from_lite(c)
            for c in o.bindings()
        ])

    elif isinstance(o, lij.InjectorKey):
        check.not_equal(o.cls_, lij.InjectorKeyCls)
        check.arg(not o.array)
        return Key(rfl.type_(o.cls_), tag=o.tag)

    elif isinstance(o, lij.InjectorBinding):
        blp = convert_from_lite(o.provider)
        return Binding(
            convert_from_lite(o.key),
            blp.p,
            blp.sc if blp.sc is not None else Unscoped(),
        )

    elif isinstance(o, lij.InjectorProvider):
        if isinstance(o, lij.FnInjectorProvider):
            return BoxedLiteProvider(FnProvider(
                o.fn,
            ))

        elif isinstance(o, lij.CtorInjectorProvider):
            return BoxedLiteProvider(CtorProvider(
                o.cls_,
            ))

        elif isinstance(o, lij.ConstInjectorProvider):
            return BoxedLiteProvider(ConstProvider(
                o.v,
            ))

        elif isinstance(o, lij.SingletonInjectorProvider):
            blp = convert_from_lite(o.p)
            check.none(blp.sc)
            return dc.replace(
                blp,
                sc=Singleton(),
            )

        elif isinstance(o, lij.LinkInjectorProvider):
            return BoxedLiteProvider(LinkProvider(
                convert_from_lite(o.k),
            ))

        elif isinstance(o, lij.ScopedInjectorProvider):
            raise NotImplementedError

        else:
            raise TypeError(o)

    else:
        raise TypeError(o)
