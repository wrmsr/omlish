import os.path
import typing as ta


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
