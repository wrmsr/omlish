import ast
import base64
import itertools
import os.path
import typing as ta

from ...py.tokens import all as tks


##


class RootLevelResourcesRead(ta.NamedTuple):
    variable: str
    kind: ta.Literal['binary', 'text']
    resource: str


def is_root_level_resources_read(lts: tks.Tokens) -> RootLevelResourcesRead | None:
    wts = list(tks.ignore_ws(lts, keep=['INDENT']))

    if not tks.match_toks(wts, [
        ('NAME', None),
        ('OP', '='),
        ('NAME', ('read_package_resource_binary', 'read_package_resource_text')),
        ('OP', '('),
        ('NAME', '__package__'),
        ('OP', ','),
        ('STRING', None),
        ('OP', ')'),
    ]):
        return None

    return RootLevelResourcesRead(
        wts[0].src,
        'binary' if wts[2].src == 'read_package_resource_binary' else 'text',
        ast.literal_eval(wts[6].src),
    )


##


def build_resource_lines(
        rsrc: RootLevelResourcesRead,
        path: str,
) -> list[tks.Tokens]:
    rf = os.path.join(os.path.dirname(path), rsrc.resource)

    if rsrc.kind == 'binary':
        with open(rf, 'rb') as bf:
            rb = bf.read()  # noqa

        out: list[tks.Tokens] = [[
            tks.Token(name='NAME', src=rsrc.variable),
            tks.Token(name='UNIMPORTANT_WS', src=' '),
            tks.Token(name='OP', src='='),
            tks.Token(name='UNIMPORTANT_WS', src=' '),
            tks.Token(name='NAME', src='base64'),
            tks.Token(name='OP', src='.'),
            tks.Token(name='NAME', src='b64decode'),
            tks.Token(name='OP', src='('),
            tks.Token(name='NL', src='\n'),
        ]]

        rb64 = base64.b64encode(rb).decode('ascii')
        for chunk in itertools.batched(rb64, 96):
            out.append([
                tks.Token(name='UNIMPORTANT_WS', src='    '),
                tks.Token(name='STRING', src=f"'{''.join(chunk)}'"),
                tks.Token(name='NL', src='\n'),
            ])

        out.append([
            tks.Token(name='OP', src=')'),
            tks.Token(name='NEWLINE', src='\n'),
        ])

        return out

    elif rsrc.kind == 'text':
        with open(rf) as tf:
            rt = tf.read()  # noqa
        rt = rt.replace('\\', '\\\\')  # Escape backslashes
        rt = rt.replace('"""', r'\"\"\"')
        return [[
            tks.Token(name='NAME', src=rsrc.variable),
            tks.Token(name='UNIMPORTANT_WS', src=' '),
            tks.Token(name='OP', src='='),
            tks.Token(name='UNIMPORTANT_WS', src=' '),
            tks.Token(name='STRING', src=f'"""\\\n{rt}"""  # noqa\n'),
            tks.Token(name='NEWLINE', src=''),
        ]]

    else:
        raise ValueError(rsrc.kind)
