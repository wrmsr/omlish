import typing as ta

from .base import FunctionsClass
from .base import signature
from .types import FunctionContext


T = ta.TypeVar('T')


##


class ObjectFunctions(FunctionsClass):
    @signature({'types': ['object']}, pass_context=True)
    def _func_items(self, arg, *, ctx: FunctionContext):
        return ctx.runtime.make_array(ctx.runtime.make_array(t) for t in ctx.runtime.iter_object_items_or_raise(arg))

    @signature({'types': ['array']}, pass_context=True)
    def _func_from_items(self, items, *, ctx: FunctionContext):
        return ctx.runtime.make_object(dict(ctx.runtime.array_items(items)))

    @signature({'types': ['object']}, pass_context=True)
    def _func_keys(self, arg, *, ctx: FunctionContext):
        # To be consistent with .values() should we also return the indices of a list?
        return ctx.runtime.make_array(k for k, _ in ctx.runtime.iter_object_items_or_raise(arg))

    @signature({'types': ['object']}, pass_context=True)
    def _func_values(self, arg, *, ctx: FunctionContext):
        return ctx.runtime.make_array(v for _, v in ctx.runtime.iter_object_items_or_raise(arg))

    @signature({'types': ['expref']}, {'types': ['object']}, pass_context=True)
    def _func_filter_keys(self, expref, arg, *, ctx: FunctionContext):
        return ctx.runtime.make_object({
            k: v
            for k, v in ctx.runtime.iter_object_items_or_raise(arg)
            if expref.visit(expref.expression, k)
        })

    @signature({'types': ['expref']}, {'types': ['object']}, pass_context=True)
    def _func_filter_values(self, expref, arg, *, ctx: FunctionContext):
        return ctx.runtime.make_object({
            k: v
            for k, v in ctx.runtime.iter_object_items_or_raise(arg)
            if expref.visit(expref.expression, v)
        })
