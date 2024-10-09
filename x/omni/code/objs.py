"""
TODO:
 - class CO/FUNC (ValueEnum)
 - Code/Function dataclass - dc.replaceable
 - pyc find/unmarshal/marshal
"""
import dis
import gc
import sys
import types
import typing as ta
import weakref

from .. import check
from .argspecs import ArgSpec
from .argspecs import ArgSpecable
from .argspecs import render_arg_spec_call
from .gen import create_function


CODE_ARGS = [
    'argcount',
    'kwonlyargcount',
    'nlocals',
    'stacksize',
    'flags',
    'code',
    'consts',
    'names',
    'varnames',
    'filename',
    'name',
    'firstlineno',
    'lnotab',
    'freevars',
    'cellvars',
]

if sys.version_info[1] > 7:
    CODE_ARGS.insert(1, 'posonlyargcount')


CO_FLAG_VALUES = {v: k for k, v in dis.COMPILER_FLAG_NAMES.items()}

CO_OPTIMIZED: int = CO_FLAG_VALUES['OPTIMIZED']
CO_NEWLOCALS: int = CO_FLAG_VALUES['NEWLOCALS']
CO_VARARGS: int = CO_FLAG_VALUES['VARARGS']
CO_VARKEYWORDS: int = CO_FLAG_VALUES['VARKEYWORDS']
CO_NESTED: int = CO_FLAG_VALUES['NESTED']
CO_GENERATOR: int = CO_FLAG_VALUES['GENERATOR']
CO_NOFREE: int = CO_FLAG_VALUES['NOFREE']
CO_COROUTINE: int = CO_FLAG_VALUES['COROUTINE']
CO_ITERABLE_COROUTINE: int = CO_FLAG_VALUES['ITERABLE_COROUTINE']
CO_ASYNC_GENERATOR: int = CO_FLAG_VALUES['ASYNC_GENERATOR']


FUNCTION_ARGS = [
    'code',
    'globals',
    'name',
    'defaults',
    'closure',
]

FUNC_NONE = 0
FUNC_DEFAULTS = 1
FUNC_KWDEFAULTS = 2
FUNC_ANNOTATIONS = 4
FUNC_CLOSURE = 8


def get_code_flag_names(flags: int) -> ta.List[str]:
    return [k for k, v in CO_FLAG_VALUES.items() if flags & v]


def instruction_bytes(instrs: ta.Iterable[dis.Instruction]) -> bytes:
    return bytes(b if b is not None else 0 for instr in instrs for b in [instr.opcode, instr.arg])


def recode_func(func: types.FunctionType, code_bytes: ta.Union[bytes, bytearray]) -> ta.Iterable[ta.Any]:
    codeargs = [getattr(func.__code__, f'co_{k}') for k in CODE_ARGS]
    codeargs[CODE_ARGS.index('code')] = bytes(code_bytes)
    code = types.CodeType(*codeargs)

    funcargs = [getattr(func, f'__{k}__') for k in FUNCTION_ARGS]
    funcargs[FUNCTION_ARGS.index('code')] = code
    return funcargs


class AmbiguousCodeException(Exception):
    pass


_FUNCTIONS_BY_CODE: ta.MutableMapping[types.CodeType, types.FunctionType] = weakref.WeakValueDictionary()


def get_code_function(code: types.CodeType) -> types.FunctionType:
    """
    AmbiguousFrameException should always be handled gracefully - in the presence of multiple threads (and even
    recursive invocations within a single thread) the originally invoking function may have already had its code
    patched. Callers of this code should be robust enough for this to only result in wasted work that will likely be
    redone and corrected in subsequent invocations.
    """

    try:
        return _FUNCTIONS_BY_CODE[code]
    except KeyError:
        refs = gc.get_referrers(code)
        funcs = [
            r for r in refs if (
                isinstance(r, types.FunctionType) and
                r.__code__ is code
            )
        ]
        if len(funcs) != 1:
            raise AmbiguousCodeException(code)
        func = _FUNCTIONS_BY_CODE[code] = funcs[0]
        return func


def create_detour(arg_spec: ArgSpecable, target: ta.Callable) -> types.CodeType:
    arg_spec = ArgSpec.of(arg_spec)
    check.callable(target)

    gfn = create_function('_', arg_spec, f'return 1{render_arg_spec_call(arg_spec)}')
    check.state(gfn.__code__.co_consts == (None, 1))
    kw = {a: getattr(gfn.__code__, 'co_' + a) for a in CODE_ARGS}
    kw['consts'] = (None, target)
    return types.CodeType(*[kw[a] for a in CODE_ARGS])
