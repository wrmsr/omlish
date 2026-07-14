import math
import typing as ta

from .base import FunctionsClass
from .base import signature
from .types import FunctionContext


T = ta.TypeVar('T')


##


class NumberFunctions(FunctionsClass):
    @signature({'types': ['number']})
    def _func_abs(self, arg):
        return abs(arg)

    @signature({'types': ['array-number']}, pass_context=True)
    def _func_avg(self, arg, *, ctx: FunctionContext):
        items = ctx.runtime.array_items(arg)
        if items:
            return sum(items) / len(items)
        else:
            return None

    @signature({'types': ['number']})
    def _func_ceil(self, arg):
        return math.ceil(arg)

    @signature({'types': ['number']})
    def _func_floor(self, arg):
        return math.floor(arg)

    @signature({'types': ['array-number', 'array-string']}, pass_context=True)
    def _func_max(self, arg, *, ctx: FunctionContext):
        items = ctx.runtime.array_items(arg)
        if items:
            return max(items)
        else:
            return None

    @signature({'types': ['array-number', 'array-string']}, pass_context=True)
    def _func_min(self, arg, *, ctx: FunctionContext):
        items = ctx.runtime.array_items(arg)
        if items:
            return min(items)
        else:
            return None

    @signature({'types': ['array-number']}, pass_context=True)
    def _func_sum(self, arg, *, ctx: FunctionContext):
        return sum(ctx.runtime.iter_array_or_raise(arg))
