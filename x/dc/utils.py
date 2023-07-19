import typing as ta

from omlish import lang


Namespace = ta.MutableMapping[str, ta.Any]


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
    ns = {}
    exec(txt, globals, ns)
    return ns['__create_fn__'](**locals)
