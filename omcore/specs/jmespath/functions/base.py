import dataclasses as dc
import inspect
import typing as ta

from ..errors import ArityError
from ..errors import JmespathTypeError
from ..errors import JmespathValueError
from ..errors import UnknownFunctionError
from ..errors import VariadicArityError
from ..runtime import JmespathType
from ..runtime import PythonRuntime
from .types import FunctionContext


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
