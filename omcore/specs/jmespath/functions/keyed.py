import typing as ta

from ..errors import JmespathTypeError
from .base import FunctionsClass
from .base import signature
from .types import FunctionContext


T = ta.TypeVar('T')


##


class KeyedFunctions(FunctionsClass):
    def _create_key_func(self, expref, allowed_types, function_name, *, ctx: FunctionContext):
        def keyfunc(x):
            result = expref.visit(expref.expression, x)
            jmespath_type = ctx.runtime.type_of(result)
            # allowed_types is in terms of jmespath types, not python types.
            if jmespath_type not in allowed_types:
                raise JmespathTypeError(
                    function_name, result, jmespath_type, allowed_types)

            return result

        return keyfunc

    @signature({'types': ['array']}, {'types': ['expref']}, pass_context=True)
    def _func_sort_by(self, array, expref, *, ctx: FunctionContext):
        items = ctx.runtime.array_items(array)
        if not items:
            return array

        # sort_by allows for the expref to be either a number of a string, so we have some special logic to handle this.
        # We evaluate the first array element and verify that it's either a string of a number.  We then create a key
        # function that validates that type, which requires that remaining array elements resolve to the same type as
        # the first element.
        required_type = ctx.runtime.type_of(expref.visit(expref.expression, items[0]))
        if required_type not in ['number', 'string']:
            raise JmespathTypeError(
                'sort_by',
                items[0],
                required_type,
                ['string', 'number'],
            )

        keyfunc = self._create_key_func(expref, [required_type], 'sort_by', ctx=ctx)
        return ctx.runtime.make_array(sorted(items, key=keyfunc))

    @signature({'types': ['array']}, {'types': ['expref']}, pass_context=True)
    def _func_min_by(self, array, expref, *, ctx: FunctionContext):
        keyfunc = self._create_key_func(
            expref,
            ['number', 'string'],
            'min_by',
            ctx=ctx,
        )

        items = ctx.runtime.array_items(array)
        if items:
            return min(items, key=keyfunc)
        else:
            return None

    @signature({'types': ['array']}, {'types': ['expref']}, pass_context=True)
    def _func_max_by(self, array, expref, *, ctx: FunctionContext):
        keyfunc = self._create_key_func(
            expref,
            ['number', 'string'],
            'max_by',
            ctx=ctx,
        )

        items = ctx.runtime.array_items(array)
        if items:
            return max(items, key=keyfunc)
        else:
            return None

    @signature({'types': ['array']}, {'types': ['expref']}, pass_context=True)
    def _func_group_by(self, array, expref, *, ctx: FunctionContext):
        keyfunc = self._create_key_func(expref, ['null', 'string'], 'group_by', ctx=ctx)
        items = ctx.runtime.array_items(array)
        if not items:
            return None

        result: dict[str, ta.Any] = {}
        keys = list(dict.fromkeys([keyfunc(item) for item in items if keyfunc(item) is not None]))
        for key in keys:
            grouped_items = [item for item in items if keyfunc(item) == key]
            result.update({key: ctx.runtime.make_array(grouped_items)})

        return ctx.runtime.make_object(result)
