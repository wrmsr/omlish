import dataclasses as dc


def _create_fn(
        name,
        args,
        body,
        *,
        globals=None,
        locals=None,
        return_type=dc.MISSING,
):
    if locals is None:
        locals = {}
    return_annotation = ''
    if return_type is not dc.MISSING:
        locals['__dataclass_return_type__'] = return_type
        return_annotation = '->__dataclass_return_type__'
    args = ','.join(args)
    body = '\n'.join(f'  {b}' for b in body)

    txt = f' def {name}({args}){return_annotation}:\n{body}'

    local_vars = ', '.join(locals.keys())
    txt = f"def __create_fn__({local_vars}):\n{txt}\n return {name}"
    ns = {}
    exec(txt, globals, ns)
    return ns['__create_fn__'](**locals)
