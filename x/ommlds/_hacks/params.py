import typing as ta

from omlish import lang

from .names import NamespaceBuilder


##


def render_param_spec_call(
        params: lang.ParamSpec,
        *,
        as_kwargs: bool = False,
) -> str:
    src = ['(']

    for i, p in enumerate(params):
        if isinstance(p, lang.ParamSeparator):
            continue

        if i:
            src.append(', ')

        if as_kwargs:
            if isinstance(p, lang.Param):
                src.append(f'{p.name}={p.name}')
            else:
                raise TypeError(p)

        else:
            if isinstance(p, lang.ArgsParam):
                src.append(f'*{p.name}')
            elif isinstance(p, lang.KwargsParam):
                src.append(f'**{p.name}')
            elif isinstance(p, lang.PosOnlyParam):
                src.append(p.name)
            elif isinstance(p, lang.KwOnlyParam):
                src.append(f'{p.name}={p.name}')
            elif isinstance(p, lang.ValParam):
                src.append(p.name)
            else:
                raise TypeError(p)

    src.append(')')

    return ''.join(src)


def render_param_spec_def(
        params: lang.ParamSpec,
        nsb: NamespaceBuilder,
        *,
        return_ann: lang.Maybe[ta.Any] = lang.empty(),
) -> str:
    src = ['(']

    for i, p in enumerate(params):
        if i:
            src.append(', ')

        src.append(lang.param_render(
            p,
            render_annotation=lambda ann: nsb.put(ann, f'ann_{p.name}'),  # noqa
            render_default=lambda dfl: nsb.put(dfl, f'dfl_{p.name}'),  # noqa
        ))

    src.append(')')

    if return_ann.present:
        src.append(f' -> {nsb.put(return_ann.must(), "ann_return")}')

    return ''.join(src)
