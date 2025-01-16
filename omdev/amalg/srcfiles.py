import dataclasses as dc
import typing as ta

from omlish import collections as col
from omlish import lang

from ..tokens import all as tks
from .imports import Import
from .imports import make_import
from .manifests import comment_out_manifest_comment
from .manifests import is_manifest_comment
from .resources import build_resource_lines
from .resources import is_root_level_resources_read
from .strip import split_header_lines
from .strip import strip_header_lines
from .typing import Typing
from .typing import is_root_level_if_type_checking_block
from .typing import make_typing
from .typing import skip_root_level_if_type_checking_block


##


@dc.dataclass(frozen=True, kw_only=True)
class SrcFile:
    path: str

    src: str = dc.field(repr=False)
    tokens: tks.Tokens = dc.field(repr=False)
    lines: ta.Sequence[tks.Tokens] = dc.field(repr=False)

    header_lines: ta.Sequence[tks.Tokens] = dc.field(repr=False)
    imports: ta.Sequence[Import] = dc.field(repr=False)
    typings: ta.Sequence[Typing] = dc.field(repr=False)
    content_lines: ta.Sequence[tks.Tokens] = dc.field(repr=False)

    ruff_noqa: ta.AbstractSet[str] = dc.field(repr=False)

    has_binary_resources: bool = False


def make_src_file(
        path: str,
        *,
        mounts: ta.Mapping[str, str],
) -> SrcFile:
    with open(path) as f:
        src = f.read().strip()

    tokens = tks.src_to_tokens(src)
    lines = tks.split_lines(tokens)

    header_lines, cls = split_header_lines(lines)

    header_lines = strip_header_lines(header_lines)
    rnls, header_lines = col.partition(header_lines, lambda l: tks.join_toks(l).startswith('# ruff: noqa: '))

    imps: list[Import] = []
    tys: list[Typing] = []
    ctls: list[tks.Tokens] = []

    has_binary_resources = False

    i = 0
    while i < len(cls):
        line = cls[i]
        i += 1

        if (imp := make_import(
                line,
                src_path=path,
                mounts=mounts,
        )) is not None:
            imps.append(imp)

        elif (ty := make_typing(
                line,
                src_path=path,
        )) is not None:
            tys.append(ty)

        elif is_manifest_comment(line):
            out, i = comment_out_manifest_comment(line, cls, i)
            ctls.extend(out)

        elif is_root_level_if_type_checking_block(line):
            i = skip_root_level_if_type_checking_block(cls, i)

        elif (rsrc := is_root_level_resources_read(line)) is not None:
            ctls.extend(build_resource_lines(
                rsrc,
                path,
            ))

            if rsrc.kind == 'binary':
                has_binary_resources = True

        else:
            ctls.append(line)

    return SrcFile(
        path=path,

        src=src,
        tokens=tokens,
        lines=lines,

        header_lines=header_lines,
        imports=imps,
        typings=tys,
        content_lines=ctls,

        ruff_noqa=set(lang.flatten(tks.join_toks(l).strip().split()[3:] for l in rnls)),  # noqa

        has_binary_resources=has_binary_resources,
    )
