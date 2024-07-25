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
import abc
import codecs
import contextlib
import io
import logging
import os
import pathlib
import re
import shutil
import tempfile
import typing as ta

##


logger = logging.getLogger(__name__)


##


_posix_variable: ta.Pattern[str] = re.compile(
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


class Atom(metaclass=abc.ABCMeta):
    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    @abc.abstractmethod
    def resolve(self, env: ta.Mapping[str, str | None]) -> str: ...


class Literal(Atom):
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f'Literal(value={self.value})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash((self.__class__, self.value))

    def resolve(self, env: ta.Mapping[str, str | None]) -> str:
        return self.value


class Variable(Atom):
    def __init__(self, name: str, default: str | None) -> None:
        self.name = name
        self.default = default

    def __repr__(self) -> str:
        return f'Variable(name={self.name}, default={self.default})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.name, self.default) == (other.name, other.default)

    def __hash__(self) -> int:
        return hash((self.__class__, self.name, self.default))

    def resolve(self, env: ta.Mapping[str, str | None]) -> str:
        default = self.default if self.default is not None else ''
        result = env.get(self.name, default)
        return result if result is not None else ''


def parse_variables(value: str) -> ta.Iterator[Atom]:
    cursor = 0

    for match in _posix_variable.finditer(value):
        (start, end) = match.span()
        name = match['name']
        default = match['default']

        if start > cursor:
            yield Literal(value=value[cursor:start])

        yield Variable(name=name, default=default)
        cursor = end

    length = len(value)
    if cursor < length:
        yield Literal(value=value[cursor:length])


##


def make_regex(string: str, extra_flags: int = 0) -> ta.Pattern[str]:
    return re.compile(string, re.UNICODE | extra_flags)


_newline = make_regex(r'(\r\n|\n|\r)')
_multiline_whitespace = make_regex(r'\s*', extra_flags=re.MULTILINE)
_whitespace = make_regex(r'[^\S\r\n]*')
_export = make_regex(r'(?:export[^\S\r\n]+)?')
_single_quoted_key = make_regex(r"'([^']+)'")
_unquoted_key = make_regex(r'([^=\#\s]+)')
_equal_sign = make_regex(r'(=[^\S\r\n]*)')
_single_quoted_value = make_regex(r"'((?:\\'|[^'])*)'")
_double_quoted_value = make_regex(r'"((?:\\"|[^"])*)"')
_unquoted_value = make_regex(r'([^\r\n]*)')
_comment = make_regex(r'(?:[^\S\r\n]*#[^\r\n]*)?')
_end_of_line = make_regex(r'[^\S\r\n]*(?:\r\n|\n|\r|$)')
_rest_of_line = make_regex(r'[^\r\n]*(?:\r|\n|\r\n)?')
_double_quote_escapes = make_regex(r"\\[\\'\"abfnrtv]")
_single_quote_escapes = make_regex(r"\\[\\']")


class Original(ta.NamedTuple):
    string: str
    line: int


class Binding(ta.NamedTuple):
    key: str | None
    value: str | None
    original: Original
    error: bool


class Position:
    def __init__(self, chars: int, line: int) -> None:
        self.chars = chars
        self.line = line

    @classmethod
    def start(cls) -> 'Position':
        return cls(chars=0, line=1)

    def set(self, other: 'Position') -> None:
        self.chars = other.chars
        self.line = other.line

    def advance(self, string: str) -> None:
        self.chars += len(string)
        self.line += len(re.findall(_newline, string))


class Error(Exception):
    pass


class Reader:
    def __init__(self, stream: ta.IO[str]) -> None:
        self.string = stream.read()
        self.position = Position.start()
        self.mark = Position.start()

    def has_next(self) -> bool:
        return self.position.chars < len(self.string)

    def set_mark(self) -> None:
        self.mark.set(self.position)

    def get_marked(self) -> Original:
        return Original(
            string=self.string[self.mark.chars:self.position.chars],
            line=self.mark.line,
        )

    def peek(self, count: int) -> str:
        return self.string[self.position.chars:self.position.chars + count]

    def read(self, count: int) -> str:
        result = self.string[self.position.chars:self.position.chars + count]
        if len(result) < count:
            raise Error('read: End of string')
        self.position.advance(result)
        return result

    def read_regex(self, regex: ta.Pattern[str]) -> ta.Sequence[str]:
        match = regex.match(self.string, self.position.chars)
        if match is None:
            raise Error('read_regex: Pattern not found')
        self.position.advance(self.string[match.start():match.end()])
        return match.groups()


def decode_escapes(regex: ta.Pattern[str], string: str) -> str:
    def decode_match(match: ta.Match[str]) -> str:
        return codecs.decode(match.group(0), 'unicode-escape')  # type: ignore

    return regex.sub(decode_match, string)


def parse_key(reader: Reader) -> str | None:
    char = reader.peek(1)
    if char == '#':
        return None
    elif char == "'":
        (key,) = reader.read_regex(_single_quoted_key)
    else:
        (key,) = reader.read_regex(_unquoted_key)
    return key


def parse_unquoted_value(reader: Reader) -> str:
    (part,) = reader.read_regex(_unquoted_value)
    return re.sub(r'\s+#.*', '', part).rstrip()


def parse_value(reader: Reader) -> str:
    char = reader.peek(1)
    if char == "'":
        (value,) = reader.read_regex(_single_quoted_value)
        return decode_escapes(_single_quote_escapes, value)
    elif char == '"':
        (value,) = reader.read_regex(_double_quoted_value)
        return decode_escapes(_double_quote_escapes, value)
    elif char in ('', '\n', '\r'):
        return ''
    else:
        return parse_unquoted_value(reader)


def parse_binding(reader: Reader) -> Binding:
    reader.set_mark()
    try:
        reader.read_regex(_multiline_whitespace)
        if not reader.has_next():
            return Binding(
                key=None,
                value=None,
                original=reader.get_marked(),
                error=False,
            )
        reader.read_regex(_export)
        key = parse_key(reader)
        reader.read_regex(_whitespace)
        if reader.peek(1) == '=':
            reader.read_regex(_equal_sign)
            value: str | None = parse_value(reader)
        else:
            value = None
        reader.read_regex(_comment)
        reader.read_regex(_end_of_line)
        return Binding(
            key=key,
            value=value,
            original=reader.get_marked(),
            error=False,
        )
    except Error:
        reader.read_regex(_rest_of_line)
        return Binding(
            key=None,
            value=None,
            original=reader.get_marked(),
            error=True,
        )


def parse_stream(stream: ta.IO[str]) -> ta.Iterator[Binding]:
    reader = Reader(stream)
    while reader.has_next():
        yield parse_binding(reader)


##


# A type alias for a string path to be used for the paths in this file. These paths may flow to `open()` and
# `shutil.move()`; `shutil.move()` only accepts string paths, not byte paths or file descriptors. See
# https://github.com/python/typeshed/pull/6832.
StrPath: ta.TypeAlias = ta.Union[str, 'os.PathLike[str]']


def with_warn_for_invalid_lines(mappings: ta.Iterator[Binding]) -> ta.Iterator[Binding]:
    for mapping in mappings:
        if mapping.error:
            logger.warning(
                'dotenv could not parse statement starting at line %s',
                mapping.original.line,
            )
        yield mapping


class DotEnv:
    def __init__(
        self,
        dotenv_path: StrPath | None,
        stream: ta.IO[str] | None = None,
        verbose: bool = False,
        encoding: str | None = None,
        interpolate: bool = True,
        override: bool = True,
    ) -> None:
        super().__init__()
        self.dotenv_path: StrPath | None = dotenv_path
        self.stream: ta.IO[str] | None = stream
        self._dict: dict[str, str | None] | None = None
        self.verbose: bool = verbose
        self.encoding: str | None = encoding
        self.interpolate: bool = interpolate
        self.override: bool = override

    @contextlib.contextmanager
    def _get_stream(self) -> ta.Iterator[ta.IO[str]]:
        if self.dotenv_path and os.path.isfile(self.dotenv_path):
            with open(self.dotenv_path, encoding=self.encoding) as stream:
                yield stream
        elif self.stream is not None:
            yield self.stream
        else:
            if self.verbose:
                logger.info(
                    'dotenv could not find configuration file %s.',
                    self.dotenv_path or '.env',
                )
            yield io.StringIO('')

    def dict(self) -> dict[str, str | None]:
        """Return dotenv as dict"""
        if self._dict:
            return self._dict

        raw_values = self.parse()

        if self.interpolate:
            self._dict = resolve_variables(raw_values, override=self.override)
        else:
            self._dict = raw_values

        return self._dict

    def parse(self) -> ta.Iterator[tuple[str, str | None]]:
        with self._get_stream() as stream:
            for mapping in with_warn_for_invalid_lines(parse_stream(stream)):
                if mapping.key is not None:
                    yield mapping.key, mapping.value

    def set_as_environment_variables(self) -> bool:
        """
        Load the current dotenv as system environment variable.
        """
        if not self.dict():
            return False

        for k, v in self.dict().items():
            if k in os.environ and not self.override:
                continue
            if v is not None:
                os.environ[k] = v

        return True

    def get(self, key: str) -> str | None:
        """
        """
        data = self.dict()

        if key in data:
            return data[key]

        if self.verbose:
            logger.warning('Key %s not found in %s.', key, self.dotenv_path)

        return None


def get_key(
    dotenv_path: StrPath,
    key_to_get: str,
    encoding: str | None = 'utf-8',
) -> str | None:
    """
    Get the value of a given key from the given .env.

    Returns `None` if the key isn't found or doesn't have a value.
    """
    return DotEnv(dotenv_path, verbose=True, encoding=encoding).get(key_to_get)


@contextlib.contextmanager
def rewrite(
    path: StrPath,
    encoding: str | None,
) -> ta.Iterator[tuple[ta.IO[str], ta.IO[str]]]:
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


def set_key(
    dotenv_path: StrPath,
    key_to_set: str,
    value_to_set: str,
    quote_mode: str = 'always',
    export: bool = False,
    encoding: str | None = 'utf-8',
) -> tuple[bool | None, str, str]:
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

    with rewrite(dotenv_path, encoding=encoding) as (source, dest):
        replaced = False
        missing_newline = False
        for mapping in with_warn_for_invalid_lines(parse_stream(source)):
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


def unset_key(
    dotenv_path: StrPath,
    key_to_unset: str,
    quote_mode: str = 'always',
    encoding: str | None = 'utf-8',
) -> tuple[bool | None, str]:
    """
    Removes a given key from the given `.env` file.

    If the .env path given doesn't exist, fails.
    If the given key doesn't exist in the .env, fails.
    """
    if not os.path.exists(dotenv_path):
        logger.warning("Can't delete from %s - it doesn't exist.", dotenv_path)
        return None, key_to_unset

    removed = False
    with rewrite(dotenv_path, encoding=encoding) as (source, dest):
        for mapping in with_warn_for_invalid_lines(parse_stream(source)):
            if mapping.key == key_to_unset:
                removed = True
            else:
                dest.write(mapping.original.string)

    if not removed:
        logger.warning("Key %s not removed from %s - key doesn't exist.", key_to_unset, dotenv_path)
        return None, key_to_unset

    return removed, key_to_unset


def resolve_variables(
    values: ta.Iterable[tuple[str, str | None]],
    override: bool,
) -> dict[str, str | None]:
    new_values: dict[str, str | None] = {}

    for (name, value) in values:
        if value is None:
            result = None
        else:
            atoms = parse_variables(value)
            env: dict[str, str | None] = {}
            if override:
                env.update(os.environ)  # type: ignore
                env.update(new_values)
            else:
                env.update(new_values)
                env.update(os.environ)  # type: ignore
            result = ''.join(atom.resolve(env) for atom in atoms)

        new_values[name] = result

    return new_values


def dotenv_values(
    dotenv_path: StrPath | None = None,
    stream: ta.IO[str] | None = None,
    verbose: bool = False,
    interpolate: bool = True,
    encoding: str | None = 'utf-8',
) -> dict[str, str | None]:
    """
    Parse a .env file and return its content as a dict.

    The returned dict will have `None` values for keys without values in the .env file.
    For example, `foo=bar` results in `{"foo": "bar"}` whereas `foo` alone results in
    `{"foo": None}`

    Parameters:
        dotenv_path: Absolute or relative path to the .env file.
        stream: `StringIO` object with .env content, used if `dotenv_path` is `None`.
        verbose: Whether to output a warning if the .env file is missing.
        encoding: Encoding to be used to read the file.

    If both `dotenv_path` and `stream` are `None`, `find_dotenv()` is used to find the
    .env file.
    """
    if dotenv_path is None and stream is None:
        raise ValueError('must set dotenv_path or stream')

    return DotEnv(
        dotenv_path=dotenv_path,
        stream=stream,
        verbose=verbose,
        interpolate=interpolate,
        override=True,
        encoding=encoding,
    ).dict()
