import dataclasses as dc
import textwrap
import types
import typing as ta

from ... import check
from ... import lang


T = ta.TypeVar('T')
Namespace: ta.TypeAlias = ta.MutableMapping[str, ta.Any]


def create_fn(
        name: str,
        args: ta.Sequence[str],
        body: ta.Sequence[str],
        *,
        globals: Namespace | None = None,  # noqa
        locals: Namespace | None = None,  # noqa
        return_type: lang.Maybe[ta.Any] = lang.empty(),
) -> ta.Callable:
    check.not_isinstance(args, str)
    check.not_isinstance(body, str)

    if locals is None:
        locals = {}  # noqa
    return_annotation = ''
    if return_type.present:
        locals['__dataclass_return_type__'] = return_type()
        return_annotation = '->__dataclass_return_type__'
    args = ','.join(args)
    body = '\n'.join(f'  {b}' for b in body)

    txt = f' def {name}({args}){return_annotation}:\n{body}'

    local_vars = ', '.join(locals.keys())
    txt = f'def __create_fn__({local_vars}):\n{txt}\n return {name}'
    ns: dict[str, ta.Any] = {}
    exec(txt, globals, ns)  # type: ignore
    return ns['__create_fn__'](**locals)


# TODO: https://github.com/python/cpython/commit/8945b7ff55b87d11c747af2dad0e3e4d631e62d6
class FuncBuilder:
    def __init__(self, globals: Namespace) -> None:  # noqa
        super().__init__()

        self.names: list[str] = []
        self.src: list[str] = []
        self.globals = globals
        self.locals: Namespace = {}
        self.overwrite_errors: dict[str, bool] = {}
        self.unconditional_adds: dict[str, bool] = {}

    def add_fn(
            self,
            name: str,
            args: ta.Sequence[str],
            body: ta.Sequence[str],
            *,
            locals: Namespace | None = None,  # noqa
            return_type: lang.Maybe[ta.Any] = lang.empty(),
            overwrite_error: bool = False,
            unconditional_add: bool = False,
            decorator: str | None = None,
    ) -> None:
        if locals is not None:
            self.locals.update(locals)

        # Keep track if this method is allowed to be overwritten if it already exists in the class.  The error is
        # method-specific, so keep it with the name.  We'll use this when we generate all of the functions in the
        # add_fns_to_class call.  overwrite_error is either True, in which case we'll raise an error, or it's a string,
        # in which case we'll raise an error and append this string.
        if overwrite_error:
            self.overwrite_errors[name] = overwrite_error

        # Should this function always overwrite anything that's already in the class?  The default is to not overwrite a
        # function that already exists.
        if unconditional_add:
            self.unconditional_adds[name] = True

        self.names.append(name)

        if return_type.present:
            self.locals[f'__dataclass_{name}_return_type__'] = return_type()
            return_annotation = f' -> __dataclass_{name}_return_type__'
        else:
            return_annotation = ''
        args = ', '.join(args)
        body = textwrap.indent('\n'.join(body), '    ')

        # Compute the text of the entire function, add it to the text we're generating.
        deco_str = '  {decorator}\n' if decorator else ''
        self.src.append(f'{deco_str}  def {name}({args}){return_annotation}:\n{body}')

    def add_fns_to_class(self, cls: type) -> None:
        # The source to all of the functions we're generating.
        fns_src = '\n'.join(self.src)

        # The locals they use.
        local_vars = ','.join(self.locals)

        # The names of all of the functions, used for the return value of the outer function.  Need to handle the
        # 0-tuple specially.
        if not self.names:
            return_names = '()'
        else:
            return_names = f'({",".join(self.names)},)'

        # txt is the entire function we're going to execute, including the bodies of the functions we're defining.
        # Here's a greatly simplified version:
        # def __create_fn__():
        #   def __init__(self, x, y):
        #     self.x = x
        #     self.y = y
        #   @recursive_repr
        #   def __repr__(self):
        #     return f'cls(x={self.x!r},y={self.y!r})'
        # return __init__,__repr__

        txt = f'def __create_fn__({local_vars}):\n{fns_src}\n  return {return_names}'
        ns: dict[str, ta.Any] = {}
        exec(txt, self.globals, ns)  # type: ignore
        fns = ns['__create_fn__'](**self.locals)

        # Now that we've generated the functions, assign them into cls.
        for name, fn in zip(self.names, fns):
            fn.__qualname__ = f'{cls.__qualname__}.{fn.__name__}'
            if self.unconditional_adds.get(name, False):
                setattr(cls, name, fn)
            else:
                already_exists = set_new_attribute(cls, name, fn)

                # See if it's an error to overwrite this particular function.
                if already_exists and (msg_extra := self.overwrite_errors.get(name)):
                    error_msg = (f'Cannot overwrite attribute {fn.__name__} in class {cls.__name__}')
                    if msg_extra:
                        error_msg = f'{error_msg} {msg_extra}'

                    raise TypeError(error_msg)


def set_qualname(cls: type, value: T) -> T:
    if isinstance(value, types.FunctionType):
        value.__qualname__ = f'{cls.__qualname__}.{value.__name__}'
    return value


def set_new_attribute(cls: type, name: str, value: ta.Any) -> bool:
    if name in cls.__dict__:
        return True
    set_qualname(cls, value)
    setattr(cls, name, value)
    return False


def tuple_str(obj_name: str, fields: ta.Iterable[dc.Field]) -> str:
    # Return a string representing each field of obj_name as a tuple member.  So, if fields is ['x', 'y'] and obj_name
    # is "self", return "(self.x,self.y)".

    # Special case for the 0-tuple.
    if not fields:
        return '()'

    # Note the trailing comma, needed if this turns out to be a 1-tuple.
    return f'({",".join([f"{obj_name}.{f.name}" for f in fields])},)'
