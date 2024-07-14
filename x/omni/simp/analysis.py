import typing as ta

from . import nodes as no
from .. import dispatch
from .. import lang
from .utils import memoized_unary


T = ta.TypeVar('T')


class Analyzer(dispatch.Class, lang.Abstract, ta.Generic[T]):
    _process = dispatch.property()

    __call__ = memoized_unary(_process, identity=True, max_recursion=100)

    def _process(self, node: no.Node) -> T:  # noqa
        raise TypeError(node)
