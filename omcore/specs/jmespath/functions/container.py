import typing as ta

from .base import FunctionsClass
from .base import signature
from .types import FunctionContext


T = ta.TypeVar('T')


##


class ContainerFunctions(FunctionsClass):
    @signature({'types': ['array', 'string']}, {'types': [], 'variadic': True}, pass_context=True)
    def _func_contains(self, subject, *searches, ctx: FunctionContext):
        return any(ctx.runtime.contains(subject, search) for search in searches)

    @signature({'types': ['array', 'string']}, {'types': [], 'variadic': True}, pass_context=True)
    def _func_in(self, subject, *searches, ctx: FunctionContext):
        return ctx.runtime.contains(ctx.runtime.make_array(searches), subject)

    @signature({'types': ['string', 'array', 'object']}, pass_context=True)
    def _func_length(self, arg, *, ctx: FunctionContext):
        return ctx.runtime.length(arg)

    @signature({'types': ['array', 'string']})
    def _func_reverse(self, arg):
        if isinstance(arg, str):
            return arg[::-1]
        else:
            return list(reversed(arg))

    @signature({'types': ['expref']}, {'types': ['array']}, pass_context=True)
    def _func_map(self, expref, arg, *, ctx: FunctionContext):
        return ctx.runtime.make_array(
            expref.visit(expref.expression, element)
            for element in ctx.runtime.iter_array_or_raise(arg)
        )

    @signature({'types': ['object'], 'variadic': True}, pass_context=True)
    def _func_merge(self, *arguments, ctx: FunctionContext):
        merged: dict[str, ta.Any] = {}
        for arg in arguments:
            merged.update(ctx.runtime.iter_object_items_or_raise(arg))
        return ctx.runtime.make_object(merged)

    @signature({'types': ['array-string', 'array-number']}, pass_context=True)
    def _func_sort(self, arg, *, ctx: FunctionContext):
        return ctx.runtime.make_array(sorted(ctx.runtime.array_items(arg)))

    @signature({'types': ['array'], 'variadic': True}, pass_context=True)
    def _func_zip(self, *arguments, ctx: FunctionContext):
        arrays = [ctx.runtime.iter_array_or_raise(arg) for arg in arguments]
        return ctx.runtime.make_array(ctx.runtime.make_array(t) for t in zip(*arrays))
