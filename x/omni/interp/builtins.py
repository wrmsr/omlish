import types
import typing as ta


PERMITTED_KEYS: ta.Set[str] = {
    'abs',
    'all',
    'any',
    'ascii',
    'bin',
    # debug: 'breakpoint',
    'callable',
    'chr',
    # block: 'compile',
    # special: 'delattr',
    'dir',
    'divmod',
    # block: 'eval',
    # block: 'exec',
    'format',
    # special: 'getattr',
    # special: 'globals',
    # special: 'hasattr',
    'hash',
    'hex',
    'id',
    # block: 'input',
    'isinstance',
    'issubclass',
    'iter',
    'len',
    # special: 'locals',
    'max',
    'min',
    'next',
    'oct',
    'ord',
    'pow',
    # debug: 'print',
    'repr',
    'round',
    # special: 'setattr',
    'sorted',
    'sum',
    'vars',

    'None',
    'Ellipsis',
    'NotImplemented',
    'False',
    'True',
    'bool',

    'memoryview',
    'bytearray',
    'bytes',
    'classmethod',
    'complex',
    'dict',
    'enumerate',
    'filter',
    'float',
    'frozenset',
    'property',
    'int',
    'list',
    'map',
    'object',
    'range',
    'reversed',
    'set',
    'slice',
    'staticmethod',
    'str',
    # special: 'super',
    'tuple',
    'type',
    'zip',

    # debug: 'open',
    # block: 'quit',
    # block: 'exit',
    # block: 'copyright',
    # block: 'credits',
    # block: 'license',
    # block: 'help',
}


PERMITTED_TYPES: ta.Set[type] = set([

])


PERMITTED_BASETYPES: ta.Set[type] = {
    BaseException,
    Warning,
}


def filter_builtins(bltins=None):
    if bltins is None:
        bltins = __builtins__

    if isinstance(bltins, types.ModuleType):
        dct = {a: getattr(__builtins__, a) for a in dir(__builtins__)}
    elif isinstance(bltins, dict):
        dct = dict(bltins)
    else:
        raise TypeError(bltins)

    ret = {}
    for k, v in dct.items():
        if k in PERMITTED_KEYS:
            ret[k] = v
        elif k.startswith('__') and k.endswith('__'):
            continue
        elif (
                any(isinstance(v, c) for c in PERMITTED_TYPES) or
                (isinstance(v, type) and any(isinstance(v, c) for c in PERMITTED_BASETYPES))
        ):
            ret[k] = v
    return ret
