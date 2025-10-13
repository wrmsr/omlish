# ruff: noqa: TC002
import typing as ta

from omlish import lang


with lang.auto_proxy_import(globals()):
    import markdown_it as md
    import markdown_it.token  # noqa


##


def token_repr(t: 'md.token.Token') -> str:
    return ''.join([
        'Token(',
        f'type={t.type!r}',
        *([f', tag={t.tag!r}'] if t.tag else []),
        *([f', nesting={t.nesting!r}'] if t.nesting else []),
        *([f', attrs={t.attrs!r}'] if t.attrs else []),
        *([f', map={t.map!r}'] if t.map else []),
        *([f', level={t.level!r}'] if t.level else []),
        *([f', children={t.children!r}'] if t.children else []),
        *([f', content={t.content!r}'] if t.content else []),
        *([f', markup={t.markup!r}'] if t.markup else []),
        *([f', info={t.info!r}'] if t.info else []),
        *([f', meta={t.meta!r}'] if t.meta else []),
        *([f', block={t.block!r}'] if t.block else []),
        *([f', hidden={t.hidden!r}'] if t.hidden else []),
        ')',
    ])


##


def flatten_tokens(
        tokens: ta.Iterable['md.token.Token'],
        *,
        filter: ta.Callable[['md.token.Token'], bool] | None = None,  # noqa
) -> ta.Iterable['md.token.Token']:
    def rec(tks: ta.Iterable['md.token.Token']) -> ta.Iterator['md.token.Token']:
        for tk in tks:
            if tk.children and not (filter is not None and not filter(tk)):
                yield from rec(tk.children)

            else:
                yield tk

    return rec(tokens)
