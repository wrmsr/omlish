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


T = ta.TypeVar('T')


##


JmespathType: ta.TypeAlias = ta.Literal[
    'boolean',
    'array',
    'object',
    'null',
    'string',
    'number',
    'expref',
]


PyType = ta.NewType('PyType', str)


def pytype_of(o: ta.Any) -> PyType:
    return PyType(type(o).__name__)


TYPES_MAP: ta.Mapping[PyType, JmespathType] = {
    PyType('bool'): 'boolean',
    PyType('list'): 'array',
    PyType('dict'): 'object',
    PyType('NoneType'): 'null',
    PyType('unicode'): 'string',
    PyType('str'): 'string',
    PyType('float'): 'number',
    PyType('int'): 'number',
    PyType('long'): 'number',
    PyType('OrderedDict'): 'object',
    PyType('_Projection'): 'array',
    PyType('_Expression'): 'expref',
}


REVERSE_TYPES_MAP: ta.Mapping[JmespathType, ta.Sequence[PyType]] = {
    'boolean': [
        PyType('bool'),
    ],
    'array': [
        PyType('list'),
        PyType('_Projection'),
    ],
    'object': [
        PyType('dict'),
        PyType('OrderedDict'),
    ],
    'null': [
        PyType('NoneType'),
    ],
    'string': [
        PyType('unicode'),
        PyType('str'),
    ],
    'number': [
        PyType('float'),
        PyType('int'),
    ],
    'expref': [
        PyType('_Expression'),
    ],
}


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
class Function:
    function: ta.Callable
    signature: Signature


def signature(*params: Parameter):
    def _record_signature(func):
        func.signature = params
        return func
    return _record_signature


class Functions(ta.Protocol):
    def call_function(self, function_name, resolved_args): ...


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
                )

        cls._function_table = function_table

    #

    def call_function(self, function_name: str, resolved_args: ta.Sequence[ta.Any]) -> ta.Any:
        try:
            spec = self._function_table[function_name]
        except KeyError:
            raise UnknownFunctionError(f'Unknown function: {function_name}()')  # noqa

        self._validate_arguments(resolved_args, spec.signature, function_name)
        return spec.function.__get__(self, self.__class__)(*resolved_args)  # noqa

    def _validate_arguments(self, args: ta.Sequence[ta.Any], sig: Signature, function_name: str) -> None:
        if len(sig) == 0:
            self._type_check(args, sig, function_name)
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

        self._type_check(args, sig, function_name)

    def _type_check(self, actual: ta.Sequence[ta.Any], sig: Signature, function_name: str) -> None:
        for i in range(min(len(sig), len(actual))):
            allowed_types = self._get_allowed_types_from_signature(sig[i])
            if allowed_types:
                self._type_check_single(actual[i], allowed_types, function_name)

    def _get_allowed_types_from_signature(self, spec: Parameter) -> ta.Sequence[ParameterType]:
        # signature supports monotype {'type': 'type-name'}## or multiple types {'types': ['type1-name', 'type2-name']}
        return [
            *([st] if (st := spec.get('type')) is not None else []),
            *spec.get('types', []),
        ]

    def _type_check_single(self, current: ta.Any, types: ta.Sequence[ParameterType], function_name: str) -> None:
        # Type checking involves checking the top level type, and in the case of arrays, potentially checking the types
        # of each element.
        allowed_types, allowed_element_types = self._get_allowed_pytypes(types)

        # We're not using isinstance() on purpose. The type model for jmespath does not map 1-1 with python types
        # (booleans are considered integers in python for example).
        pytype = pytype_of(current)
        if pytype not in allowed_types:
            raise JmespathTypeError(
                function_name,
                current,
                self._convert_to_jmespath_type(pytype),
                types,
            )

        # If we're dealing with a list type, we can have additional restrictions on the type of the list elements (for
        # example a function can require a list of numbers or a list of strings). Arrays are the only types that can
        # have element types.
        if allowed_element_types:
            self._element_type_check(
                current,
                allowed_element_types,
                types,
                function_name,
            )

    class _AllowedPytypes(ta.NamedTuple):
        types: ta.Sequence[PyType]
        element_types: ta.Sequence[ta.Sequence[PyType]]

    def _get_allowed_pytypes(self, types: ta.Iterable[ParameterType]) -> _AllowedPytypes:
        allowed_types: list = []
        allowed_element_types: list = []

        t: str
        for t in types:
            if '-' in t:
                t, et = t.split('-', 1)
                allowed_element_types.append(REVERSE_TYPES_MAP[ta.cast(JmespathType, et)])

            allowed_types.extend(REVERSE_TYPES_MAP[ta.cast(JmespathType, t)])

        return FunctionsClass._AllowedPytypes(allowed_types, allowed_element_types)

    def _element_type_check(
            self,
            current: ta.Sequence[ta.Any],
            allowed_element_types: ta.Sequence[ta.Sequence[PyType]],
            types: ta.Sequence[ParameterType],
            function_name: str,
    ) -> None:
        if len(allowed_element_types) == 1:
            # The easy case, we know up front what type we need to validate.
            ets = allowed_element_types[0]
            for element in current:
                pytype = pytype_of(element)
                if pytype not in ets:
                    raise JmespathTypeError(function_name, element, pytype, types)

        elif len(allowed_element_types) > 1 and current:
            # Dynamic type validation. Based on the first type we see, we validate that the remaining types match.
            first = pytype_of(current[0])
            for element_types in allowed_element_types:
                if first in element_types:
                    allowed = element_types
                    break
            else:
                raise JmespathTypeError(function_name, current[0], first, types)

            for element in current:
                pytype = pytype_of(element)
                if pytype not in allowed:
                    raise JmespathTypeError(function_name, element, pytype, types)

    #

    def _convert_to_jmespath_type(self, pytype: PyType) -> JmespathType | ta.Literal['unknown']:
        return TYPES_MAP.get(pytype, 'unknown')

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
    @signature({'types': []})
    def _func_type(self, arg):
        if isinstance(arg, str):
            return 'string'
        elif isinstance(arg, bool):
            return 'boolean'
        elif isinstance(arg, list):
            return 'array'
        elif isinstance(arg, dict):
            return 'object'
        elif isinstance(arg, (float, int)):
            return 'number'
        elif arg is None:
            return 'null'
        else:
            return None

    @signature({'types': [], 'variadic': True})
    def _func_not_null(self, *arguments):
        for argument in arguments:
            if argument is not None:
                return argument
        return None

    @signature({'types': []})
    def _func_to_array(self, arg):
        if isinstance(arg, list):
            return arg
        else:
            return [arg]

    @signature({'types': []})
    def _func_to_string(self, arg):
        if isinstance(arg, str):
            return arg
        else:
            return json.dumps(arg, separators=(',', ':'), default=str)

    @signature({'types': []})
    def _func_to_number(self, arg):
        if isinstance(arg, (list, dict, bool)):
            return None

        elif arg is None:
            return None

        elif isinstance(arg, (int, float)):
            return arg

        else:
            try:
                return int(arg)
            except ValueError:
                try:
                    return float(arg)
                except ValueError:
                    return None


class ContainerFunctions(FunctionsClass):
    @signature({'types': ['array', 'string']}, {'types': [], 'variadic': True})
    def _func_contains(self, subject, *searches):
        return any(search in subject for search in searches)

    @signature({'types': ['array', 'string']}, {'types': [], 'variadic': True})
    def _func_in(self, subject, *searches):
        return subject in searches

    @signature({'types': ['string', 'array', 'object']})
    def _func_length(self, arg):
        return len(arg)

    @signature({'types': ['array', 'string']})
    def _func_reverse(self, arg):
        if isinstance(arg, str):
            return arg[::-1]
        else:
            return list(reversed(arg))

    @signature({'types': ['expref']}, {'types': ['array']})
    def _func_map(self, expref, arg):
        result = []
        for element in arg:
            result.append(expref.visit(expref.expression, element))
        return result

    @signature({'types': ['object'], 'variadic': True})
    def _func_merge(self, *arguments):
        merged = {}
        for arg in arguments:
            merged.update(arg)
        return merged

    @signature({'types': ['array-string', 'array-number']})
    def _func_sort(self, arg):
        return sorted(arg)

    @signature({'types': ['array'], 'variadic': True})
    def _func_zip(self, *arguments):
        return [list(t) for t in zip(*arguments)]


class NumberFunctions(FunctionsClass):
    @signature({'types': ['number']})
    def _func_abs(self, arg):
        return abs(arg)

    @signature({'types': ['array-number']})
    def _func_avg(self, arg):
        if arg:
            return sum(arg) / len(arg)
        else:
            return None

    @signature({'types': ['number']})
    def _func_ceil(self, arg):
        return math.ceil(arg)

    @signature({'types': ['number']})
    def _func_floor(self, arg):
        return math.floor(arg)

    @signature({'types': ['array-number', 'array-string']})
    def _func_max(self, arg):
        if arg:
            return max(arg)
        else:
            return None

    @signature({'types': ['array-number', 'array-string']})
    def _func_min(self, arg):
        if arg:
            return min(arg)
        else:
            return None

    @signature({'types': ['array-number']})
    def _func_sum(self, arg):
        return sum(arg)


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
    @signature({'types': ['object']})
    def _func_items(self, arg):
        return [list(t) for t in arg.items()]

    @signature({'types': ['array']})
    def _func_from_items(self, items):
        return dict(items)

    @signature({'types': ['object']})
    def _func_keys(self, arg):
        # To be consistent with .values() should we also return the indices of a list?
        return list(arg.keys())

    @signature({'types': ['object']})
    def _func_values(self, arg):
        return list(arg.values())

    @signature({'types': ['expref']}, {'types': ['object']})
    def _func_filter_keys(self, expref, arg):
        return {k: v for k, v in arg.items() if expref.visit(expref.expression, k)}

    @signature({'types': ['expref']}, {'types': ['object']})
    def _func_filter_values(self, expref, arg):
        return {k: v for k, v in arg.items() if expref.visit(expref.expression, v)}


class KeyedFunctions(FunctionsClass):
    def _create_key_func(self, expref, allowed_types, function_name):
        def keyfunc(x):
            result = expref.visit(expref.expression, x)
            jmespath_type = self._convert_to_jmespath_type(pytype_of(result))
            # allowed_types is in terms of jmespath types, not python types.
            if jmespath_type not in allowed_types:
                raise JmespathTypeError(
                    function_name, result, jmespath_type, allowed_types)

            return result

        return keyfunc

    @signature({'types': ['array']}, {'types': ['expref']})
    def _func_sort_by(self, array, expref):
        if not array:
            return array

        # sort_by allows for the expref to be either a number of a string, so we have some special logic to handle this.
        # We evaluate the first array element and verify that it's either a string of a number.  We then create a key
        # function that validates that type, which requires that remaining array elements resolve to the same type as
        # the first element.
        required_type = self._convert_to_jmespath_type(pytype_of(expref.visit(expref.expression, array[0])))
        if required_type not in ['number', 'string']:
            raise JmespathTypeError(
                'sort_by',
                array[0],
                required_type,
                ['string', 'number'],
            )

        keyfunc = self._create_key_func(expref, [required_type], 'sort_by')
        return sorted(array, key=keyfunc)

    @signature({'types': ['array']}, {'types': ['expref']})
    def _func_min_by(self, array, expref):
        keyfunc = self._create_key_func(
            expref,
            ['number', 'string'],
            'min_by',
        )

        if array:
            return min(array, key=keyfunc)
        else:
            return None

    @signature({'types': ['array']}, {'types': ['expref']})
    def _func_max_by(self, array, expref):
        keyfunc = self._create_key_func(
            expref,
            ['number', 'string'],
            'max_by',
        )

        if array:
            return max(array, key=keyfunc)
        else:
            return None

    @signature({'types': ['array']}, {'types': ['expref']})
    def _func_group_by(self, array, expref):
        keyfunc = self._create_key_func(expref, ['null', 'string'], 'group_by')
        if not array:
            return None

        result = {}
        keys = list(dict.fromkeys([keyfunc(item) for item in array if keyfunc(item) is not None]))
        for key in keys:
            items = [item for item in array if keyfunc(item) == key]
            result.update({key: items})

        return result


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
