import types
import typing as ta

from omlish import lang


T = ta.TypeVar('T')
Namespace: ta.TypeAlias = ta.MutableMapping[str, ta.Any]


def create_fn(
        name: str,
        args: ta.Sequence[str],
        body: ta.Sequence[str],
        *,
        globals: ta.Optional[Namespace] = None,
        locals: ta.Optional[Namespace] = None,
        return_type: lang.Maybe[ta.Any] = lang.empty(),
) -> ta.Callable:
    if locals is None:
        locals = {}
    return_annotation = ''
    if return_type.present:
        locals['__dataclass_return_type__'] = return_type.must()
        return_annotation = '->__dataclass_return_type__'
    args = ','.join(args)
    body = '\n'.join(f'  {b}' for b in body)

    txt = f' def {name}({args}){return_annotation}:\n{body}'

    local_vars = ', '.join(locals.keys())
    txt = f"def __create_fn__({local_vars}):\n{txt}\n return {name}"
    ns: dict[str, ta.Any] = {}
    exec(txt, globals, ns)  # type: ignore
    return ns['__create_fn__'](**locals)


def set_qualname(cls: type, value: T) -> T:
    if isinstance(value, types.FunctionType):
        value.__qualname__ = f"{cls.__qualname__}.{value.__name__}"
    return value


def set_new_attribute(cls: type, name: str, value: ta.Any) -> bool:
    if name in cls.__dict__:
        return True
    set_qualname(cls, value)
    setattr(cls, name, value)
    return False
