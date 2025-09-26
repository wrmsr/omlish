# @omlish-lite
# ruff: noqa: UP006 UP007 UP037 UP045
# Copyright (c) 2014, Saurabh Kumar (python-dotenv), 2013, Ted Tieken (django-dotenv-rw), 2013, Jacob Kaplan-Moss
# (django-dotenv)
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided with the distribution.
#
# - Neither the name of django-dotenv nor the names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# https://github.com/theskumar/python-dotenv/tree/4d505f2c9bc3569791e64bca0f2e4300f43df0e0/src/dotenv
import abc
import codecs
import contextlib
import io
import os
import pathlib
import re
import shutil
import tempfile
import typing as ta

from ..lite.abstract import Abstract
from ..logs.protocols import LoggerLike


##


_dotenv_posix_variable_pat: ta.Pattern[str] = re.compile(
    r"""
    \$\{
        (?P<name>[^}:]*)
        (?::-
            (?P<default>[^}]*)
        )?
    }
    """,
    re.VERBOSE,
)


class DotenvAtom(Abstract):
    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    @abc.abstractmethod
    def resolve(self, env: ta.Mapping[str, ta.Optional[str]]) -> str: ...


class DotenvLiteral(DotenvAtom):
    def __init__(self, value: str) -> None:
        super().__init__()

        self.value = value

    def __repr__(self) -> str:
        return f'DotenvLiteral(value={self.value})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash((self.__class__, self.value))

    def resolve(self, env: ta.Mapping[str, ta.Optional[str]]) -> str:
        return self.value


class DotenvVariable(DotenvAtom):
    def __init__(self, name: str, default: ta.Optional[str]) -> None:
        super().__init__()

        self.name = name
        self.default = default

    def __repr__(self) -> str:
        return f'DotenvVariable(name={self.name}, default={self.default})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.name, self.default) == (other.name, other.default)

    def __hash__(self) -> int:
        return hash((self.__class__, self.name, self.default))

    def resolve(self, env: ta.Mapping[str, ta.Optional[str]]) -> str:
        default = self.default if self.default is not None else ''
        result = env.get(self.name, default)
        return result if result is not None else ''


def parse_dotenv_variables(value: str) -> ta.Iterator[DotenvAtom]:
    cursor = 0

    for match in _dotenv_posix_variable_pat.finditer(value):
        (start, end) = match.span()
        name = match['name']
        default = match['default']

        if start > cursor:
            yield DotenvLiteral(value=value[cursor:start])

        yield DotenvVariable(name=name, default=default)
        cursor = end

    length = len(value)
    if cursor < length:
        yield DotenvLiteral(value=value[cursor:length])


##


def _make_dotenv_regex(string: str, extra_flags: int = 0) -> ta.Pattern[str]:
    return re.compile(string, re.UNICODE | extra_flags)


_dotenv_newline_pat = _make_dotenv_regex(r'(\r\n|\n|\r)')
_dotenv_multiline_whitespace_pat = _make_dotenv_regex(r'\s*', extra_flags=re.MULTILINE)
_dotenv_whitespace_pat = _make_dotenv_regex(r'[^\S\r\n]*')
_dotenv_export_pat = _make_dotenv_regex(r'(?:export[^\S\r\n]+)?')
_dotenv_single_quoted_key_pat = _make_dotenv_regex(r"'([^']+)'")
_dotenv_unquoted_key_pat = _make_dotenv_regex(r'([^=\#\s]+)')
_dotenv_equal_sign_pat = _make_dotenv_regex(r'(=[^\S\r\n]*)')
_dotenv_single_quoted_value_pat = _make_dotenv_regex(r"'((?:\\'|[^'])*)'")
_dotenv_double_quoted_value_pat = _make_dotenv_regex(r'"((?:\\"|[^"])*)"')
_dotenv_unquoted_value_pat = _make_dotenv_regex(r'([^\r\n]*)')
_dotenv_comment_pat = _make_dotenv_regex(r'(?:[^\S\r\n]*#[^\r\n]*)?')
_dotenv_end_of_line_pat = _make_dotenv_regex(r'[^\S\r\n]*(?:\r\n|\n|\r|$)')
_dotenv_rest_of_line_pat = _make_dotenv_regex(r'[^\r\n]*(?:\r|\n|\r\n)?')
_dotenv_double_quote_escapes_pat = _make_dotenv_regex(r"\\[\\'\"abfnrtv]")
_dotenv_single_quote_escapes_pat = _make_dotenv_regex(r"\\[\\']")


class DotenvOriginal(ta.NamedTuple):
    string: str
    line: int


class DotenvBinding(ta.NamedTuple):
    key: ta.Optional[str]
    value: ta.Optional[str]
    original: DotenvOriginal
    error: bool


class _DotenvPosition:
    def __init__(self, chars: int, line: int) -> None:
        super().__init__()

        self.chars = chars
        self.line = line

    @classmethod
    def start(cls) -> '_DotenvPosition':
        return cls(chars=0, line=1)

    def set(self, other: '_DotenvPosition') -> None:
        self.chars = other.chars
        self.line = other.line

    def advance(self, string: str) -> None:
        self.chars += len(string)
        self.line += len(re.findall(_dotenv_newline_pat, string))


class DotenvError(Exception):
    pass


class _DotenvReader:
    def __init__(self, stream: ta.IO[str]) -> None:
        super().__init__()

        self.string = stream.read()
        self.position = _DotenvPosition.start()
        self.mark = _DotenvPosition.start()

    def has_next(self) -> bool:
        return self.position.chars < len(self.string)

    def set_mark(self) -> None:
        self.mark.set(self.position)

    def get_marked(self) -> DotenvOriginal:
        return DotenvOriginal(
            string=self.string[self.mark.chars:self.position.chars],
            line=self.mark.line,
        )

    def peek(self, count: int) -> str:
        return self.string[self.position.chars:self.position.chars + count]

    def read(self, count: int) -> str:
        result = self.string[self.position.chars:self.position.chars + count]
        if len(result) < count:
            raise DotenvError('read: End of string')
        self.position.advance(result)
        return result

    def read_regex(self, regex: ta.Pattern[str]) -> ta.Sequence[str]:
        match = regex.match(self.string, self.position.chars)
        if match is None:
            raise DotenvError('read_regex: Pattern not found')
        self.position.advance(self.string[match.start():match.end()])
        return match.groups()


def _decode_dotenv_escapes(regex: ta.Pattern[str], string: str) -> str:
    def decode_match(match: ta.Match[str]) -> str:
        return codecs.decode(match.group(0), 'unicode-escape')

    return regex.sub(decode_match, string)


def _parse_dotenv_key(reader: _DotenvReader) -> ta.Optional[str]:
    char = reader.peek(1)
    if char == '#':
        return None
    elif char == "'":
        (key,) = reader.read_regex(_dotenv_single_quoted_key_pat)
    else:
        (key,) = reader.read_regex(_dotenv_unquoted_key_pat)
    return key


def _parse_dotenv_unquoted_value(reader: _DotenvReader) -> str:
    (part,) = reader.read_regex(_dotenv_unquoted_value_pat)
    return re.sub(r'\s+#.*', '', part).rstrip()


def _parse_dotenv_value(reader: _DotenvReader) -> str:
    char = reader.peek(1)
    if char == "'":
        (value,) = reader.read_regex(_dotenv_single_quoted_value_pat)
        return _decode_dotenv_escapes(_dotenv_single_quote_escapes_pat, value)
    elif char == '"':
        (value,) = reader.read_regex(_dotenv_double_quoted_value_pat)
        return _decode_dotenv_escapes(_dotenv_double_quote_escapes_pat, value)
    elif char in ('', '\n', '\r'):
        return ''
    else:
        return _parse_dotenv_unquoted_value(reader)


def _parse_dotenv_binding(reader: _DotenvReader) -> DotenvBinding:
    reader.set_mark()
    try:
        reader.read_regex(_dotenv_multiline_whitespace_pat)
        if not reader.has_next():
            return DotenvBinding(
                key=None,
                value=None,
                original=reader.get_marked(),
                error=False,
            )
        reader.read_regex(_dotenv_export_pat)
        key = _parse_dotenv_key(reader)
        reader.read_regex(_dotenv_whitespace_pat)
        if reader.peek(1) == '=':
            reader.read_regex(_dotenv_equal_sign_pat)
            value: ta.Optional[str] = _parse_dotenv_value(reader)
        else:
            value = None
        reader.read_regex(_dotenv_comment_pat)
        reader.read_regex(_dotenv_end_of_line_pat)
        return DotenvBinding(
            key=key,
            value=value,
            original=reader.get_marked(),
            error=False,
        )
    except DotenvError:
        reader.read_regex(_dotenv_rest_of_line_pat)
        return DotenvBinding(
            key=None,
            value=None,
            original=reader.get_marked(),
            error=True,
        )


def parse_dotenv_stream(stream: ta.IO[str]) -> ta.Iterator[DotenvBinding]:
    reader = _DotenvReader(stream)
    while reader.has_next():
        yield _parse_dotenv_binding(reader)


##


def _dotenv_with_warn_for_invalid_lines(
        mappings: ta.Iterator[DotenvBinding],
        log: ta.Optional[LoggerLike] = None,
) -> ta.Iterator[DotenvBinding]:
    for mapping in mappings:
        if mapping.error:
            if log is not None:
                log.warning(
                    'dotenv could not parse statement starting at line %s',
                    mapping.original.line,
                )
        yield mapping


StrStrMutableMappingT = ta.TypeVar('StrStrMutableMappingT', bound=ta.MutableMapping[str, str])


class Dotenv:
    def __init__(
        self,
        path: ta.Union[str, 'os.PathLike[str]', None] = None,
        stream: ta.Optional[ta.IO[str]] = None,
        verbose: bool = False,
        encoding: ta.Optional[str] = None,
        interpolate: bool = True,
        override: bool = True,
        env: ta.Optional[ta.Mapping[str, str]] = None,
        log: ta.Optional[LoggerLike] = None,
    ) -> None:
        super().__init__()

        self.path: ta.Union[str, 'os.PathLike[str]', None] = path
        self.stream: ta.Optional[ta.IO[str]] = stream
        self._dict: ta.Optional[ta.Dict[str, ta.Optional[str]]] = None
        self.verbose: bool = verbose
        self.encoding: ta.Optional[str] = encoding
        self.interpolate: bool = interpolate
        self.override: bool = override
        self.env = env or {}
        self.log = log

    @contextlib.contextmanager
    def _get_stream(self) -> ta.Iterator[ta.IO[str]]:
        if self.path and os.path.isfile(self.path):
            with open(self.path, encoding=self.encoding) as stream:
                yield stream
        elif self.stream is not None:
            yield self.stream
        else:
            if self.verbose:
                if self.log is not None:
                    self.log.info(
                        'dotenv could not find configuration file %s.',
                        self.path or '.env',
                    )
            yield io.StringIO('')

    def dict(self) -> ta.Dict[str, ta.Optional[str]]:
        if self._dict:
            return self._dict

        raw_values = self.parse()

        if self.interpolate:
            self._dict = dotenv_resolve_variables(raw_values, override=self.override, env=self.env)
        else:
            self._dict = dict(raw_values)

        return self._dict

    def apply_to(self, dst: StrStrMutableMappingT) -> StrStrMutableMappingT:
        for k, v in self.dict().items():
            if v is not None:
                dst[k] = v
            elif k in dst:
                del dst[k]
        return dst

    def parse(self) -> ta.Iterator[ta.Tuple[str, ta.Optional[str]]]:
        with self._get_stream() as stream:
            for mapping in _dotenv_with_warn_for_invalid_lines(parse_dotenv_stream(stream), self.log):
                if mapping.key is not None:
                    yield mapping.key, mapping.value

    def get(self, key: str) -> ta.Optional[str]:
        data = self.dict()

        if key in data:
            return data[key]

        if self.verbose:
            if self.log is not None:
                self.log.warning('Key %s not found in %s.', key, self.path)

        return None


##


def dotenv_get_key(
    path: ta.Union[str, 'os.PathLike[str]'],
    key_to_get: str,
    *,
    encoding: ta.Optional[str] = 'utf-8',
    log: ta.Optional[LoggerLike] = None,
) -> ta.Optional[str]:
    """
    Get the value of a given key from the given .env.

    Returns `None` if the key isn't found or doesn't have a value.
    """

    return Dotenv(
        path,
        verbose=True,
        encoding=encoding,
        log=log,
    ).get(key_to_get)


@contextlib.contextmanager
def _dotenv_rewrite(
    path: ta.Union[str, 'os.PathLike[str]'],
    encoding: ta.Optional[str],
) -> ta.Iterator[ta.Tuple[ta.IO[str], ta.IO[str]]]:
    pathlib.Path(path).touch()

    with tempfile.NamedTemporaryFile(mode='w', encoding=encoding, delete=False) as dest:
        error = None
        try:
            with open(path, encoding=encoding) as source:
                yield (source, dest)
        except BaseException as err:  # noqa
            error = err

    if error is None:
        shutil.move(dest.name, path)
    else:
        os.unlink(dest.name)
        raise error from None


def dotenv_set_key(
    path: ta.Union[str, 'os.PathLike[str]'],
    key_to_set: str,
    value_to_set: str,
    *,
    quote_mode: str = 'always',
    export: bool = False,
    encoding: ta.Optional[str] = 'utf-8',
    log: ta.Optional[LoggerLike] = None,
) -> ta.Tuple[ta.Optional[bool], str, str]:
    """
    Adds or Updates a key/value to the given .env

    If the .env path given doesn't exist, fails instead of risking creating
    an orphan .env somewhere in the filesystem
    """

    if quote_mode not in ('always', 'auto', 'never'):
        raise ValueError(f'Unknown quote_mode: {quote_mode}')

    quote = (
        quote_mode == 'always'
        or (quote_mode == 'auto' and not value_to_set.isalnum())
    )

    if quote:
        value_out = "'{}'".format(value_to_set.replace("'", "\\'"))
    else:
        value_out = value_to_set
    if export:
        line_out = f'export {key_to_set}={value_out}\n'
    else:
        line_out = f'{key_to_set}={value_out}\n'

    with _dotenv_rewrite(path, encoding=encoding) as (source, dest):
        replaced = False
        missing_newline = False
        for mapping in _dotenv_with_warn_for_invalid_lines(parse_dotenv_stream(source), log):
            if mapping.key == key_to_set:
                dest.write(line_out)
                replaced = True
            else:
                dest.write(mapping.original.string)
                missing_newline = not mapping.original.string.endswith('\n')
        if not replaced:
            if missing_newline:
                dest.write('\n')
            dest.write(line_out)

    return True, key_to_set, value_to_set


def dotenv_unset_key(
    path: ta.Union[str, 'os.PathLike[str]'],
    key_to_unset: str,
    *,
    quote_mode: str = 'always',
    encoding: ta.Optional[str] = 'utf-8',
    log: ta.Optional[LoggerLike] = None,
) -> ta.Tuple[ta.Optional[bool], str]:
    """
    Removes a given key from the given `.env` file.

    If the .env path given doesn't exist, fails.
    If the given key doesn't exist in the .env, fails.
    """

    if not os.path.exists(path):
        if log is not None:
            log.warning("Can't delete from %s - it doesn't exist.", path)
        return None, key_to_unset

    removed = False
    with _dotenv_rewrite(path, encoding=encoding) as (source, dest):
        for mapping in _dotenv_with_warn_for_invalid_lines(parse_dotenv_stream(source), log):
            if mapping.key == key_to_unset:
                removed = True
            else:
                dest.write(mapping.original.string)

    if not removed:
        if log is not None:
            log.warning("Key %s not removed from %s - key doesn't exist.", key_to_unset, path)
        return None, key_to_unset

    return removed, key_to_unset


def dotenv_resolve_variables(
        values: ta.Iterable[ta.Tuple[str, ta.Optional[str]]],
        override: bool,
        env: ta.Mapping[str, str],
) -> ta.Dict[str, ta.Optional[str]]:
    new_values: ta.Dict[str, ta.Optional[str]] = {}

    for (name, value) in values:
        if value is None:
            result = None
        else:
            atoms = parse_dotenv_variables(value)
            aenv: ta.Dict[str, ta.Optional[str]] = {}
            if override:
                aenv.update(env)
                aenv.update(new_values)
            else:
                aenv.update(new_values)
                aenv.update(env)
            result = ''.join(atom.resolve(aenv) for atom in atoms)

        new_values[name] = result

    return new_values


def dotenv_values(
    path: ta.Union[str, 'os.PathLike[str]', None] = None,
    stream: ta.Optional[ta.IO[str]] = None,
    *,
    verbose: bool = False,
    interpolate: bool = True,
    encoding: ta.Optional[str] = 'utf-8',
    env: ta.Optional[ta.Mapping[str, str]] = None,
    log: ta.Optional[LoggerLike] = None,
) -> ta.Dict[str, ta.Optional[str]]:
    """
    Parse a .env file and return its content as a dict.

    The returned dict will have `None` values for keys without values in the .env file.
    For example, `foo=bar` results in `{"foo": "bar"}` whereas `foo` alone results in
    `{"foo": None}`

    Args:
        path: Absolute or relative path to the .env file.
        stream: `StringIO` object with .env content, used if `path` is `None`.
        verbose: Whether to output a warning if the .env file is missing.
        encoding: Encoding to be used to read the file.

    If both `path` and `stream` are `None`, `find_dotenv()` is used to find the
    .env file.
    """

    if path is None and stream is None:
        raise ValueError('must set path or stream')

    return Dotenv(
        path=path,
        stream=stream,
        verbose=verbose,
        interpolate=interpolate,
        override=True,
        encoding=encoding,
        env=env,
        log=log,
    ).dict()
