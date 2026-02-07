# ruff: noqa: UP006 UP007 UP045
"""
Parses a complete HTTP/1.x start-line + header fields + final CRLF from a ``bytes`` object. Does NOT handle message
bodies, chunked transfer decoding, trailers, or HTTP/2+.

TODO:
 - mapping from error code to outbound http status code
"""
import dataclasses as dc
import datetime
import enum
import io
import re
import typing as ta

from .versions import HttpVersion
from .versions import HttpVersions


##


class StartLineHttpParseErrorCode(enum.Enum):
    MALFORMED_REQUEST_LINE = enum.auto()
    MALFORMED_STATUS_LINE = enum.auto()
    UNSUPPORTED_HTTP_VERSION = enum.auto()
    INVALID_METHOD = enum.auto()
    INVALID_REQUEST_TARGET = enum.auto()
    INVALID_STATUS_CODE = enum.auto()


class HeaderFieldHttpParseErrorCode(enum.Enum):
    INVALID_FIELD_NAME = enum.auto()
    INVALID_FIELD_VALUE = enum.auto()
    OBS_FOLD_NOT_ALLOWED = enum.auto()
    SPACE_BEFORE_COLON = enum.auto()
    MISSING_COLON = enum.auto()
    BARE_CARRIAGE_RETURN = enum.auto()
    BARE_LF = enum.auto()
    NUL_IN_HEADER = enum.auto()
    MISSING_TERMINATOR = enum.auto()
    TRAILING_DATA = enum.auto()
    TOO_MANY_HEADERS = enum.auto()
    EMPTY_FIELD_NAME = enum.auto()


class SemanticHeaderHttpParseErrorCode(enum.Enum):
    DUPLICATE_CONTENT_LENGTH = enum.auto()
    CONFLICTING_CONTENT_LENGTH = enum.auto()
    CONTENT_LENGTH_WITH_TRANSFER_ENCODING = enum.auto()
    MISSING_HOST_HEADER = enum.auto()
    MULTIPLE_HOST_HEADERS = enum.auto()
    CONFLICTING_HOST_HEADERS = enum.auto()
    INVALID_CONTENT_LENGTH = enum.auto()
    INVALID_TRANSFER_ENCODING = enum.auto()
    INVALID_CONTENT_TYPE = enum.auto()
    FORBIDDEN_TRAILER_FIELD = enum.auto()
    INVALID_HOST = enum.auto()
    INVALID_EXPECT = enum.auto()
    INVALID_DATE = enum.auto()
    INVALID_CACHE_CONTROL = enum.auto()
    INVALID_ACCEPT_ENCODING = enum.auto()
    INVALID_ACCEPT = enum.auto()
    INVALID_AUTHORIZATION = enum.auto()
    TE_WITHOUT_CHUNKED_LAST = enum.auto()
    TE_IN_HTTP10 = enum.auto()


class EncodingHttpParseErrorCode(enum.Enum):
    NON_ASCII_IN_FIELD_NAME = enum.auto()
    OBS_TEXT_IN_FIELD_VALUE = enum.auto()


HttpParseErrorCode = ta.Union[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    StartLineHttpParseErrorCode,
    HeaderFieldHttpParseErrorCode,
    SemanticHeaderHttpParseErrorCode,
    EncodingHttpParseErrorCode,
]


##


class HttpParseError(Exception):
    pass


@dc.dataclass()
class ErrorCodeHttpParseError(HttpParseError):
    """Base exception for all HTTP header parsing errors."""

    code: HttpParseErrorCode
    message: str = ''
    line: int = 0
    offset: int = 0

    def __post_init__(self) -> None:
        Exception.__init__(self, str(self))

    def __str__(self) -> str:
        return f'[{self.code.name}] line {self.line}, offset {self.offset}: {self.message}'


@dc.dataclass()
class StartLineHttpParseError(ErrorCodeHttpParseError):
    """Errors in the request-line or status-line."""

    code: StartLineHttpParseErrorCode = dc.field(default=StartLineHttpParseErrorCode.MALFORMED_REQUEST_LINE)


@dc.dataclass()
class HeaderFieldHttpParseError(ErrorCodeHttpParseError):
    """Errors in header field syntax."""

    code: HeaderFieldHttpParseErrorCode = dc.field(default=HeaderFieldHttpParseErrorCode.INVALID_FIELD_NAME)


@dc.dataclass()
class SemanticHeaderHttpParseError(ErrorCodeHttpParseError):
    """Errors in header field semantics / cross-field validation."""

    code: SemanticHeaderHttpParseErrorCode = dc.field(default=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH)


@dc.dataclass()
class EncodingHttpParseError(ErrorCodeHttpParseError):
    """Errors in character encoding within headers."""

    code: EncodingHttpParseErrorCode = dc.field(default=EncodingHttpParseErrorCode.NON_ASCII_IN_FIELD_NAME)


@dc.dataclass()
class NoCombineHeaderHttpParseError(HttpParseError):
    """Errors in headers where duplicate values are not allowed."""

    name: str


##


@ta.final
class ParsedHttpHeaders:
    """
    Normalized, case-insensitive header mapping.

    Field names are stored in lowercase. Values are decoded as Latin-1. Multiple values for the same field-name are
    stored individually and combined with ``", "`` on access (except Set-Cookie, which is never combined).
    """

    def __init__(self) -> None:
        # normalized name -> list of individual values
        self._entries: ta.Dict[str, ta.List[str]] = {}

        # insertion-ordered unique names
        self._order: ta.List[str] = []

    def _add(self, name: str, value: str) -> None:
        if name not in self._entries:
            self._entries[name] = []
            self._order.append(name)
        self._entries[name].append(value)

    def __contains__(self, name: ta.Any) -> bool:
        if not isinstance(name, str):
            return False
        return name.lower() in self._entries

    # Headers where duplicate values are comma-combined per RFC 7230 §3.2.2. # Set-Cookie is the notable exception.
    _NO_COMBINE_HEADERS: ta.ClassVar[ta.FrozenSet[str]] = frozenset({
        'set-cookie',
    })

    def __getitem__(self, name: str) -> str:
        key = name.lower()
        values = self._entries[key]
        if key in self._NO_COMBINE_HEADERS:
            raise NoCombineHeaderHttpParseError(name)
        return ', '.join(values)

    def get(self, name: str, default: ta.Optional[str] = None) -> ta.Optional[str]:
        try:
            return self[name]
        except KeyError:
            return default

    def get_all(self, name: str) -> ta.List[str]:
        return list(self._entries.get(name.lower(), []))

    def items(self) -> ta.List[ta.Tuple[str, str]]:
        result: ta.List[ta.Tuple[str, str]] = []
        for name in self._order:
            values = self._entries[name]
            if name in self._NO_COMBINE_HEADERS:
                for v in values:
                    result.append((name, v))
            else:
                result.append((name, ', '.join(values)))
        return result

    def keys(self) -> ta.List[str]:
        return list(self._order)

    def __iter__(self) -> ta.Iterator[str]:
        return iter(self._order)

    def __len__(self) -> int:
        return len(self._order)

    def __repr__(self) -> str:
        return f'ParsedHttpHeaders({dict(self.items())})'


@dc.dataclass()
class PreparedParsedHttpHeaders:
    content_length: ta.Optional[int] = None

    transfer_encoding: ta.Optional[ta.List[str]] = None

    host: ta.Optional[str] = None

    connection: ta.Optional[ta.FrozenSet[str]] = None
    keep_alive: ta.Optional[bool] = None

    @dc.dataclass(frozen=True)
    class ContentType:
        media_type: str
        params: ta.Dict[str, str]

        @property
        def charset(self) -> ta.Optional[str]:
            return self.params.get('charset')

    content_type: ta.Optional[ContentType] = None

    te: ta.Optional[ta.List[str]] = None

    upgrade: ta.Optional[ta.List[str]] = None

    trailer: ta.Optional[ta.FrozenSet[str]] = None

    expect: ta.Optional[str] = None
    expect_100_continue: ta.Optional[bool] = None

    date: ta.Optional[datetime.datetime] = None

    cache_control: ta.Optional[ta.Dict[str, ta.Optional[str]]] = None

    @dc.dataclass(frozen=True)
    class AcceptEncodingItem:
        coding: str
        q: float = 1.0

    accept_encoding: ta.Optional[ta.List[AcceptEncodingItem]] = None

    @dc.dataclass(frozen=True)
    class AcceptItem:
        media_range: str
        q: float = 1.0
        params: ta.Dict[str, str] = dc.field(default_factory=dict)

    accept: ta.Optional[ta.List[AcceptItem]] = None

    @dc.dataclass(frozen=True)
    class AuthorizationValue:
        scheme: str
        credentials: str

    authorization: ta.Optional[AuthorizationValue] = None


@dc.dataclass(frozen=True)
class RawParsedHttpHeader:
    name: bytes
    value: bytes


@dc.dataclass()
class ParsedHttpMessage:
    class Kind(enum.Enum):
        REQUEST = 'request'
        RESPONSE = 'response'

    kind: Kind

    @dc.dataclass(frozen=True)
    class RequestLine:
        method: str
        request_target: bytes
        http_version: HttpVersion

    request_line: ta.Optional[RequestLine]

    @dc.dataclass(frozen=True)
    class StatusLine:
        http_version: HttpVersion
        status_code: int
        reason_phrase: str

    status_line: ta.Optional[StatusLine]

    raw_headers: ta.List[RawParsedHttpHeader]
    headers: ParsedHttpHeaders

    prepared: PreparedParsedHttpHeaders


@dc.dataclass(frozen=True)
class ParsedHttpTrailers:
    """Result of parsing HTTP trailer fields."""

    raw_headers: ta.List[RawParsedHttpHeader]
    headers: ParsedHttpHeaders


##


class HttpParser:
    """Strict HTTP/1.x parser."""

    @dc.dataclass(frozen=True)
    class Config:
        """Strictness knobs. Defaults are maximally strict."""

        allow_obs_fold: bool = False
        allow_space_before_colon: bool = False  # DANGEROUS - upstreams may not handle well
        allow_multiple_content_lengths: bool = False
        allow_content_length_with_te: bool = False
        allow_bare_lf: bool = False
        allow_missing_host: bool = False
        allow_multiple_hosts: bool = False
        allow_unknown_transfer_encoding: bool = False
        allow_empty_header_values: bool = True
        allow_bare_cr_in_value: bool = False
        allow_te_without_chunked_in_response: bool = False
        allow_transfer_encoding_http10: bool = False
        reject_multi_value_content_length: bool = False
        reject_obs_text: bool = False
        reject_non_visible_ascii_request_target: bool = False
        max_header_count: int = 128
        max_header_length: ta.Optional[int] = 8192
        max_content_length_str_len: ta.Optional[int] = None

    def __init__(self, config: Config = Config()) -> None:
        super().__init__()

        self._config = config

    # Public API

    class Mode(enum.Enum):
        REQUEST = 'request'
        RESPONSE = 'response'
        AUTO = 'auto'

    def parse_message(self, data: bytes, mode: Mode = Mode.AUTO) -> ParsedHttpMessage:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f'Expected bytes, got {type(data).__name__}')

        ctx = _HttpParseContext(
            data=bytes(data),
            config=self._config,
            mode=mode,
        )

        # 1. Verify terminator
        ctx.verify_terminator()

        # 2. Split off start-line
        start_line_end = ctx.find_line_end(0)
        start_line_bytes = data[:start_line_end]

        # 3. Determine message kind
        kind = ctx.detect_kind(start_line_bytes)

        # 4. Parse start-line
        request_line: ta.Optional[ParsedHttpMessage.RequestLine] = None
        status_line: ta.Optional[ParsedHttpMessage.StatusLine] = None
        if kind == ParsedHttpMessage.Kind.REQUEST:
            request_line = ctx.parse_request_line(start_line_bytes)
        else:
            status_line = ctx.parse_status_line(start_line_bytes)

        http_version = (
            request_line.http_version if request_line else
            status_line.http_version if status_line else
            HttpVersions.HTTP_1_1
        )

        # 5. Parse header fields
        # Position after start-line CRLF (or LF if bare LF allowed)
        header_start = start_line_end + ctx.line_ending_len(start_line_end)
        raw_headers = ctx.parse_header_fields(header_start)

        # 6. Build normalized headers
        headers = ParsedHttpHeaders()
        for rh in raw_headers:
            name_str = rh.name.decode('ascii').lower()
            value_str = rh.value.decode('latin-1')
            headers._add(name_str, value_str)  # noqa

        # 7. Build prepared headers
        prepared = ctx.prepare_headers(headers, kind, http_version)

        return ParsedHttpMessage(
            kind=kind,
            request_line=request_line,
            status_line=status_line,
            raw_headers=raw_headers,
            headers=headers,
            prepared=prepared,
        )

    def parse_trailers(
        self,
        data: bytes,
    ) -> ParsedHttpTrailers:
        """
        Parse HTTP/1.x trailer fields from *data*.

        *data* must contain the complete trailer section ending with ``\\r\\n\\r\\n`` (an empty line). No start-line is
        expected.

        Fields listed in :data:`_FORBIDDEN_TRAILER_FIELDS` (per RFC 7230 §4.1.2) are rejected.

        :param data: Complete trailer section ending with ``\\r\\n\\r\\n``.
        :param config: Parsing strictness configuration (same knobs as header parsing).
        :returns: A :class:`ParsedTrailers` with raw and normalized headers.
        :raises HttpParseError: On any parsing violation.
        """

        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f'Expected bytes, got {type(data).__name__}')

        # Special case: empty trailers (just the terminating empty line, no fields)
        if data == b'\r\n' or (self._config.allow_bare_lf and data == b'\n'):
            return ParsedHttpTrailers(
                raw_headers=[],
                headers=ParsedHttpHeaders(),
            )

        ctx = _HttpParseContext(
            data=bytes(data),
            config=self._config,
            mode=HttpParser.Mode.AUTO,
        )

        # Verify terminator (trailers end with an empty CRLF line, same as headers)
        ctx.verify_terminator()

        # Parse fields starting at position 0 (no start-line)
        raw_headers = ctx.parse_header_fields(0)

        # Build normalized headers
        headers = ParsedHttpHeaders()
        for rh in raw_headers:
            name_str = rh.name.decode('ascii').lower()
            value_str = rh.value.decode('latin-1')
            headers._add(name_str, value_str)  # noqa

        # Enforce forbidden trailer fields (RFC 7230 §4.1.2)
        for name in headers:
            if name in _HttpParseContext._FORBIDDEN_TRAILER_FIELDS:  # noqa
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.FORBIDDEN_TRAILER_FIELD,
                    message=f'Forbidden field in trailers: {name!r}',
                )

        return ParsedHttpTrailers(
            raw_headers=raw_headers,
            headers=headers,
        )


class _HttpParseContext:
    def __init__(
            self,
            data: bytes,
            config: HttpParser.Config,
            mode: HttpParser.Mode,
    ) -> None:
        super().__init__()

        self.data = data
        self.config = config
        self.mode = mode
        self.current_line = 0  # 0-indexed logical line number

    # Character constants

    # RFC 7230 §3.2.6: token = 1*tchar
    # tchar = "!" / "#" / "$" / "%" / "&" / "'" / "*" / "+" / "-" / "." / "^" / "_" / "`" / "|" / "~" / DIGIT / ALPHA
    _TCHAR_EXTRAS: ta.ClassVar[ta.FrozenSet[int]] = frozenset(b"!#$%&'*+-.^_`|~")

    _TCHAR: ta.ClassVar[ta.FrozenSet[int]] = frozenset(
        set(range(0x30, 0x3A)) |  # DIGIT 0-9
        set(range(0x41, 0x5B)) |  # ALPHA A-Z
        set(range(0x61, 0x7B)) |  # ALPHA a-z
        _TCHAR_EXTRAS,
    )

    # VCHAR = %x21-7E
    _VCHAR: ta.ClassVar[ta.FrozenSet[int]] = frozenset(range(0x21, 0x7F))

    # obs-text = %x80-FF
    _OBS_TEXT: ta.ClassVar[ta.FrozenSet[int]] = frozenset(range(0x80, 0x100))

    _SP = 0x20
    _HTAB = 0x09
    _CR = 0x0D
    _LF = 0x0A
    _COLON = 0x3A
    _NUL = 0x00

    # OWS = *( SP / HTAB )
    _OWS_CHARS: ta.ClassVar[ta.FrozenSet[int]] = frozenset({_SP, _HTAB})

    _CRLF = b'\r\n'
    _CRLFCRLF = b'\r\n\r\n'

    # Allowed characters as raw bytes for translate()
    _TCHAR_BYTES = bytes(sorted(_TCHAR))
    _VCHAR_BYTES = bytes(range(0x21, 0x7F))

    # Terminator verification

    def verify_terminator(self) -> None:
        data = self.data

        idx = data.find(self._CRLFCRLF)
        if idx >= 0:
            after = idx + 4
            if after < len(data):
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.TRAILING_DATA,
                    message=f'Unexpected {len(data) - after} byte(s) after header terminator',
                    line=0,
                    offset=after,
                )
            return

        # Bare-LF mode: require the header block to END with LF LF, not just contain it.
        if self.config.allow_bare_lf:
            if data.endswith(b'\n\n'):
                return
            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.MISSING_TERMINATOR,
                message='Header block does not end with LFLF',
                line=0,
                offset=len(data),
            )

        raise HeaderFieldHttpParseError(
            code=HeaderFieldHttpParseErrorCode.MISSING_TERMINATOR,
            message='Header block does not end with CRLFCRLF',
            line=0,
            offset=len(data),
        )

    # Line utilities

    def find_line_end(self, start: int) -> int:
        """
        Find the end of the current line (position of CR before CRLF, or LF if bare-LF allowed). Returns the index of
        the first byte of the line-ending sequence.

        Uses bytes.find() for NUL/CR/LF rather than iterating byte-by-byte in Python. Only loops when a bare CR must be
        skipped (allow_bare_cr_in_value mode).
        """

        data = self.data
        length = len(data)
        pos = start

        while True:
            # Let C-level .find() locate the first occurrence of each interesting byte.
            nul_at = data.find(b'\x00', pos)
            cr_at = data.find(b'\r', pos)
            lf_at = data.find(b'\n', pos)

            # Replace "not found" (-1) with length so min() picks the real hits.
            if nul_at < 0:
                nul_at = length
            if cr_at < 0:
                cr_at = length
            if lf_at < 0:
                lf_at = length

            first = min(nul_at, cr_at, lf_at)

            if first == length:
                # None of the three bytes found before end of data.
                break

            # NUL: always an error
            if first == nul_at and nul_at <= cr_at and nul_at <= lf_at:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.NUL_IN_HEADER,
                    message='NUL byte in header data',
                    line=self.current_line,
                    offset=nul_at,
                )

            # CR: check for CRLF vs bare CR
            if first == cr_at and cr_at <= lf_at:
                if cr_at + 1 < length and data[cr_at + 1] == self._LF:
                    return cr_at  # CRLF - this is the line ending

                # Bare CR (not followed by LF)
                if not self.config.allow_bare_cr_in_value:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.BARE_CARRIAGE_RETURN,
                        message='Bare CR not followed by LF',
                        line=self.current_line,
                        offset=cr_at,
                    )

                # Bare CR is allowed in values - skip past it and search again.
                pos = cr_at + 1
                continue

            # LF: bare LF (if it were preceded by CR we'd have returned above)
            if self.config.allow_bare_lf:
                return lf_at

            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.BARE_LF,
                message='Bare LF without preceding CR',
                line=self.current_line,
                offset=lf_at,
            )

        raise HeaderFieldHttpParseError(
            code=HeaderFieldHttpParseErrorCode.MISSING_TERMINATOR,
            message='Unexpected end of data while scanning for line ending',
            line=self.current_line,
            offset=length,
        )

    def line_ending_len(self, line_end_pos: int) -> int:
        """Return the length of the line ending at *line_end_pos* (1 for LF, 2 for CRLF)."""

        if line_end_pos < len(self.data) and self.data[line_end_pos] == self._LF:
            return 1  # bare LF
        return 2  # CRLF

    # Kind detection

    def detect_kind(self, start_line: bytes) -> ParsedHttpMessage.Kind:
        if self.mode == HttpParser.Mode.REQUEST:
            return ParsedHttpMessage.Kind.REQUEST

        if self.mode == HttpParser.Mode.RESPONSE:
            return ParsedHttpMessage.Kind.RESPONSE

        # AUTO: responses start with "HTTP/"
        if start_line.startswith(b'HTTP/'):
            return ParsedHttpMessage.Kind.RESPONSE

        return ParsedHttpMessage.Kind.REQUEST

    # Start-line parsing

    _REQUEST_TARGET_BYTES: ta.ClassVar[bytes] = bytes(set(_VCHAR_BYTES) | set(range(0x80, 0x100)))

    def parse_request_line(self, line: bytes) -> ParsedHttpMessage.RequestLine:
        """Parse ``method SP request-target SP HTTP-version``."""

        # Must have exactly two SP separators

        first_sp = line.find(b' ')
        if first_sp < 0:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_REQUEST_LINE,
                message='No SP found in request-line',
                line=0,
                offset=0,
            )

        last_sp = line.rfind(b' ')
        if first_sp == last_sp:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_REQUEST_LINE,
                message='Only one SP found in request-line; expected method SP target SP version',
                line=0,
                offset=first_sp,
            )

        method_bytes = line[:first_sp]
        target_bytes = line[first_sp + 1:last_sp]
        version_bytes = line[last_sp + 1:]

        # Validate no extra SP in components: check that second SP search from first_sp+1 matches last_sp - i.e., the
        # target does not contain the last SP. Actually the HTTP spec says request-target can contain spaces? No - it's
        # defined as *visible ASCII*. But to find the correct split: method is a token (no SP), version is fixed format
        # (no SP), and everything in between is the target which is VCHAR (no SP). However, some real URIs... no, VCHAR
        # excludes SP. Let's be strict: Check there are exactly 2 SPs total.
        if line.count(b' ') != 2:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_REQUEST_LINE,
                message=f'Request-line contains {line.count(b" ")} spaces; expected exactly 2',
                line=0,
                offset=0,
            )

        # Validate method

        if not method_bytes:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_METHOD,
                message='Empty method in request-line',
                line=0,
                offset=0,
            )

        if method_bytes.translate(None, self._TCHAR_BYTES):
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_METHOD,
                message=f'Method contains invalid character(s)',
                line=0,
                offset=0,
            )

        # Validate request-target (VCHAR only, non-empty)

        if not target_bytes:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_REQUEST_TARGET,
                message='Empty request-target',
                line=0,
                offset=first_sp + 1,
            )

        if self.config.reject_non_visible_ascii_request_target:
            if target_bytes.translate(None, self._VCHAR_BYTES):
                raise StartLineHttpParseError(
                    code=StartLineHttpParseErrorCode.INVALID_REQUEST_TARGET,
                    message='Request-target contains non-visible-ASCII character(s)',
                    line=0,
                    offset=first_sp + 1,
                )

        else:
            if target_bytes.translate(None, self._REQUEST_TARGET_BYTES):
                raise StartLineHttpParseError(
                    code=StartLineHttpParseErrorCode.INVALID_REQUEST_TARGET,
                    message='Request-target contains invalid character(s)',
                    line=0,
                    offset=first_sp + 1,
                )

        # Validate HTTP version

        version_str = version_bytes.decode('ascii', errors='replace')
        if version_str == 'HTTP/1.0':
            version = HttpVersions.HTTP_1_0
        elif version_str == 'HTTP/1.1':
            version = HttpVersions.HTTP_1_1
        else:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.UNSUPPORTED_HTTP_VERSION,
                message=f'Unsupported HTTP version: {version_str!r}',
                line=0,
                offset=last_sp + 1,
            )

        return ParsedHttpMessage.RequestLine(
            method=method_bytes.decode('ascii'),
            request_target=target_bytes,
            http_version=version,
        )

    # reason-phrase: 0+ bytes of HTAB / SP / VCHAR / obs-text
    _RE_REASON_PHRASE: ta.ClassVar[re.Pattern] = re.compile(rb'^[\x09\x20\x21-\x7e\x80-\xff]*\Z')

    # reason-phrase = *( HTAB / SP / VCHAR / obs-text )
    _REASON_PHRASE_CHARS: ta.ClassVar[ta.FrozenSet[int]] = frozenset(
        {_HTAB, _SP} |
        set(_VCHAR) |
        set(_OBS_TEXT),
    )

    def parse_status_line(self, line: bytes) -> ParsedHttpMessage.StatusLine:
        """Parse ``HTTP-version SP status-code SP reason-phrase``."""

        # First SP separates version from status code

        first_sp = line.find(b' ')
        if first_sp < 0:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_STATUS_LINE,
                message='No SP found in status-line',
                line=0,
                offset=0,
            )

        version_bytes = line[:first_sp]
        rest = line[first_sp + 1:]

        # Second SP separates status code from reason phrase

        second_sp = rest.find(b' ')
        if second_sp < 0:
            # Per RFC 7230:
            #   `status-line = HTTP-version SP status-code SP reason-phrase`.
            # The SP before reason-phrase is required even if reason-phrase is empty.
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_STATUS_LINE,
                message='Missing second SP in status-line (required before reason-phrase)',
                line=0,
                offset=first_sp + 1 + len(rest),
            )

        status_bytes = rest[:second_sp]
        reason_bytes = rest[second_sp + 1:]

        # Validate HTTP version

        version_str = version_bytes.decode('ascii', errors='replace')
        if version_str == 'HTTP/1.0':
            version = HttpVersions.HTTP_1_0
        elif version_str == 'HTTP/1.1':
            version = HttpVersions.HTTP_1_1
        else:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.UNSUPPORTED_HTTP_VERSION,
                message=f'Unsupported HTTP version: {version_str!r}',
                line=0,
                offset=0,
            )

        # Validate status code: exactly 3 ASCII digits

        if len(status_bytes) != 3 or not status_bytes.isdigit():
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_STATUS_CODE,
                message=f'Status code is not exactly 3 digits: {status_bytes!r}',
                line=0,
                offset=first_sp + 1,
            )

        status_code = int(status_bytes)
        if not (100 <= status_code <= 599):
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_STATUS_CODE,
                message=f'Status code {status_code} out of range 100-599',
                line=0,
                offset=first_sp + 1,
            )

        # Validate reason-phrase characters

        if not self._RE_REASON_PHRASE.match(reason_bytes):
            # Regex rejected - scan to find the specific bad byte for error reporting
            reason_base_offset = first_sp + 1 + second_sp + 1

            for i, b in enumerate(reason_bytes):
                if b == self._NUL:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.NUL_IN_HEADER,
                        message='NUL byte in reason-phrase',
                        line=0,
                        offset=reason_base_offset + i,
                    )

                if b not in self._REASON_PHRASE_CHARS:
                    raise StartLineHttpParseError(
                        code=StartLineHttpParseErrorCode.MALFORMED_STATUS_LINE,
                        message=f'Invalid character 0x{b:02x} in reason-phrase',
                        line=0,
                        offset=reason_base_offset + i,
                    )

        return ParsedHttpMessage.StatusLine(
            http_version=version,
            status_code=status_code,
            reason_phrase=reason_bytes.decode('latin-1'),
        )

    # Header field parsing

    def parse_header_fields(self, start: int) -> ta.List[RawParsedHttpHeader]:
        """Parse all header fields from *start* until the empty-line terminator."""

        headers: ta.List[RawParsedHttpHeader] = []
        pos = start
        data = self.data
        self.current_line = 1  # line 0 is the start-line

        while pos < len(data):
            # Check for the empty line that terminates headers
            if data[pos] == self._CR and pos + 1 < len(data) and data[pos + 1] == self._LF:
                # Could be the terminator (\r\n at start of a "line" = empty line)
                break

            if self.config.allow_bare_lf and data[pos] == self._LF:
                break

            # Max header count check
            if len(headers) >= self.config.max_header_count:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.TOO_MANY_HEADERS,
                    message=f'Exceeded maximum header count of {self.config.max_header_count}',
                    line=self.current_line,
                    offset=pos,
                )

            # Find end of this header line
            line_end = self.find_line_end(pos)
            line_data = data[pos:line_end]
            next_pos = line_end + self.line_ending_len(line_end)

            if self.config.max_header_length is not None and len(line_data) > self.config.max_header_length:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_VALUE,
                    message='Header line exceeds maximum length',
                    line=self.current_line,
                    offset=next_pos,
                )

            # Handle obs-fold: if the *next* line starts with SP or HTAB, it's a continuation
            obs_buf: ta.Optional[io.BytesIO] = None

            while next_pos < len(data):
                next_byte = data[next_pos]

                if next_byte in self._OWS_CHARS:
                    if not self.config.allow_obs_fold:
                        raise HeaderFieldHttpParseError(
                            code=HeaderFieldHttpParseErrorCode.OBS_FOLD_NOT_ALLOWED,
                            message='Obsolete line folding (obs-fold) encountered but not allowed',
                            line=self.current_line,
                            offset=next_pos,
                        )

                    # Unfold: find the end of the continuation line
                    cont_line_end = self.find_line_end(next_pos)
                    cont_data = data[next_pos:cont_line_end]

                    # Replace fold with single SP
                    if obs_buf is None:
                        obs_buf = io.BytesIO()
                        obs_buf.write(line_data)
                    obs_buf.write(b' ')
                    obs_buf.write(cont_data.lstrip(b' \t'))

                    next_pos = cont_line_end + self.line_ending_len(cont_line_end)

                    if self.config.max_header_length is not None and obs_buf.tell() > self.config.max_header_length:
                        raise HeaderFieldHttpParseError(
                            code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_VALUE,
                            message='Unfolded header line exceeds maximum length',
                            line=self.current_line,
                            offset=next_pos,
                        )

                else:
                    break

            if obs_buf is not None:
                line_data = obs_buf.getvalue()

            # Parse field-name : field-value
            header = self._parse_one_header(line_data, pos)
            headers.append(header)

            pos = next_pos
            self.current_line += 1

        return headers

    @classmethod
    def _strip_ows(cls, data: bytes) -> bytes:
        """Strip leading and trailing optional whitespace (SP / HTAB)."""

        return data.strip(b' \t')

    # token: 1+ tchar bytes
    _RE_TOKEN: ta.ClassVar[re.Pattern] = re.compile(rb"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+\Z")

    # Pre-calculate the 4 field-value variants for the translation filter (allow_bare_cr, reject_obs_text)
    _FIELD_VALUE_ALLOWED: ta.ClassVar[ta.Mapping[ta.Tuple[bool, bool], bytes]] = {
        (False, False): bytes({_HTAB, _SP}      | set(range(0x21, 0x7F))   | set(range(0x80, 0x100))),  # noqa
        (False, True):  bytes({_HTAB, _SP}      | set(range(0x21, 0x7F))),  # noqa
        (True, False):  bytes({_HTAB, _CR, _SP} | set(range(0x21, 0x7F))   | set(range(0x80, 0x100))),  # noqa
        (True, True):   bytes({_HTAB, _CR, _SP} | set(range(0x21, 0x7F))),  # noqa
    }

    def _parse_one_header(self, line_data: bytes, line_start_offset: int) -> RawParsedHttpHeader:
        """Parse a single ``field-name: field-value`` line (already unfolded)."""

        colon_idx = line_data.find(b':')
        if colon_idx < 0:
            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.MISSING_COLON,
                message='Header line has no colon separator',
                line=self.current_line,
                offset=line_start_offset,
            )

        name_bytes = line_data[:colon_idx]
        value_bytes = line_data[colon_idx + 1:]

        # Validate field-name

        if not name_bytes:
            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.EMPTY_FIELD_NAME,
                message='Empty field-name before colon',
                line=self.current_line,
                offset=line_start_offset,
            )

        # Check for space before colon
        if name_bytes[-1] in self._OWS_CHARS:
            if not self.config.allow_space_before_colon:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.SPACE_BEFORE_COLON,
                    message='Whitespace between field-name and colon',
                    line=self.current_line,
                    offset=line_start_offset + len(name_bytes) - 1,
                )

            # Strip trailing whitespace from name if allowed
            name_bytes = name_bytes.rstrip(b' \t')
            if not name_bytes:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.EMPTY_FIELD_NAME,
                    message='Field-name is only whitespace before colon',
                    line=self.current_line,
                    offset=line_start_offset,
                )

        # Validate name characters (regex fast-path; fallback scan on failure)
        if not self._RE_TOKEN.match(name_bytes):
            for i, b in enumerate(name_bytes):
                if b == self._NUL:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.NUL_IN_HEADER,
                        message='NUL byte in field-name',
                        line=self.current_line,
                        offset=line_start_offset + i,
                    )

                if b >= 0x80:
                    raise EncodingHttpParseError(
                        code=EncodingHttpParseErrorCode.NON_ASCII_IN_FIELD_NAME,
                        message=f'Non-ASCII byte 0x{b:02x} in field-name',
                        line=self.current_line,
                        offset=line_start_offset + i,
                    )

                if b not in self._TCHAR:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_NAME,
                        message=f'Invalid character 0x{b:02x} in field-name',
                        line=self.current_line,
                        offset=line_start_offset + i,
                    )

        # Process field-value

        # Strip OWS
        value_stripped = self._strip_ows(value_bytes)

        # Check for empty value
        if not value_stripped and not self.config.allow_empty_header_values:
            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_VALUE,
                message='Empty header field value not allowed',
                line=self.current_line,
                offset=line_start_offset + colon_idx + 1,
            )

        # Validate value characters (Translation fast-path)
        allowed_bytes = self._FIELD_VALUE_ALLOWED[(
            self.config.allow_bare_cr_in_value,
            self.config.reject_obs_text,
        )]

        # This is the "Pedantic" C-speed check. translate(None, allowed_bytes) removes all valid characters. If any
        # bytes remain, the input is invalid.
        invalid_chars = value_stripped.translate(None, allowed_bytes)

        if invalid_chars:
            value_base_offset = line_start_offset + colon_idx + 1
            # We only enter this Python loop if we ALREADY found an error.
            # This keeps the "happy path" fast while maintaining detailed error reporting.
            for i, b in enumerate(value_stripped):
                if b == self._NUL:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.NUL_IN_HEADER,
                        message='NUL byte in field-value',
                        line=self.current_line,
                        offset=value_base_offset + i,
                    )

                if b == self._CR:
                    if not self.config.allow_bare_cr_in_value:
                        raise HeaderFieldHttpParseError(
                            code=HeaderFieldHttpParseErrorCode.BARE_CARRIAGE_RETURN,
                            message='Bare CR in field-value',
                            line=self.current_line,
                            offset=value_base_offset + i,
                        )
                    continue

                if b not in allowed_bytes:
                    # Specific error logic for obs-text/bare CR
                    if b >= 0x80 and self.config.reject_obs_text:
                        raise EncodingHttpParseError(
                            code=EncodingHttpParseErrorCode.OBS_TEXT_IN_FIELD_VALUE,
                            message=f'obs-text byte 0x{b:02x} rejected by config',
                            line=self.current_line,
                            offset=value_base_offset + i,
                        )

                    # General character error
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_VALUE,
                        message=f'Invalid character 0x{b:02x} in field-value',
                        line=self.current_line,
                        offset=value_base_offset + i,
                    )

        return RawParsedHttpHeader(
            name=name_bytes,
            value=value_stripped,
        )

    # Prepared header construction

    def prepare_headers(
        self,
        headers: ParsedHttpHeaders,
        kind: ParsedHttpMessage.Kind,
        http_version: HttpVersion,
    ) -> PreparedParsedHttpHeaders:
        prepared = PreparedParsedHttpHeaders()

        self._prepare_content_length(headers, prepared)
        self._prepare_transfer_encoding(headers, prepared, kind, http_version)
        self._prepare_host(headers, prepared, kind, http_version)
        self._prepare_connection(headers, prepared, http_version)
        self._prepare_content_type(headers, prepared)
        self._prepare_te(headers, prepared)
        self._prepare_upgrade(headers, prepared)
        self._prepare_trailer(headers, prepared)
        self._prepare_expect(headers, prepared)
        self._prepare_date(headers, prepared)
        self._prepare_cache_control(headers, prepared)
        self._prepare_accept_encoding(headers, prepared)
        self._prepare_accept(headers, prepared)
        self._prepare_authorization(headers, prepared)

        # Cross-field: Content-Length + Transfer-Encoding conflict
        if (
            prepared.content_length is not None and
            prepared.transfer_encoding is not None and
            not self.config.allow_content_length_with_te
        ):
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.CONTENT_LENGTH_WITH_TRANSFER_ENCODING,
                message='Content-Length and Transfer-Encoding are both present',
            )

        return prepared

    def _prepare_content_length(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        values = headers.get_all('content-length')
        if not values:
            return

        parsed_values: ta.List[int] = []
        for v in values:
            # A single Content-Length header might itself be a comma-separated list (some implementations do this). We
            # parse each element.
            if self.config.reject_multi_value_content_length and ',' in v:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                    message=f'Content-Length with multiple values is forbidden: {v!r}',
                )

            for part in v.split(','):
                stripped = part.strip()

                if not stripped.isdigit():
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                        message=f'Content-Length value is not a valid non-negative integer: {stripped!r}',
                    )

                if (
                        self.config.max_content_length_str_len is not None and
                        len(stripped) > self.config.max_content_length_str_len
                ):
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                        message=f'Content-Length value string too long: {stripped!r}',
                    )

                parsed_values.append(int(stripped))

        if not parsed_values:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                message='Content-Length header present but empty',
            )

        unique = set(parsed_values)
        if len(unique) > 1:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.CONFLICTING_CONTENT_LENGTH,
                message=f'Conflicting Content-Length values: {sorted(unique)}',
            )

        if len(parsed_values) > 1:
            if not self.config.allow_multiple_content_lengths:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.DUPLICATE_CONTENT_LENGTH,
                    message=(
                        f'Multiple Content-Length values (all {parsed_values[0]}); '
                        f'set allow_multiple_content_lengths to accept'
                    ),
                )

        val = parsed_values[0]
        if val < 0:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                message=f'Content-Length is negative: {val}',
            )

        prepared.content_length = val

    _KNOWN_CODINGS: ta.ClassVar[ta.FrozenSet[str]] = frozenset([
        'chunked',
        'compress',
        'deflate',
        'gzip',
        'x-gzip',
        'x-compress',
    ])

    def _prepare_transfer_encoding(
        self,
        headers: ParsedHttpHeaders,
        prepared: PreparedParsedHttpHeaders,
        kind: ParsedHttpMessage.Kind,
        http_version: HttpVersion,
    ) -> None:
        if 'transfer-encoding' not in headers:
            return

        combined = headers['transfer-encoding']
        codings = [c.strip().lower() for c in combined.split(',') if c.strip()]

        if not codings:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_TRANSFER_ENCODING,
                message='Transfer-Encoding header present but empty',
            )

        # HTTP/1.0 check
        if http_version == HttpVersions.HTTP_1_0 and not self.config.allow_transfer_encoding_http10:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.TE_IN_HTTP10,
                message='Transfer-Encoding is not defined for HTTP/1.0',
            )

        # Validate known codings
        if not self.config.allow_unknown_transfer_encoding:
            for c in codings:
                if c not in self._KNOWN_CODINGS:
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.INVALID_TRANSFER_ENCODING,
                        message=f'Unknown transfer-coding: {c!r}',
                    )

        # chunked positioning
        if 'chunked' in codings:
            if codings[-1] != 'chunked':
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.TE_WITHOUT_CHUNKED_LAST,
                    message='chunked must be the last (outermost) transfer-coding',
                )

            if codings.count('chunked') > 1:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_TRANSFER_ENCODING,
                    message='chunked appears more than once in Transfer-Encoding',
                )

        else:
            # No chunked present
            if kind == ParsedHttpMessage.Kind.REQUEST:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.TE_WITHOUT_CHUNKED_LAST,
                    message='Transfer-Encoding in a request must include chunked as the last coding',
                )

            elif kind == ParsedHttpMessage.Kind.RESPONSE:
                if not self.config.allow_te_without_chunked_in_response:
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.TE_WITHOUT_CHUNKED_LAST,
                        message=(
                            'Transfer-Encoding in a response without chunked; '
                            'set allow_te_without_chunked_in_response to accept'
                        ),
                    )

        prepared.transfer_encoding = codings

    # Host header: reject control chars 0x00-0x1F and SP 0x20. # Operates on str (already latin-1 decoded).
    _RE_HOST_VALID: ta.ClassVar[re.Pattern] = re.compile(r'^[^\x00-\x20]*\Z')

    def _prepare_host(
        self,
        headers: ParsedHttpHeaders,
        prepared: PreparedParsedHttpHeaders,
        kind: ParsedHttpMessage.Kind,
        http_version: HttpVersion,
    ) -> None:
        values = headers.get_all('host')

        if kind == ParsedHttpMessage.Kind.REQUEST and http_version == HttpVersions.HTTP_1_1:
            if not values and not self.config.allow_missing_host:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.MISSING_HOST_HEADER,
                    message='Host header is required in HTTP/1.1 requests',
                )

        if len(values) > 1:
            if not self.config.allow_multiple_hosts:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.MULTIPLE_HOST_HEADERS,
                    message=f'Multiple Host headers found ({len(values)})',
                )

            # If allowed, all values must be identical
            unique = set(values)
            if len(unique) > 1:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.CONFLICTING_HOST_HEADERS,
                    message=f'Multiple Host headers with different values: {sorted(unique)}',
                )

        if values:
            host_val = values[0].strip()

            # Minimal validation: reject any whitespace/control chars. Host is an authority, and
            # allowing OWS creates parsing inconsistencies across components.
            if not host_val and kind == ParsedHttpMessage.Kind.REQUEST:
                # Empty Host is technically allowed for certain request-targets (authority form, etc.), but let's just
                # accept it - the URI layer handles that.
                pass

            # Reject any SP / HTAB anywhere.
            if ' ' in host_val or '\t' in host_val:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_HOST,
                    message='Whitespace not allowed in Host header',
                )

            # Reject other C0 controls (including NUL) if present (defense in depth). (Host is a str decoded as Latin-1
            # in your ParsedHttpHeaders container.)
            if not self._RE_HOST_VALID.match(host_val):
                for i, ch in enumerate(host_val):
                    if ord(ch) < 0x21:  # includes 0x00-0x20; we've already rejected SP/HTAB explicitly
                        raise SemanticHeaderHttpParseError(
                            code=SemanticHeaderHttpParseErrorCode.INVALID_HOST,
                            message=f'Invalid character in Host header at position {i}',
                        )

            prepared.host = host_val

    @classmethod
    def _parse_comma_list(cls, value: str) -> ta.List[str]:
        """Split a comma-separated header value into trimmed, non-empty tokens."""

        parts: ta.List[str] = []
        for part in value.split(','):
            stripped = part.strip()
            if stripped:
                parts.append(stripped)
        return parts

    def _prepare_connection(
        self,
        headers: ParsedHttpHeaders,
        prepared: PreparedParsedHttpHeaders,
        http_version: HttpVersion,
    ) -> None:
        if 'connection' in headers:
            tokens = {t.lower() for t in self._parse_comma_list(headers['connection'])}
            prepared.connection = frozenset(tokens)
        else:
            prepared.connection = frozenset()

        # Derive keep_alive
        if 'close' in prepared.connection:
            prepared.keep_alive = False
        elif 'keep-alive' in prepared.connection:
            prepared.keep_alive = True
        else:
            # Default: HTTP/1.1 = keep-alive, HTTP/1.0 = close
            prepared.keep_alive = (http_version == HttpVersions.HTTP_1_1)

    @classmethod
    def _parse_quoted_string(cls, data: str, pos: int) -> ta.Tuple[str, int]:
        """
        Parse a quoted-string starting at *pos* (which must point at the opening DQUOTE). Returns (unescaped_value,
        position_after_closing_DQUOTE).
        """

        if pos >= len(data) or data[pos] != '"':
            raise ValueError('Expected opening double-quote')

        pos += 1  # skip opening "

        result: ta.List[str] = []
        while pos < len(data):
            ch = data[pos]

            if ch == '"':
                return ''.join(result), pos + 1

            if ch == '\\':
                pos += 1
                if pos >= len(data):
                    raise ValueError('Backslash at end of quoted-string')
                result.append(data[pos])
                pos += 1

            else:
                result.append(ch)
                pos += 1

        raise ValueError('Unterminated quoted-string')

    @classmethod
    def _parse_media_type_params(cls, params_str: str) -> ta.Dict[str, str]:
        """
        Parse ``;param=value`` segments from a Content-Type or Accept header. Values may be tokens or quoted-strings.
        """

        params: ta.Dict[str, str] = {}

        remaining = params_str.strip()
        while remaining:
            if not remaining.startswith(';'):
                break

            remaining = remaining[1:].strip()
            if not remaining:
                break

            eq_idx = remaining.find('=')
            if eq_idx < 0:
                # parameter name without value - skip to next semicolon or end
                semi_idx = remaining.find(';')
                if semi_idx < 0:
                    break

                remaining = remaining[semi_idx:]
                continue

            pname = remaining[:eq_idx].strip().lower()
            remaining = remaining[eq_idx + 1:].strip()

            if remaining.startswith('"'):
                try:
                    pvalue, end_pos = cls._parse_quoted_string(remaining, 0)
                except ValueError:
                    break
                remaining = remaining[end_pos:].strip()

            else:
                semi_idx = remaining.find(';')

                if semi_idx < 0:
                    pvalue = remaining.strip()
                    remaining = ''
                else:
                    pvalue = remaining[:semi_idx].strip()
                    remaining = remaining[semi_idx:]

            if pname:
                params[pname] = pvalue

        return params

    def _prepare_content_type(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'content-type' not in headers:
            return

        raw = headers['content-type']

        # media-type = type "/" subtype *( OWS ";" OWS parameter )
        semi_idx = raw.find(';')
        if semi_idx < 0:
            media_type = raw.strip().lower()
            params: ta.Dict[str, str] = {}
        else:
            media_type = raw[:semi_idx].strip().lower()
            params = self._parse_media_type_params(raw[semi_idx:])

        if '/' not in media_type:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_TYPE,
                message=f'Content-Type missing "/" in media-type: {media_type!r}',
            )

        parts = media_type.split('/', 1)
        if not parts[0] or not parts[1]:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_TYPE,
                message=f'Content-Type has empty type or subtype: {media_type!r}',
            )

        prepared.content_type = PreparedParsedHttpHeaders.ContentType(
            media_type=media_type,
            params=params,
        )

    @classmethod
    def _split_header_element(cls, element: str) -> ta.Tuple[str, float, ta.Dict[str, str]]:
        """
        Split a single header list element like ``"token;q=0.5;param=val"`` into ``(token_lower, q, params_dict)``.

        *token* is lowercased.  ``q`` defaults to ``1.0`` if absent.  The ``q`` key is consumed and **not** included in
        *params_dict*.  Raises ``ValueError`` on a malformed ``q`` value.
        """

        semi_idx = element.find(';')
        if semi_idx < 0:
            return element.strip().lower(), 1.0, {}

        token = element[:semi_idx].strip().lower()
        params = cls._parse_media_type_params(element[semi_idx:])

        q = 1.0
        q_str = params.pop('q', None)
        if q_str is not None:
            q = float(q_str)  # caller wraps ValueError

        return token, q, params

    def _prepare_te(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'te' not in headers:
            return

        codings = [
            self._split_header_element(p)[0]
            for p in self._parse_comma_list(headers['te'])
        ]

        prepared.te = [c for c in codings if c]

    def _prepare_upgrade(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'upgrade' not in headers:
            return

        prepared.upgrade = self._parse_comma_list(headers['upgrade'])

    # Headers that MUST NOT appear in trailers (RFC 7230 §4.1.2)
    _FORBIDDEN_TRAILER_FIELDS: ta.ClassVar[ta.FrozenSet[str]] = frozenset({
        'transfer-encoding',
        'content-length',
        'host',
        'cache-control',
        'expect',
        'max-forwards',
        'pragma',
        'range',
        'te',
        'authorization',
        'proxy-authenticate',
        'proxy-authorization',
        'www-authenticate',
        'content-encoding',
        'content-type',
        'content-range',
        'trailer',
    })

    def _prepare_trailer(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'trailer' not in headers:
            return

        fields = {f.lower() for f in self._parse_comma_list(headers['trailer'])}
        for f in fields:
            if f in self._FORBIDDEN_TRAILER_FIELDS:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.FORBIDDEN_TRAILER_FIELD,
                    message=f'Forbidden field in Trailer header: {f!r}',
                )

        prepared.trailer = frozenset(fields)

    def _prepare_expect(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'expect' not in headers:
            return

        raw = headers['expect'].strip().lower()
        if raw != '100-continue':
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_EXPECT,
                message=f'Only "100-continue" is accepted for Expect; got {raw!r}',
            )

        prepared.expect = raw
        prepared.expect_100_continue = True

    _MONTH_NAMES: ta.ClassVar[ta.Mapping[str, int]] = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12,
    }

    @classmethod
    def _parse_http_date(cls, value: str) -> datetime.datetime:
        """
        Parse an HTTP-date (RFC 7231 §7.1.1.1).

        Supports:
          - IMF-fixdate:  Sun, 06 Nov 1994 08:49:37 GMT
          - RFC 850:      Sunday, 06-Nov-94 08:49:37 GMT
          - asctime:      Sun Nov  6 08:49:37 1994
        """

        value = value.strip()

        # Try IMF-fixdate: day-name "," SP date1 SP time-of-day SP GMT
        # date1 = day SP month SP year (4-digit)
        if ',' in value:
            after_comma = value.split(',', 1)[1].strip()
            parts = after_comma.split()

            if len(parts) == 3 and parts[2].upper() == 'GMT' and '-' in parts[0]:
                # RFC 850: DD-Mon-YY HH:MM:SS GMT
                date_pieces = parts[0].split('-')
                if len(date_pieces) != 3:
                    raise ValueError(f'Invalid date component: {parts[0]}')

                day = int(date_pieces[0])
                month_str = date_pieces[1].lower()
                year_raw = int(date_pieces[2])

                # Two-digit year: RFC 7231 says interpret >= 50 as 19xx, < 50 as 20xx
                if year_raw < 100:
                    year = year_raw + 1900 if year_raw >= 50 else year_raw + 2000
                else:
                    year = year_raw

                time_pieces = parts[1].split(':')
                if len(time_pieces) != 3:
                    raise ValueError(f'Invalid time component: {parts[1]}')

                hour, minute, second = int(time_pieces[0]), int(time_pieces[1]), int(time_pieces[2])

                month = cls._MONTH_NAMES.get(month_str)
                if month is None:
                    raise ValueError(f'Invalid month: {month_str}')

                return datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)  # noqa

            elif len(parts) == 5 and parts[4].upper() == 'GMT':
                # IMF-fixdate: DD Mon YYYY HH:MM:SS GMT
                day = int(parts[0])
                month_str = parts[1].lower()
                year = int(parts[2])

                time_pieces = parts[3].split(':')
                if len(time_pieces) != 3:
                    raise ValueError(f'Invalid time component: {parts[3]}')

                hour, minute, second = int(time_pieces[0]), int(time_pieces[1]), int(time_pieces[2])

                month = cls._MONTH_NAMES.get(month_str)
                if month is None:
                    raise ValueError(f'Invalid month: {month_str}')

                return datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)  # noqa

            raise ValueError(f'Cannot parse date: {value}')

        else:
            # asctime: Sun Nov  6 08:49:37 1994 (Strict fixed-width check)
            # 012345678901234567890123
            # Sun Nov  6 08:49:37 1994
            if len(value) != 24:
                raise ValueError(f'Invalid asctime length: {len(value)}')

            month_str = value[4:7].lower()
            # Handle the space-padded day (e.g., " 6")
            day_str = value[8:10].replace(' ', '0')
            day = int(day_str)

            time_pieces = value[11:19].split(':')
            if len(time_pieces) != 3:
                raise ValueError('Invalid time component')
            hour, minute, second = map(int, time_pieces)

            year = int(value[20:24])
            month = cls._MONTH_NAMES.get(month_str)
            if month is None:
                raise ValueError(f'Invalid month: {month_str}')

            return datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)  # noqa

    def _prepare_date(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'date' not in headers:
            return

        raw = headers['date']
        try:
            prepared.date = self._parse_http_date(raw)
        except (ValueError, IndexError, OverflowError) as e:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_DATE,
                message=f'Cannot parse Date header: {e}',
            ) from None

    def _prepare_cache_control(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'cache-control' not in headers:
            return

        directives: ta.Dict[str, ta.Optional[str]] = {}

        for part in self._parse_comma_list(headers['cache-control']):
            eq_idx = part.find('=')
            if eq_idx < 0:
                directives[part.lower()] = None
                continue

            name = part[:eq_idx].strip().lower()
            value = part[eq_idx + 1:].strip()
            if value.startswith('"'):
                try:
                    value, _ = self._parse_quoted_string(value, 0)
                except ValueError:
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.INVALID_CACHE_CONTROL,
                        message=f'Invalid quoted-string in Cache-Control directive: {name}',
                    ) from None

            directives[name] = value

        prepared.cache_control = directives

    def _prepare_accept_encoding(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'accept-encoding' not in headers:
            return

        items: ta.List[PreparedParsedHttpHeaders.AcceptEncodingItem] = []

        for part in self._parse_comma_list(headers['accept-encoding']):
            try:
                coding, q, _ = self._split_header_element(part)
            except ValueError:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_ACCEPT_ENCODING,
                    message=f'Invalid q-value in Accept-Encoding: {part!r}',
                ) from None

            if coding:
                items.append(PreparedParsedHttpHeaders.AcceptEncodingItem(
                    coding=coding,
                    q=q,
                ))

        prepared.accept_encoding = items

    def _prepare_accept(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'accept' not in headers:
            return

        items: ta.List[PreparedParsedHttpHeaders.AcceptItem] = []

        for part in self._parse_comma_list(headers['accept']):
            try:
                media_range, q, params = self._split_header_element(part)
            except ValueError:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_ACCEPT,
                    message=f'Invalid q-value in Accept: {part!r}',
                ) from None

            items.append(PreparedParsedHttpHeaders.AcceptItem(
                media_range=media_range,
                q=q,
                params=params,
            ))

        prepared.accept = items

    def _prepare_authorization(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'authorization' not in headers:
            return

        raw = headers['authorization'].strip()
        if not raw:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_AUTHORIZATION,
                message='Authorization header is present but empty',
            )

        # scheme SP credentials (credentials may contain spaces for some schemes)
        sp_idx = raw.find(' ')
        if sp_idx < 0:
            # Scheme only, no credentials (e.g., some edge cases)
            prepared.authorization = PreparedParsedHttpHeaders.AuthorizationValue(
                scheme=raw,
                credentials='',
            )
        else:
            scheme = raw[:sp_idx]
            credentials = raw[sp_idx + 1:]
            prepared.authorization = PreparedParsedHttpHeaders.AuthorizationValue(
                scheme=scheme,
                credentials=credentials,
            )


##


def parse_http_message(
        data: bytes,
        mode: HttpParser.Mode = HttpParser.Mode.AUTO,
        config: ta.Optional[HttpParser.Config] = None,
) -> ParsedHttpMessage:
    """
    Parse an HTTP/1.x message head from *data*.

    This is a convenience wrapper around :class:`HttpHeadParser`.

    :param data: Complete message head ending with ``\\r\\n\\r\\n``.
    :param mode: ``REQUEST``, ``RESPONSE``, or ``AUTO`` (detect from start-line).
    :param config: Parsing strictness configuration.
    :returns: A :class:`ParsedHttpHead` with raw headers, normalized headers, and prepared values.
    :raises HttpParseError: On any parsing violation.
    """

    parser = HttpParser(**(dict(config=config) if config is not None else {}))
    return parser.parse_message(data, mode=mode)


def parse_http_trailers(
        data: bytes,
        config: ta.Optional[HttpParser.Config] = None,
) -> ParsedHttpTrailers:
    """
    Parse HTTP/1.x trailer fields from *data*.

    *data* must contain the complete trailer section ending with ``\\r\\n\\r\\n`` (an empty line). No start-line is
    expected.

    Fields listed in :data:`_FORBIDDEN_TRAILER_FIELDS` (per RFC 7230 §4.1.2) are rejected.

    :param data: Complete trailer section ending with ``\\r\\n\\r\\n``.
    :param config: Parsing strictness configuration (same knobs as header parsing).
    :returns: A :class:`ParsedTrailers` with raw and normalized headers.
    :raises HttpParseError: On any parsing violation.
    """

    parser = HttpParser(**(dict(config=config) if config is not None else {}))
    return parser.parse_trailers(data)
