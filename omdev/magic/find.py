import functools
import os.path
import re
import typing as ta

from .magic import Magic
from .prepare import MagicPrepareError
from .prepare import py_compile_magic_preparer
from .styles import PY_MAGIC_STYLE
from .styles import MagicStyle


##


def compile_magic_style_pat(style: MagicStyle) -> re.Pattern:
    ms: list[str] = []

    if style.line_prefix is not None:
        ms.append(style.line_prefix + style.key_prefix)
    if style.block_prefix_suffix is not None:
        ms.append(style.block_prefix_suffix[0] + style.key_prefix)

    if not ms:
        raise Exception('No prefixes')

    p = '|'.join('(' + re.escape(m) + r'\S*)' for m in ms)
    s = '^(' + p + r')($|(\s.*))'
    return re.compile(s)


##


def chop_magic_lines(
        magic_key: str,
        prefix: str,
        lines: ta.Iterable[str],
) -> list[str] | None:
    out: list[str] = []
    for i, line in enumerate(lines):
        if not i:
            if not line.startswith(prefix + magic_key):
                return None
            out.append(line[len(prefix) + len(magic_key) + 1:])
        else:
            if not line.startswith(prefix):
                return None
            out.append(line[len(prefix):])
    return out


def chop_magic_block(
        magic_key: str,
        prefix: str,
        suffix: str,
        lines: ta.Iterable[str],
) -> list[str] | None:
    out: list[str] = []
    for i, line in enumerate(lines):
        if not i:
            if not line.startswith(prefix + magic_key):
                return None
            s = line[len(prefix) + len(magic_key) + 1:]
            if s.rstrip().endswith(suffix):
                out.append(s.rstrip()[:-len(suffix)])
                break
            out.append(s)
        elif line.rstrip().endswith(suffix):
            out.append(line.rstrip()[:-len(suffix)])
            break
        else:
            out.append(line)
    return out


##


def find_magic(
        style: MagicStyle,
        lines: ta.Sequence[str],
        *,
        file: str | None = None,
        preparer: ta.Callable[[str], ta.Any] = py_compile_magic_preparer,
) -> list[Magic]:
    out: list[Magic] = []

    start = 0
    while start < len(lines):
        start_line = lines[start]

        chopper: ta.Callable[[ta.Iterable[str]], list[str] | None]
        if (
                style.line_prefix is not None and
                start_line.startswith(style.line_prefix + style.key_prefix)
        ):
            key = start_line[len(style.line_prefix):].split()[0]
            chopper = functools.partial(
                chop_magic_lines,
                key,
                style.line_prefix,
            )

        elif (
                style.block_prefix_suffix is not None and
                start_line.startswith(style.block_prefix_suffix[0] + style.key_prefix)
        ):
            key = start_line[len(style.block_prefix_suffix[0]):].split()[0]
            chopper = functools.partial(
                chop_magic_block,
                key,
                *style.block_prefix_suffix,
            )

        else:
            start += 1
            continue

        end = start
        magic: Magic | None = None
        while end < len(lines):
            block_lines = chopper(lines[start:end + 1])
            if block_lines is None:
                raise Exception(f'Failed to find magic block terminator : {file=} {start=} {end=}')

            block_src = ''.join(block_lines)
            if not block_src:
                prepared = None
            else:
                try:
                    prepared = preparer(block_src)
                except MagicPrepareError:
                    end += 1
                    continue

            magic = Magic(
                key=key,
                file=file,
                start_line=start + 1,
                end_line=end + 1,
                body=block_src,
                prepared=prepared,
            )
            break

        if magic is None:
            raise Exception(f'Failed to find magic block terminator : {file=} {start=} {end=}')

        out.append(magic)
        start = end + 1

    return out


##


def find_magic_files(
        style: MagicStyle,
        roots: ta.Sequence[str],
) -> ta.Iterator[str]:
    if isinstance(roots, str):
        raise TypeError(roots)

    pat = compile_magic_style_pat(style)

    for root in roots:
        for dp, dns, fns in os.walk(root):  # noqa
            for fn in fns:
                if not any(fn.endswith(f'.{x}') for x in style.exts):
                    continue

                fp = os.path.join(dp, fn)
                try:
                    with open(fp) as f:
                        src = f.read()
                except UnicodeDecodeError:
                    continue

                if not any(pat.fullmatch(l) for l in src.splitlines()):
                    continue

                yield fp


def find_magic_py_modules(
        roots: ta.Sequence[str],
        *,
        style: MagicStyle = PY_MAGIC_STYLE,
) -> ta.Iterator[str]:
    for fp in find_magic_files(style, roots):
        dp = os.path.dirname(fp)
        fn = os.path.basename(fp)

        if fn == '__init__.py':
            yield dp.replace(os.sep, '.')
        elif fn.endswith('.py'):
            yield fp[:-3].replace(os.sep, '.')
        else:
            yield fp
