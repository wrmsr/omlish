import typing as ta

from omlish import lang

from .names import NamespaceBuilder


##


def render_param_spec_call(params: lang.ParamSpec) -> str:
    args = []
    for p in params:
        if isinstance(p, lang.ArgsParam):
            args.append(f'*{p.name}')
        elif isinstance(p, lang.KwargsParam):
            args.append(f'**{p.name}')
        elif isinstance(p, lang.PosOnlyParam):
            args.append(p.name)
        elif isinstance(p, lang.KwOnlyParam):
            args.append(f'{p.name}={p.name}')
        elif isinstance(p, lang.ValParam):
            args.append(p.name)
        elif isinstance(p, lang.ParamSeparator):
            pass
        else:
            raise TypeError(p)
    return f"({', '.join(args)})"


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
