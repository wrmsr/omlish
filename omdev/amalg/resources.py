import ast
import base64
import itertools
import os.path
import typing as ta

import tokenize_rt as trt

from .. import tokens as tks
from .types import Tokens


##


class RootLevelResourcesRead(ta.NamedTuple):
    variable: str
    kind: ta.Literal['binary', 'text']
    resource: str


def is_root_level_resources_read(lts: Tokens) -> RootLevelResourcesRead | None:
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
) -> list[Tokens]:
    rf = os.path.join(os.path.dirname(path), rsrc.resource)

    if rsrc.kind == 'binary':
        with open(rf, 'rb') as bf:
            rb = bf.read()  # noqa

        out: list[Tokens] = [[
            trt.Token(name='NAME', src=rsrc.variable),
            trt.Token(name='UNIMPORTANT_WS', src=' '),
            trt.Token(name='OP', src='='),
            trt.Token(name='UNIMPORTANT_WS', src=' '),
            trt.Token(name='NAME', src='base64'),
            trt.Token(name='OP', src='.'),
            trt.Token(name='NAME', src='b64decode'),
            trt.Token(name='OP', src='('),
            trt.Token(name='NL', src='\n'),
        ]]

        rb64 = base64.b64encode(rb).decode('ascii')
        for chunk in itertools.batched(rb64, 96):
            out.append([
                trt.Token(name='UNIMPORTANT_WS', src='    '),
                trt.Token(name='STRING', src=f"'{''.join(chunk)}'"),
                trt.Token(name='NL', src='\n'),
            ])

        out.append([
            trt.Token(name='OP', src=')'),
            trt.Token(name='NEWLINE', src='\n'),
        ])

        return out

    elif rsrc.kind == 'text':
        with open(rf) as tf:
            rt = tf.read()  # noqa
        rt = rt.replace('\\', '\\\\')  # Escape backslashes
        rt = rt.replace('"""', r'\"\"\"')
        return [[
            trt.Token(name='NAME', src=rsrc.variable),
            trt.Token(name='UNIMPORTANT_WS', src=' '),
            trt.Token(name='OP', src='='),
            trt.Token(name='UNIMPORTANT_WS', src=' '),
            trt.Token(name='STRING', src=f'"""\\\n{rt}"""  # noqa\n'),
            trt.Token(name='NEWLINE', src=''),
        ]]

    else:
        raise ValueError(rsrc.kind)
