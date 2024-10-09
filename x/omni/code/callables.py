"""
FIXME:
 - modernize / use inspect.bind / use internal ArgSpec / untangle...
"""
import ast
import functools
import inspect
import typing as ta

from .. import check
from .. import lang


tuple_ = tuple


def get_arg_names(argspec: inspect.FullArgSpec) -> ta.Iterable[str]:
    arg_names = tuple_(argspec.args)
    if argspec.varargs:
        arg_names += (argspec.varargs,)
    if argspec.varkw:
        arg_names += (argspec.varkw,)
    return arg_names


def build_arg_dict(
        argspec: inspect.FullArgSpec,
        args: ta.Iterable[ta.Any],
        kwargs: ta.Mapping[str, ta.Any]
) -> ta.Dict[str, ta.Union[int, ta.Iterable[int], ta.Mapping[str, int]]]:
    args = tuple_(args)
    arg_names = get_arg_names(argspec)
    kwarg_defaults = dict(zip(argspec.args[-len(argspec.defaults):], argspec.defaults)) \
        if argspec.defaults else {}
    dct = kwarg_defaults.copy()
    dct.update(dict(zip(arg_names, args)))
    if argspec.varargs:
        dct[argspec.varargs] = args[len(argspec.args):]
    dct.update(dict((k, v) for k, v in kwargs.items() if k in arg_names))
    if argspec.varkw:
        dct[argspec.varkw] = dict((k, v) for k, v in kwargs.items() if k not in arg_names)
    return dct


class Callable(lang.Sealed):

    final_type: ta.Optional[type] = None

    def __init__(self, *args, **kwargs) -> None:
        if self.final_type is not None and type(self) is not self.final_type:
            raise TypeError('%r should not be subclassed' % (self.final_type,))
        super().__init__()
        self._args = args
        self._kwargs = kwargs
        self._fn = check.callable(self.construct(*args, **kwargs))

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def fn(self):
        return self._fn

    def __call__(self, *args, **kwargs):
        return self._fn(*args, **kwargs)

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            lang.arg_repr(*self.args, **self.kwargs))

    def __getstate__(self):
        return (self._args, self._kwargs)

    def __setstate__(self, args_and_kwargs):
        args, kwargs = args_and_kwargs
        self.__init__(*args, **kwargs)

    @classmethod
    def construct(cls, expr: str) -> ta.Callable:
        raise NotImplementedError


class Expr(Callable, lang.Final):

    @classmethod
    def construct(cls, expr: str) -> ta.Callable:
        return eval(expr)


class Lambda(Callable, lang.Final):

    @classmethod
    def construct(cls, *args) -> ta.Callable:
        if len(args) == 1:
            largs, body = '', args[0]
        elif len(args) == 2:
            largs, body = args
        else:
            raise TypeError(args)
        return eval('lambda %s: %s' % (largs, body))


class Function(Callable, lang.Final):

    fn_name = '__fn__'

    @classmethod
    def construct(
            cls,
            *args,
            imports: ta.Iterable[str] = None,
            namespace: ta.Mapping[str, ta.Any] = None
    ) -> ta.Callable:
        if len(args) == 1:
            fargs, body, init = None, args[0], None
        elif len(args) == 2:
            fargs, body, init = args[0], args[1], None
        elif len(args) == 3:
            fargs, body, init = args
        else:
            raise TypeError(args)

        def_mod_ast = ast.parse('def %s(%s): pass' % (cls.fn_name, fargs))
        check.isinstance(def_mod_ast, ast.Module)
        def_ast = def_mod_ast.body[0]
        check.isinstance(def_ast, ast.FunctionDef)
        body_ast = ast.parse(body)
        check.isinstance(body_ast, ast.Module)
        def_ast.body = body_ast.body

        if init:
            init_mod_ast = ast.parse(init)
            check.isinstance(init_mod_ast, ast.Module)
            def_mod_ast.body[:0] = init_mod_ast.body

        if imports:
            for i, _import in enumerate(imports):
                if isinstance(_import, tuple):
                    name, asname = _import
                elif isinstance(_import, str):
                    name, asname = _import, None
                else:
                    raise TypeError(_import)
                import_ast = ast.Import(
                    names=[ast.alias(name=name, asname=asname)],
                    lineno=i,
                    col_offset=0)
                def_mod_ast.body.insert(0, import_ast)

        code = compile(def_mod_ast, '<fn>', 'exec')
        code_namespace = dict(namespace) if namespace else {}
        exec(code, code_namespace)
        return code_namespace[cls.fn_name]


class Bindable(Callable):

    arg_names: ta.Sequence[str] = ()
    argspec: ta.Optional[inspect.FullArgSpec] = None

    def __repr__(self) -> str:
        if self.argspec is None:
            return self.fn.__name__
        else:
            args_dct = build_arg_dict(self.argspec, self.args, self.kwargs)
            args_str = ', '.join('%s=%r' % (k, args_dct.get(k)) for k in self.arg_names)
            return '%s(%s)' % (check.not_none(self.final_type).__name__, args_str)

    @property
    def arg(self):
        try:
            return self._arg_accessor
        except AttributeError:
            args_dct = build_arg_dict(self.argspec, self.args, self.kwargs)
            arg_accessor = self._arg_accessor = lang.Accessor(args_dct.__getitem__)
            return arg_accessor


def alias(*bases):
    def inner(fn):
        dct = dict((k, getattr(fn, k)) for k in functools.WRAPPER_ASSIGNMENTS)
        dct['__module__'] = fn.__module__
        scls = lang.new_type(fn.__name__, (Bindable,) + bases, dct)
        scls.construct = staticmethod(lambda: fn)
        scls.final_type = scls
        return scls()
    return inner


def constructor(*bases):
    def inner(fn):
        argspec: inspect.FullArgSpec = inspect.getfullargspec(fn)
        arg_names = get_arg_names(argspec)
        dct = dict((k, getattr(fn, k)) for k in functools.WRAPPER_ASSIGNMENTS)
        dct['__module__'] = fn.__module__
        scls = lang.new_type(fn.__name__, (Bindable,) + bases, dct)
        scls.final_type = scls
        scls.arg_names = arg_names
        scls.construct = staticmethod(fn)
        scls.argspec = argspec
        return scls
    return inner


@constructor()
def const(value):
    def inner(*args, **kwargs):
        return value
    return inner


@alias()
def identity(obj):
    return obj


@constructor()
def raise_(exc):
    def inner(*args, **kwargs):
        raise exc
    return inner


@alias()
def tuple(*t):  # noqa
    return t


@constructor()
def method(name):
    def inner(obj, *args, **kwargs):
        return getattr(obj, name)(*args, **kwargs)
    return inner
