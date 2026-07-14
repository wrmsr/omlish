import json
import typing as ta

from .base import FunctionsClass
from .base import signature
from .types import FunctionContext


T = ta.TypeVar('T')


##


class TypeFunctions(FunctionsClass):
    @signature({'types': []}, pass_context=True)
    def _func_type(self, arg, *, ctx: FunctionContext):
        value_type = ctx.runtime.type_of(arg)
        if value_type == 'unknown':
            return None
        return value_type

    @signature({'types': [], 'variadic': True})
    def _func_not_null(self, *arguments):
        for argument in arguments:
            if argument is not None:
                return argument
        return None

    @signature({'types': []}, pass_context=True)
    def _func_to_array(self, arg, *, ctx: FunctionContext):
        if ctx.runtime.type_of(arg) == 'array':
            return arg
        else:
            return ctx.runtime.make_array([arg])

    @signature({'types': []}, pass_context=True)
    def _func_to_string(self, arg, *, ctx: FunctionContext):
        if ctx.runtime.type_of(arg) == 'string':
            return arg
        else:
            return json.dumps(ctx.runtime.to_python(arg), separators=(',', ':'), default=str)

    @signature({'types': []}, pass_context=True)
    def _func_to_number(self, arg, *, ctx: FunctionContext):
        arg_type = ctx.runtime.type_of(arg)
        if arg_type in ('array', 'object', 'boolean', 'null'):
            return None

        elif arg_type == 'number':
            return arg

        else:
            arg = ctx.runtime.to_python(arg)
            try:
                return int(arg)
            except ValueError:
                try:
                    return float(arg)
                except ValueError:
                    return None
