"""
TODO:
 - better bad unicode handling
 - read whole file if < some size, report filesize / num lines / mtime inline
 - fs cache
 - track changes
"""
import difflib
import io
import itertools
import os.path
import typing as ta

from omlish import lang

from ...tools.execution.catalog import ToolCatalogEntry
from ...tools.execution.reflect import reflect_tool_catalog_entry
from ...tools.reflect import tool_spec_override
from ...tools.types import ToolParam


##


IMAGE_FILE_EXTENSIONS: ta.AbstractSet[str] = frozenset([
    'jpg',
    'jpeg',
    'png',
    'gif',
    'bmp',
    'webp',
])


ARCHIVE_FILE_EXTENSIONS: ta.AbstractSet[str] = frozenset([
    'zip',
    'tar',
    'gz',
    'xz',
    '7z',
])


DOC_FILE_EXTENSIONS: ta.AbstractSet[str] = frozenset([
    'doc',
    'docx',
    'xls',
    'xlsx',
    'ppt',
    'pptx',
    'odt',
    'ods',
    'odp',
])


EXECUTABLE_FILE_EXTENSIONS: ta.AbstractSet[str] = frozenset([
    'exe',
    'dll',
    'so',

    'obj',
    'o',
    'a',
    'lib',

    'class',
    'jar',
    'war',

    'wasm',

    'pyc',
    'pyo',
])


BLOB_FILE_EXTENSIONS: ta.AbstractSet[str] = frozenset([
    'bin',
    'dat',
])


BINARY_FILE_EXTENSIONS: ta.AbstractSet[str] = frozenset([
    *IMAGE_FILE_EXTENSIONS,
    *ARCHIVE_FILE_EXTENSIONS,
    *DOC_FILE_EXTENSIONS,
    *EXECUTABLE_FILE_EXTENSIONS,
    *BLOB_FILE_EXTENSIONS,
])


def has_binary_file_extension(file_path: str) -> bool:
    return os.path.basename(file_path).partition('.')[-1] in BINARY_FILE_EXTENSIONS


##


def is_binary_file(
        file_path: str,
        *,
        chunk_size: int = 0x1000,
        non_printable_cutoff: float = .3,

        st: os.stat_result | None = None,
) -> bool:
    if st is None:
        try:
            st = os.stat(file_path)
        except OSError:
            return False

    if not st.st_size:
        return False

    with open(file_path, 'rb') as f:
        chunk = f.read(chunk_size)

    if 0 in chunk:
        return True

    # Count "non-printable" ASCII-ish control chars (excluding TAB/LF/CR)
    np = sum(1 for b in chunk if b < 9 or (13 < b < 32))
    return (np / len(chunk)) > non_printable_cutoff


##


def get_suggestions(
        file_path: str,
        n: int = 3,
        *,
        cutoff: float = .6,
) -> ta.Sequence[str] | None:
    fl = [
        e.name
        for e in os.scandir(os.path.dirname(file_path))
        if e.is_file()
        and not has_binary_file_extension(e.name)
    ]

    return difflib.get_close_matches(
        os.path.basename(file_path),
        fl,
        n,
        cutoff=cutoff,
    )


##


DEFAULT_MAX_NUM_LINES = 2_000

MAX_LINE_LENGTH = 2_000


@tool_spec_override(
    desc=rf"""
        Reads a file from the local filesystem. You can access any file directly by using this tool.

        Assume this tool is able to read all files on the machine. If the User provides a path to a file assume that
        path is valid. It is okay to read a file that does not exist; an error will be returned.

        Usage:
        - The file_path parameter must be an absolute path, not a relative path.
        - By default, it reads up to {DEFAULT_MAX_NUM_LINES} lines starting from the beginning of the file.
        - You can optionally specify a line offset and limit (especially handy for long files), but it's recommended to
          read the whole file by not providing these parameters.
        - Any lines longer than {MAX_LINE_LENGTH} characters will be truncated with "...".
        - Invalid unicode characters will be replaced with the unicode replacement character "\\ufffd".
        - Results are returned using cat -n format, with line numbers starting at 1 and suffixed with a pipe character
          "|".
        - This tool cannot read binary files, including images.
""",
    params=[
        ToolParam(
            'file_path',
            desc='The absolute path to the file to read.',
        ),
        ToolParam(
            'line_offset',
            desc='The line number to start reading from (0-based).',
        ),
        ToolParam(
            'num_lines',
            desc=f'The number of lines to read (defaults to {DEFAULT_MAX_NUM_LINES}).',
        ),
    ],
)
def execute_read_tool(
        file_path: str,
        *,
        line_offset: int = 0,
        num_lines: int = DEFAULT_MAX_NUM_LINES,
) -> str:
    try:
        st = os.stat(file_path)
    except OSError:
        if (sug := get_suggestions(file_path)):
            raise FileNotFoundError(
                f'File not found: {file_path}\nDid you mean one of these?\n{"\n".join(sug)}',
            ) from None
        raise FileNotFoundError(f'File not found: {file_path}') from None

    if is_binary_file(file_path, st=st):
        raise OSError(f'Cannot read binary file: {file_path}')

    out = io.StringIO()
    out.write('<file>\n')

    zp = len(str(line_offset + num_lines))
    n = line_offset
    has_trunc = False  # noqa
    with open(file_path, errors='replace') as f:
        fi = iter(f)

        for line in itertools.islice(fi, line_offset, line_offset + num_lines):
            out.write(f'{str(n + 1).zfill(zp):}|')
            line = line.removesuffix('\n')
            if len(line) > MAX_LINE_LENGTH:
                has_trunc = True  # noqa
                out.write(line[:MAX_LINE_LENGTH])
                out.write('...')
            else:
                out.write(line)
            out.write('\n')
            n += 1

        # tl = n
        # if (ml := lang.ilen(fi)):
        #     check.state(n == num_lines)
        #     tl += ml

        try:
            next(fi)
        except StopIteration:
            has_more = False
        else:
            has_more = True

    out.write(f'</file>\n')

    if has_more:
        out.write(
            f'\n(File has more lines. Use "line_offset" parameter to read beyond line {line_offset + num_lines}.)\n',
        )

    return out.getvalue()


@lang.cached_function
def read_tool() -> ToolCatalogEntry:
    return reflect_tool_catalog_entry(execute_read_tool)
