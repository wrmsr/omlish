import dataclasses as dc
import inspect
import json
import math
import re
import typing as ta

from .errors import ArityError
from .errors import JmespathError
from .errors import JmespathTypeError
from .errors import JmespathValueError
from .errors import UnknownFunctionError
from .errors import VariadicArityError
from .runtime import JmespathType
from .runtime import PythonRuntime
from .runtime import Runtime


T = ta.TypeVar('T')


##


ArrayParameterType: ta.TypeAlias = ta.Literal[
    'array-string',
    'array-number',
]

ParameterType: ta.TypeAlias = JmespathType | ArrayParameterType


class Parameter(ta.TypedDict):
    type: ta.NotRequired[ParameterType]
    types: ta.NotRequired[ta.Sequence[ParameterType]]
    variadic: ta.NotRequired[bool]
    optional: ta.NotRequired[bool]


Signature: ta.TypeAlias = ta.Sequence[Parameter]


@dc.dataclass(frozen=True)
class FunctionContext:
    runtime: Runtime


@dc.dataclass(frozen=True)
class Function:
    function: ta.Callable
    signature: Signature
    pass_context: bool = False


def signature(*params: Parameter, pass_context: bool = False):
    def _record_signature(func):
        func.signature = params
        func.pass_context = pass_context
        return func
    return _record_signature


class Functions(ta.Protocol):
    def call_function(
            self,
            function_name: str,
            resolved_args: ta.Sequence[ta.Any],
            ctx: FunctionContext | None = None,
    ) -> ta.Any:
        ...


class FunctionsClass:
    _function_table: ta.ClassVar[ta.Mapping[str, Function]] = {}  # noqa

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        cls._populate_function_table()

    @classmethod
    def _populate_function_table(cls) -> None:
        function_table: dict[str, Function] = {}

        # Any method with a @signature decorator that also starts with "_func_" is registered as a function.
        # _func_max_by -> max_by function.
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if not name.startswith('_func_'):
                continue

            sig = getattr(method, 'signature', None)
            if sig is not None:
                function_table[name[6:]] = Function(
                    method,
                    sig,
                    getattr(method, 'pass_context', False),
                )

        cls._function_table = function_table

    #

    def call_function(
            self,
            function_name: str,
            resolved_args: ta.Sequence[ta.Any],
            ctx: FunctionContext | None = None,
    ) -> ta.Any:
        if ctx is None:
            ctx = FunctionContext(PythonRuntime())

        try:
            spec = self._function_table[function_name]
        except KeyError:
            raise UnknownFunctionError(f'Unknown function: {function_name}()')  # noqa

        self._validate_arguments(resolved_args, spec.signature, function_name, ctx=ctx)
        func = spec.function.__get__(self, self.__class__)
        if spec.pass_context:
            return func(*resolved_args, ctx=ctx)  # noqa
        else:
            return func(*[ctx.runtime.to_python(arg) for arg in resolved_args])  # noqa

    def _validate_arguments(
            self,
            args: ta.Sequence[ta.Any],
            sig: Signature,
            function_name: str,
            *,
            ctx: FunctionContext | None = None,
    ) -> None:
        if ctx is None:
            ctx = FunctionContext(PythonRuntime())
        if len(sig) == 0:
            self._type_check(args, sig, function_name, ctx=ctx)
            return

        required_arguments_count = len([
            param for param in sig if param and (not param.get('optional') or not param['optional'])
        ])
        optional_arguments_count = len([
            param for param in sig if param and param.get('optional') and param['optional']
        ])
        has_variadic = sig[-1].get('variadic') if sig is not None else False

        if has_variadic:
            if len(args) < len(sig):
                raise VariadicArityError(len(sig), len(args), function_name)

        elif optional_arguments_count > 0:
            if (
                    len(args) < required_arguments_count or
                    len(args) > (required_arguments_count + optional_arguments_count)
            ):
                raise ArityError(len(sig), len(args), function_name)

        elif len(args) != required_arguments_count:
            raise ArityError(len(sig), len(args), function_name)

        self._type_check(args, sig, function_name, ctx=ctx)

    def _type_check(
            self,
            actual: ta.Sequence[ta.Any],
            sig: Signature,
            function_name: str,
            *,
            ctx: FunctionContext,
    ) -> None:
        for i in range(min(len(sig), len(actual))):
            allowed_types = self._get_allowed_types_from_signature(sig[i])
            if allowed_types:
                self._type_check_single(actual[i], allowed_types, function_name, ctx=ctx)

    def _get_allowed_types_from_signature(self, spec: Parameter) -> ta.Sequence[ParameterType]:
        # signature supports monotype {'type': 'type-name'}## or multiple types {'types': ['type1-name', 'type2-name']}
        return [
            *([st] if (st := spec.get('type')) is not None else []),
            *spec.get('types', []),
        ]

    def _type_check_single(
            self,
            current: ta.Any,
            types: ta.Sequence[ParameterType],
            function_name: str,
            *,
            ctx: FunctionContext,
    ) -> None:
        # Type checking involves checking the top level type, and in the case of arrays, potentially checking the types
        # of each element.
        allowed_types, allowed_element_types = self._get_allowed_types(types)

        current_type = ctx.runtime.type_of(current)
        if current_type not in allowed_types:
            raise JmespathTypeError(
                function_name,
                current,
                current_type,
                types,
            )

        # If we're dealing with an array type, we can have additional restrictions on the type of the array elements.
        if allowed_element_types:
            self._element_type_check(
                current,
                allowed_element_types,
                types,
                function_name,
                ctx=ctx,
            )

    class _AllowedTypes(ta.NamedTuple):
        types: ta.Sequence[JmespathType]
        element_types: ta.Sequence[ta.Sequence[JmespathType]]

    def _get_allowed_types(self, types: ta.Iterable[ParameterType]) -> _AllowedTypes:
        allowed_types: list[JmespathType] = []
        allowed_element_types: list[ta.Sequence[JmespathType]] = []

        t: str
        for t in types:
            if '-' in t:
                t, et = t.split('-', 1)
                allowed_element_types.append([ta.cast(JmespathType, et)])

            allowed_types.append(ta.cast(JmespathType, t))

        return FunctionsClass._AllowedTypes(allowed_types, allowed_element_types)

    def _element_type_check(
            self,
            current: ta.Any,
            allowed_element_types: ta.Sequence[ta.Sequence[JmespathType]],
            types: ta.Sequence[ParameterType],
            function_name: str,
            *,
            ctx: FunctionContext,
    ) -> None:
        elements_iter = ctx.runtime.iter_array(current)
        if elements_iter is None:
            return

        if len(allowed_element_types) == 1:
            # The easy case, we know up front what type we need to validate.
            ets = allowed_element_types[0]
            for element in elements_iter:
                element_type = ctx.runtime.type_of(element)
                if element_type not in ets:
                    raise JmespathTypeError(function_name, element, element_type, types)

        else:
            elements = ctx.runtime.array_items(current)

        if len(allowed_element_types) > 1 and elements:
            # Dynamic type validation. Based on the first type we see, we validate that the remaining types match.
            first = ctx.runtime.type_of(elements[0])
            for element_types in allowed_element_types:
                if first in element_types:
                    allowed = element_types
                    break
            else:
                raise JmespathTypeError(function_name, elements[0], first, types)

            for element in elements:
                element_type = ctx.runtime.type_of(element)
                if element_type not in allowed:
                    raise JmespathTypeError(function_name, element, element_type, types)

    #

    def _ensure_integer(
            self,
            func_name: str,
            param_name: str,
            param_value: ta.Any,
    ) -> None:
        if param_value is not None:
            if int(param_value) != param_value:
                raise JmespathValueError(
                    func_name,
                    param_value,
                    'integer',
                )

    def _ensure_non_negative_integer(
            self,
            func_name: str,
            param_name: str,
            param_value: ta.Any,
    ) -> None:
        if param_value is not None:
            if int(param_value) != param_value or int(param_value) < 0:
                raise JmespathValueError(
                    func_name,
                    param_name,
                    'non-negative integer',
                )


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


class ContainerFunctions(FunctionsClass):
    @signature({'types': ['array', 'string']}, {'types': [], 'variadic': True}, pass_context=True)
    def _func_contains(self, subject, *searches, ctx: FunctionContext):
        return any(ctx.runtime.contains(subject, search) for search in searches)

    @signature({'types': ['array', 'string']}, {'types': [], 'variadic': True})
    def _func_in(self, subject, *searches):
        return subject in searches

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


class StringFunctions(FunctionsClass):
    @signature({'types': ['string']})
    def _func_lower(self, arg):
        return arg.lower()

    @signature({'types': ['string']})
    def _func_upper(self, arg):
        return arg.upper()

    @signature({'types': ['string']}, {'types': ['string']})
    def _func_ends_with(self, search, suffix):
        return search.endswith(suffix)

    @signature({'types': ['string']}, {'types': ['string']})
    def _func_starts_with(self, search, suffix):
        return search.startswith(suffix)

    @signature({'type': 'string'}, {'type': 'string', 'optional': True})
    def _func_trim(self, text, chars=None):
        if chars is None or len(chars) == 0:
            return text.strip()
        return text.strip(chars)

    @signature({'type': 'string'}, {'type': 'string', 'optional': True})
    def _func_trim_left(self, text, chars=None):
        if chars is None or len(chars) == 0:
            return text.lstrip()
        return text.lstrip(chars)

    @signature({'type': 'string'}, {'type': 'string', 'optional': True})
    def _func_trim_right(self, text, chars=None):
        if chars is None or len(chars) == 0:
            return text.rstrip()
        return text.rstrip(chars)

    @signature({'types': ['string']}, {'types': ['array-string']})
    def _func_join(self, separator, array):
        return separator.join(array)

    #

    def _find_impl(self, text, search, func, start, end):
        if len(search) == 0:
            return None
        if end is None:
            end = len(text)

        pos = func(text[start:end], search)
        if start < 0:
            start = start + len(text)

        # restrict resulting range to valid indices
        start = min(max(start, 0), len(text))
        return start + pos if pos != -1 else None

    @signature(
        {'type': 'string'},
        {'type': 'string'},
        {'type': 'number', 'optional': True},
        {'type': 'number', 'optional': True},
    )
    def _func_find_first(self, text, search, start=0, end=None):
        self._ensure_integer('find_first', 'start', start)
        self._ensure_integer('find_first', 'end', end)
        return self._find_impl(
            text,
            search,
            lambda t, s: t.find(s),
            start,
            end,
        )

    @signature(
        {'type': 'string'},
        {'type': 'string'},
        {'type': 'number', 'optional': True},
        {'type': 'number', 'optional': True})
    def _func_find_last(self, text, search, start=0, end=None):
        self._ensure_integer('find_last', 'start', start)
        self._ensure_integer('find_last', 'end', end)
        return self._find_impl(
            text,
            search,
            lambda t, s: t.rfind(s),
            start,
            end,
        )

    #

    def _pad_impl(self, func, padding):
        if len(padding) != 1:
            raise JmespathError(
                f'syntax-error: pad_right() expects $padding to have a single character, but received '
                f'`{padding}` instead.',
            )
        return func()

    @signature(
        {'type': 'string'},
        {'type': 'number'},
        {'type': 'string', 'optional': True},
    )
    def _func_pad_left(self, text, width, padding=' '):
        self._ensure_non_negative_integer('pad_left', 'width', width)
        return self._pad_impl(lambda: text.rjust(width, padding), padding)

    @signature(
        {'type': 'string'},
        {'type': 'number'},
        {'type': 'string', 'optional': True},
    )
    def _func_pad_right(self, text, width, padding=' '):
        self._ensure_non_negative_integer('pad_right', 'width', width)
        return self._pad_impl(lambda: text.ljust(width, padding), padding)

    #

    @signature(
        {'type': 'string'},
        {'type': 'string'},
        {'type': 'string'},
        {'type': 'number', 'optional': True},
    )
    def _func_replace(self, text, search, replacement, count=None):
        self._ensure_non_negative_integer(
            'replace',
            'count',
            count,
        )

        if count is not None:
            return text.replace(search, replacement, int(count))

        return text.replace(search, replacement)

    @signature(
        {'type': 'string'},
        {'type': 'string'},
        {'type': 'number', 'optional': True},
    )
    def _func_split(self, text, search, count=None):
        self._ensure_non_negative_integer(
            'split',
            'count',
            count,
        )

        if len(search) == 0:
            chars = list(text)
            if count is None:
                return chars

            head = list(chars[:count])
            tail = [''.join(chars[count:])]
            return head + tail

        if count is not None:
            return text.split(search, count)

        return text.split(search)

    #

    @signature({'types': ['string']}, {'types': ['string']})
    def _func_match(self, string, pattern):
        return re.match(pattern, string) is not None


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


class DefaultFunctions(
    KeyedFunctions,
    ObjectFunctions,
    StringFunctions,
    NumberFunctions,
    ContainerFunctions,
    TypeFunctions,
    FunctionsClass,
):
    pass
